#property strict

/*
 FIO MacroFX Bridge v1
 MidasFX MT4 DEMO bridge for the Railway Macro FX engine.

 SAFETY:
 - Demo accounts only by default
 - Trading disabled by default
 - Max 0.01 lot per pair
 - Max 2 bridge-owned positions
 - 10% local equity drawdown kill switch
 - Uses Magic Number 26092601
 - No martingale/grid/recovery sizing
*/

input string ApiBaseUrl = "https://mt5.freedomincomeoptions.com";
input string ApiKeyFile = "fio_macrofx.key";
input bool DemoOnly = true;
input bool EnableTrading = false;
input int MagicNumber = 26092601;
input double MaxLotPerPair = 0.01;
input int MaxPositions = 2;
input int PollSeconds = 60;
input int DailyBarsToUpload = 320;
input int BarsPerRequest = 50;
input int BarRetryMinutes = 15;
input int SlippagePoints = 30;
input double MaxDrawdownPct = 10.0;

string EA_VERSION = "MacroFX-MT4-Bridge-1.5";
string g_apiKey = "";
datetime g_lastBarAttempt = 0;
datetime g_lastBarUploadDay = 0;
bool g_killed = false;

string UrlEncode(string s)
{
   string out="";
   for(int i=0;i<StringLen(s);i++)
   {
      ushort c=StringGetCharacter(s,i);
      if((c>='a'&&c<='z')||(c>='A'&&c<='Z')||(c>='0'&&c<='9')||c=='-'||c=='_'||c=='.')
         out += ShortToString(c);
      else if(c==' ')
         out += "%20";
      else
         out += StringFormat("%%%02X",c);
   }
   return out;
}

bool IsDemoAccount()
{
   return IsDemo();
}

string AccountId()
{
   return IntegerToString(AccountNumber());
}

bool LoadApiKey()
{
   ResetLastError();

   int handle=FileOpen(ApiKeyFile,FILE_READ|FILE_TXT|FILE_ANSI);
   if(handle==INVALID_HANDLE)
   {
      Print("MacroFX key file not found: ",ApiKeyFile," err=",GetLastError());
      return false;
   }

   string key=FileReadString(handle);
   FileClose(handle);

   key=StringTrimLeft(key);
   key=StringTrimRight(key);

   if(StringLen(key)<16)
   {
      Print("MacroFX key file is empty or invalid.");
      return false;
   }

   g_apiKey=key;
   return true;
}

int HttpRequest(string method,string url,string body,string &response)
{
   char data[];
   char result[];
   string response_headers="";
   string headers="Content-Type: text/plain\r\nX-EA-API-Key: "+g_apiKey+"\r\n";

   int data_size=StringToCharArray(body,data,0,WHOLE_ARRAY,CP_UTF8);
   if(data_size>0) ArrayResize(data,data_size-1);

   ResetLastError();
   int code=WebRequest(method,url,headers,10000,data,result,response_headers);
   if(code==-1)
   {
      Print("MacroFX WebRequest error=",GetLastError()," url=",url);
      response="";
      return -1;
   }
   response=CharArrayToString(result,0,-1,CP_UTF8);
   return code;
}

void SendHeartbeat()
{
   string url=ApiBaseUrl+"/api/macrofx/heartbeat"
      +"?account_id="+UrlEncode(AccountId())
      +"&balance="+DoubleToString(AccountBalance(),2)
      +"&equity="+DoubleToString(AccountEquity(),2)
      +"&free_margin="+DoubleToString(AccountFreeMargin(),2)
      +"&is_demo="+(IsDemoAccount()?"true":"false")
      +"&ea_version="+UrlEncode(EA_VERSION)
      +"&broker="+UrlEncode("MidasFX");

   string resp="";
   int code=HttpRequest("POST",url,"",resp);
   if(code<200 || code>=300) Print("MacroFX heartbeat HTTP ",code," ",resp);
}

void SendPositions()
{
   string body="symbol,ticket,side,lots,open_price,current_price,pnl,swap,commission,magic\n";

   for(int i=OrdersTotal()-1;i>=0;i--)
   {
      if(!OrderSelect(i,SELECT_BY_POS,MODE_TRADES)) continue;
      if(OrderMagicNumber()!=MagicNumber) continue;

      int type=OrderType();
      if(type!=OP_BUY && type!=OP_SELL) continue;

      string side=(type==OP_BUY?"LONG":"SHORT");
      int digits=(int)MarketInfo(OrderSymbol(),MODE_DIGITS);
      double current=(type==OP_BUY?MarketInfo(OrderSymbol(),MODE_BID):MarketInfo(OrderSymbol(),MODE_ASK));

      body += OrderSymbol()+","+IntegerToString(OrderTicket())+","+side+","
         +DoubleToString(OrderLots(),2)+","+DoubleToString(OrderOpenPrice(),digits)+","
         +DoubleToString(current,digits)+","+DoubleToString(OrderProfit(),2)+","
         +DoubleToString(OrderSwap(),2)+","+DoubleToString(OrderCommission(),2)+","
         +IntegerToString(OrderMagicNumber())+"\n";
   }

   string url=ApiBaseUrl+"/api/macrofx/positions-csv?account_id="+UrlEncode(AccountId());
   string resp="";
   int code=HttpRequest("POST",url,body,resp);
   if(code<200 || code>=300) Print("MacroFX positions HTTP ",code," ",resp);
}

string NormalizeBrokerSymbol(string canonical)
{
   if(MarketInfo(canonical,MODE_POINT)>0) return canonical;

   for(int i=0;i<SymbolsTotal(false);i++)
   {
      string s=SymbolName(i,false);
      if(StringFind(s,canonical,0)>=0)
      {
         SymbolSelect(s,true);
         return s;
      }
   }
   return canonical;
}

string CanonicalSymbol(string brokerSymbol)
{
   string pairs[]={"EURUSD","GBPUSD","AUDUSD","NZDUSD","USDJPY","USDCAD","USDCHF",
                   "EURGBP","EURJPY","EURCHF","EURCAD","EURAUD","EURNZD",
                   "GBPJPY","GBPCHF","GBPCAD","GBPAUD","GBPNZD",
                   "AUDJPY","AUDCHF","AUDCAD","AUDNZD",
                   "NZDJPY","NZDCHF","NZDCAD","CADJPY","CADCHF","CHFJPY"};

   for(int i=0;i<ArraySize(pairs);i++)
      if(StringFind(brokerSymbol,pairs[i],0)>=0) return pairs[i];

   return brokerSymbol;
}

bool PostBarChunk(string canonical,string body)
{
   string url=ApiBaseUrl+"/api/macrofx/bars-csv?symbol="+canonical;
   string resp="";
   int code=HttpRequest("POST",url,body,resp);
   if(code<200 || code>=300)
   {
      Print("MacroFX bars ",canonical," HTTP ",code," ",resp);
      return false;
   }
   return true;
}

bool UploadBarsForSymbol(string canonical)
{
   string symbol=NormalizeBrokerSymbol(canonical);
   if(MarketInfo(symbol,MODE_POINT)<=0)
   {
      Print("MacroFX bars ",canonical,": broker symbol not found; skipping.");
      return true;
   }

   int total=iBars(symbol,PERIOD_D1);
   if(total<=2)
   {
      Print("MacroFX bars ",canonical,": daily history unavailable.");
      return false;
   }

   int count=(int)MathMin(DailyBarsToUpload,total-1);
   int chunkLimit=MathMax(10,BarsPerRequest);
   string body="date,close\n";
   int inChunk=0;
   bool ok=true;

   for(int shift=count;shift>=1;shift--)
   {
      datetime t=iTime(symbol,PERIOD_D1,shift);
      double closePrice=iClose(symbol,PERIOD_D1,shift);
      if(t<=0 || closePrice<=0) continue;

      int digits=(int)MarketInfo(symbol,MODE_DIGITS);
      string dateText=StringFormat("%04d-%02d-%02d",TimeYear(t),TimeMonth(t),TimeDay(t));
      body += dateText+","+DoubleToString(closePrice,digits)+"\n";
      inChunk++;

      if(inChunk>=chunkLimit)
      {
         if(!PostBarChunk(canonical,body)) ok=false;
         body="date,close\n";
         inChunk=0;
         Sleep(50);
      }
   }

   if(inChunk>0)
   {
      if(!PostBarChunk(canonical,body)) ok=false;
   }

   return ok;
}

void UploadDailyBarsIfNeeded()
{
   datetime today=StringToTime(TimeToString(TimeCurrent(),TIME_DATE));
   if(g_lastBarUploadDay==today) return;

   datetime now=TimeCurrent();
   if(g_lastBarAttempt>0 && (now-g_lastBarAttempt)<BarRetryMinutes*60) return;
   g_lastBarAttempt=now;

   string pairs[]={"EURUSD","GBPUSD","AUDUSD","NZDUSD","USDJPY","USDCAD","USDCHF",
                   "EURGBP","EURJPY","EURCHF","EURCAD","EURAUD","EURNZD",
                   "GBPJPY","GBPCHF","GBPCAD","GBPAUD","GBPNZD",
                   "AUDJPY","AUDCHF","AUDCAD","AUDNZD",
                   "NZDJPY","NZDCHF","NZDCAD","CADJPY","CADCHF","CHFJPY"};

   bool allOk=true;
   for(int i=0;i<ArraySize(pairs);i++)
   {
      if(!UploadBarsForSymbol(pairs[i])) allOk=false;
   }

   if(allOk)
   {
      g_lastBarUploadDay=today;
      Print("MacroFX daily bars upload complete.");
   }
   else
   {
      Print("MacroFX daily bars upload incomplete; retrying later.");
   }
}

double TargetLotsFor(string canonical,string targetsText)
{
   string lines[];
   int n=StringSplit(targetsText,'\n',lines);

   for(int i=0;i<n;i++)
   {
      if(StringFind(lines[i],"TARGET,",0)!=0) continue;

      string parts[];
      int m=StringSplit(lines[i],',',parts);

      if(m>=4 && parts[1]==canonical)
         return StringToDouble(parts[2]);
   }
   return 0.0;
}

double TargetScoreFor(string canonical,string targetsText)
{
   string lines[];
   int n=StringSplit(targetsText,'\n',lines);

   for(int i=0;i<n;i++)
   {
      if(StringFind(lines[i],"TARGET,",0)!=0) continue;

      string parts[];
      int m=StringSplit(lines[i],',',parts);

      if(m>=4 && parts[1]==canonical)
         return StringToDouble(parts[3]);
   }
   return 0.0;
}

int BridgeOpenPositions()
{
   int n=0;

   for(int i=OrdersTotal()-1;i>=0;i--)
   {
      if(!OrderSelect(i,SELECT_BY_POS,MODE_TRADES)) continue;
      if(OrderMagicNumber()!=MagicNumber) continue;
      if(OrderType()==OP_BUY || OrderType()==OP_SELL) n++;
   }
   return n;
}

void SendFill(
   string canonical,
   string action,
   double lots,
   int ticket,
   double requested,
   double filled,
   double spreadPoints,
   double slippagePoints,
   double pnl,
   double swap,
   double commission,
   double signalScore,
   string exitReason,
   string notes
)
{
   string url=ApiBaseUrl+"/api/macrofx/fill"
      +"?account_id="+UrlEncode(AccountId())
      +"&symbol="+canonical
      +"&action="+UrlEncode(action)
      +"&lots="+DoubleToString(lots,2)
      +"&ticket="+IntegerToString(ticket)
      +"&requested_price="+DoubleToString(requested,8)
      +"&fill_price="+DoubleToString(filled,8)
      +"&spread_points="+DoubleToString(spreadPoints,3)
      +"&slippage_points="+DoubleToString(slippagePoints,3)
      +"&pnl="+DoubleToString(pnl,2)
      +"&swap="+DoubleToString(swap,2)
      +"&commission="+DoubleToString(commission,2)
      +"&signal_score="+DoubleToString(signalScore,8)
      +"&exit_reason="+UrlEncode(exitReason)
      +"&strategy_version=macrofx-v1.1"
      +"&notes="+UrlEncode(notes);

   string resp="";
   int code=HttpRequest("POST",url,"",resp);
   if(code<200 || code>=300) Print("MacroFX fill HTTP ",code," ",resp);
}

bool CloseTicket(int ticket,string canonical,string reason,double signalScore)
{
   if(!OrderSelect(ticket,SELECT_BY_TICKET)) return false;

   string sym=OrderSymbol();
   int type=OrderType();
   double lots=OrderLots();
   double pnl=OrderProfit();
   double swap=OrderSwap();
   double commission=OrderCommission();

   double bid=MarketInfo(sym,MODE_BID);
   double ask=MarketInfo(sym,MODE_ASK);
   double point=MarketInfo(sym,MODE_POINT);
   double requested=(type==OP_BUY?bid:ask);
   double spreadPoints=(point>0?(ask-bid)/point:0.0);

   bool ok=OrderClose(ticket,lots,requested,SlippagePoints,clrNONE);
   if(!ok)
   {
      Print("MacroFX close failed ticket=",ticket," err=",GetLastError());
      return false;
   }

   double filled=requested;
   if(OrderSelect(ticket,SELECT_BY_TICKET,MODE_HISTORY))
   {
      filled=OrderClosePrice();
      pnl=OrderProfit();
      swap=OrderSwap();
      commission=OrderCommission();
   }

   double slippagePoints=(point>0?MathAbs(filled-requested)/point:0.0);

   SendFill(
      canonical,
      "CLOSE",
      lots,
      ticket,
      requested,
      filled,
      spreadPoints,
      slippagePoints,
      pnl,
      swap,
      commission,
      signalScore,
      reason,
      reason
   );

   return true;
}

string HwmKey()
{
   return "FIO_MACROFX_HWM_"+AccountId();
}

bool DrawdownKillTriggered()
{
   string key=HwmKey();
   double eq=AccountEquity();
   if(eq<=0) return false;

   double hwm=eq;

   if(GlobalVariableCheck(key))
      hwm=GlobalVariableGet(key);
   else
      GlobalVariableSet(key,hwm);

   if(eq>hwm)
   {
      hwm=eq;
      GlobalVariableSet(key,hwm);
   }

   double dd=(hwm-eq)/hwm*100.0;

   if(dd < MaxDrawdownPct) return false;

   if(!g_killed)
      Print("MacroFX KILL SWITCH: drawdown=",DoubleToString(dd,2),
            "% HWM=",DoubleToString(hwm,2),
            " equity=",DoubleToString(eq,2));

   g_killed=true;

   for(int i=OrdersTotal()-1;i>=0;i--)
   {
      if(!OrderSelect(i,SELECT_BY_POS,MODE_TRADES)) continue;
      if(OrderMagicNumber()!=MagicNumber) continue;
      if(OrderType()!=OP_BUY && OrderType()!=OP_SELL) continue;
      string canonical=CanonicalSymbol(OrderSymbol());
      CloseTicket(OrderTicket(),canonical,"drawdown_kill",0.0);
   }

   return true;
}

void ReconcileTargets(string targetsText)
{
   if(!EnableTrading) return;
   if(g_killed || DrawdownKillTriggered()) return;

   if(DemoOnly && !IsDemoAccount())
   {
      Print("MacroFX BLOCKED: bridge is demo-only.");
      return;
   }

   // Flatten bridge-owned positions that are no longer targets or have reversed.
   for(int i=OrdersTotal()-1;i>=0;i--)
   {
      if(!OrderSelect(i,SELECT_BY_POS,MODE_TRADES)) continue;
      if(OrderMagicNumber()!=MagicNumber) continue;
      if(OrderType()!=OP_BUY && OrderType()!=OP_SELL) continue;

      string canonical=CanonicalSymbol(OrderSymbol());
      double target=TargetLotsFor(canonical,targetsText);
      double actual=(OrderType()==OP_BUY?OrderLots():-OrderLots());

      if(target==0.0 || (target>0 && actual<0) || (target<0 && actual>0))
      {
         int ticket=OrderTicket();
         double signalScore=TargetScoreFor(canonical,targetsText);
         string reason=(target==0.0?"target_removed":"signal_reversed");
         CloseTicket(ticket,canonical,reason,signalScore);
      }
   }

   // Open missing targets. v1 deliberately uses 0.01-lot targets only.
   string lines[];
   int n=StringSplit(targetsText,'\n',lines);

   for(int k=0;k<n;k++)
   {
      if(StringFind(lines[k],"TARGET,",0)!=0) continue;

      string p[];
      int m=StringSplit(lines[k],',',p);
      if(m<4) continue;

      string canonical=p[1];
      double target=StringToDouble(p[2]);

      if(MathAbs(target)<0.0001) continue;

      target=(target>0
         ? MathMin(target,MaxLotPerPair)
         : -MathMin(MathAbs(target),MaxLotPerPair));

      bool already=false;

      for(int j=OrdersTotal()-1;j>=0;j--)
      {
         if(!OrderSelect(j,SELECT_BY_POS,MODE_TRADES)) continue;
         if(OrderMagicNumber()!=MagicNumber) continue;
         if(CanonicalSymbol(OrderSymbol())!=canonical) continue;

         double actual=(OrderType()==OP_BUY?OrderLots():-OrderLots());

         if((target>0 && actual>0) || (target<0 && actual<0))
            already=true;
      }

      if(already) continue;
      if(BridgeOpenPositions()>=MaxPositions) break;

      string sym=NormalizeBrokerSymbol(canonical);
      int cmd=(target>0?OP_BUY:OP_SELL);
      double lots=MathAbs(target);

      double minLot=MarketInfo(sym,MODE_MINLOT);
      double lotStep=MarketInfo(sym,MODE_LOTSTEP);

      if(minLot>0 && lots<minLot)
      {
         Print("MacroFX skip ",canonical,": target lots below broker minimum.");
         continue;
      }

      if(lotStep>0)
         lots=MathFloor(lots/lotStep+0.0000001)*lotStep;

      double ask=MarketInfo(sym,MODE_ASK);
      double bid=MarketInfo(sym,MODE_BID);
      double point=MarketInfo(sym,MODE_POINT);
      double req=(cmd==OP_BUY?ask:bid);
      double spreadPoints=(point>0?(ask-bid)/point:0.0);
      double signalScore=StringToDouble(p[3]);

      ResetLastError();

      int ticket=OrderSend(
         sym,
         cmd,
         lots,
         req,
         SlippagePoints,
         0,
         0,
         "FIO MacroFX",
         MagicNumber,
         0,
         clrNONE
      );

      if(ticket<0)
      {
         Print("MacroFX OrderSend failed ",canonical," err=",GetLastError());
         continue;
      }

      if(OrderSelect(ticket,SELECT_BY_TICKET))
      {
         double filled=OrderOpenPrice();
         double slippagePoints=(point>0?MathAbs(filled-req)/point:0.0);

         SendFill(
            canonical,
            (cmd==OP_BUY?"OPEN_LONG":"OPEN_SHORT"),
            lots,
            ticket,
            req,
            filled,
            spreadPoints,
            slippagePoints,
            0.0,
            0.0,
            OrderCommission(),
            signalScore,
            "",
            "target_open"
         );
      }
   }
}

void PollTargets()
{
   string url=ApiBaseUrl+"/api/macrofx/targets-text?account_id="+UrlEncode(AccountId());
   string resp="";
   int code=HttpRequest("GET",url,"",resp);

   if(code==409)
   {
      Print("MacroFX target poll blocked: ",resp);
      return;
   }

   if(code<200 || code>=300)
   {
      Print("MacroFX targets HTTP ",code," ",resp);
      return;
   }

   ReconcileTargets(resp);
}

int OnInit()
{
   if(!LoadApiKey())
   {
      Alert("MacroFX API key file missing or invalid. Put fio_macrofx.key in MQL4\\Files.");
      return(INIT_FAILED);
   }

   if(DemoOnly && !IsDemoAccount())
   {
      Alert("FIO MacroFX Bridge is DEMO ONLY. Attach it to a demo account.");
      return(INIT_FAILED);
   }

   EventSetTimer(MathMax(10,PollSeconds));

   Print(
      "FIO MacroFX Bridge ",
      EA_VERSION,
      " initialized. Trading=",
      EnableTrading?"ON":"OFF"
   );

   SendHeartbeat();
   SendPositions();
   UploadDailyBarsIfNeeded();

   return(INIT_SUCCEEDED);
}

void OnDeinit(const int reason)
{
   EventKillTimer();
}

void OnTimer()
{
   DrawdownKillTriggered();
   SendHeartbeat();
   SendPositions();
   UploadDailyBarsIfNeeded();
   PollTargets();
}

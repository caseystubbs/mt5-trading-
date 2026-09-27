#property strict

/*
 FIO MacroFX Bridge v1
 MidasFX MT4 DEMO bridge for the Railway Macro FX engine.

 SAFETY:
 - Demo accounts only by default
 - Trading disabled by default
 - Max 0.01 lot per pair
 - Max 2 bridge-owned positions
 - Uses Magic Number 26092601
 - No martingale/grid/recovery sizing
*/

input string ApiBaseUrl = "https://mt5.freedomincomeoptions.com";
input string ApiKey = "";
input bool DemoOnly = true;
input bool EnableTrading = false;
input int MagicNumber = 26092601;
input double MaxLotPerPair = 0.01;
input int MaxPositions = 2;
input int PollSeconds = 60;
input int DailyBarsToUpload = 320;
input int SlippagePoints = 30;

string EA_VERSION = "MacroFX-MT4-Bridge-1.0";
datetime g_lastBarUploadDay = 0;\nbool g_killed = false;

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
   return AccountDemo();
}

string AccountId()
{
   return IntegerToString(AccountNumber());
}

int HttpRequest(string method,string url,string body,string &response)
{
   char data[];
   char result[];
   string response_headers="";
   string headers="Content-Type: text/plain\r\n";
   StringToCharArray(body,data,0,WHOLE_ARRAY,CP_UTF8);
   ResetLastError();
   int code=WebRequest(method,url,headers,5000,data,result,response_headers);
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
   string url=ApiBaseUrl+"/api/macrofx/heartbeat?api_key="+UrlEncode(ApiKey)
      +"&account_id="+UrlEncode(AccountId())
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
   string url=ApiBaseUrl+"/api/macrofx/positions-csv?api_key="+UrlEncode(ApiKey)+"&account_id="+UrlEncode(AccountId());
   string resp="";
   int code=HttpRequest("POST",url,body,resp);
   if(code<200 || code>=300) Print("MacroFX positions HTTP ",code," ",resp);
}

string NormalizeBrokerSymbol(string canonical)
{
   if(MarketInfo(canonical,MODE_POINT)>0) return canonical;
   for(int i=0;i<SymbolsTotal(true);i++)
   {
      string s=SymbolName(i,true);
      if(StringFind(s,canonical,0)>=0) return s;
   }
   return canonical;
}

string CanonicalSymbol(string brokerSymbol)
{
   string pairs[]={"EURUSD","GBPUSD","AUDUSD","NZDUSD","USDJPY","USDCAD","USDCHF",
                   "EURGBP","EURJPY","GBPJPY","AUDJPY","CADJPY","EURAUD","GBPAUD"};
   for(int i=0;i<ArraySize(pairs);i++)
      if(StringFind(brokerSymbol,pairs[i],0)>=0) return pairs[i];
   return brokerSymbol;
}

void UploadBarsForSymbol(string canonical)
{
   string symbol=NormalizeBrokerSymbol(canonical);
   if(MarketInfo(symbol,MODE_POINT)<=0) return;
   string body="date,close\n";
   int count=MathMin(DailyBarsToUpload,iBars(symbol,PERIOD_D1)-1);
   for(int shift=count;shift>=1;shift--)
   {
      datetime t=iTime(symbol,PERIOD_D1,shift);
      double c=iClose(symbol,PERIOD_D1,shift);
      if(t<=0 || c<=0) continue;
      int digits=(int)MarketInfo(symbol,MODE_DIGITS);
      body += TimeToString(t,TIME_DATE)+","+DoubleToString(c,digits)+"\n";
   }
   string url=ApiBaseUrl+"/api/macrofx/bars-csv?api_key="+UrlEncode(ApiKey)+"&symbol="+canonical;
   string resp="";
   int code=HttpRequest("POST",url,body,resp);
   if(code<200 || code>=300) Print("MacroFX bars ",canonical," HTTP ",code," ",resp);
}

void UploadDailyBarsIfNeeded()
{
   datetime today=StringToTime(TimeToString(TimeCurrent(),TIME_DATE));
   if(g_lastBarUploadDay==today) return;

   string pairs[]={"EURUSD","GBPUSD","AUDUSD","NZDUSD","USDJPY","USDCAD","USDCHF",
                   "EURGBP","EURJPY","GBPJPY","AUDJPY","CADJPY","EURAUD","GBPAUD"};
   for(int i=0;i<ArraySize(pairs);i++) UploadBarsForSymbol(pairs[i]);
   g_lastBarUploadDay=today;
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

int BridgeOpenPositions()
{
   int n=0;
   for(int i=OrdersTotal()-1;i>=0;i--)
      if(OrderSelect(i,SELECT_BY_POS,MODE_TRADES) && OrderMagicNumber()==MagicNumber &&
         (OrderType()==OP_BUY || OrderType()==OP_SELL)) n++;
   return n;
}

bool CloseTicket(int ticket)
{
   if(!OrderSelect(ticket,SELECT_BY_TICKET)) return false;
   string sym=OrderSymbol();
   int type=OrderType();
   double lots=OrderLots();
   double price=(type==OP_BUY?MarketInfo(sym,MODE_BID):MarketInfo(sym,MODE_ASK));
   bool ok=OrderClose(ticket,lots,price,SlippagePoints,clrNONE);
   if(!ok) Print("MacroFX close failed ticket=",ticket," err=",GetLastError());
   return ok;
}

void SendFill(string canonical,string action,double lots,int ticket,double requested,double filled,string notes)
{
   string url=ApiBaseUrl+"/api/macrofx/fill?api_key="+UrlEncode(ApiKey)
      +"&account_id="+UrlEncode(AccountId())
      +"&symbol="+canonical
      +"&action="+UrlEncode(action)
      +"&lots="+DoubleToString(lots,2)
      +"&ticket="+IntegerToString(ticket)
      +"&requested_price="+DoubleToString(requested,8)
      +"&fill_price="+DoubleToString(filled,8)
      +"&strategy_version=macrofx-v1"
      +"&notes="+UrlEncode(notes);
   string resp="";
   HttpRequest("POST",url,"",resp);
}

void ReconcileTargets(string targetsText)
{
   if(!EnableTrading) return;
   if(DemoOnly && !IsDemoAccount())
   {
      Print("MacroFX BLOCKED: bridge is demo-only.");
      return;
   }

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
         double lots=OrderLots();
         double req=(OrderType()==OP_BUY?MarketInfo(OrderSymbol(),MODE_BID):MarketInfo(OrderSymbol(),MODE_ASK));
         if(CloseTicket(ticket))
            SendFill(canonical,"CLOSE",lots,ticket,req,req,"reconciliation");
      }
   }

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

      target=(target>0?MathMin(target,MaxLotPerPair):-MathMin(MathAbs(target),MaxLotPerPair));

      bool already=false;
      for(int j=OrdersTotal()-1;j>=0;j--)
      {
         if(!OrderSelect(j,SELECT_BY_POS,MODE_TRADES)) continue;
         if(OrderMagicNumber()!=MagicNumber) continue;
         if(CanonicalSymbol(OrderSymbol())!=canonical) continue;
         double actual=(OrderType()==OP_BUY?OrderLots():-OrderLots());
         if((target>0 && actual>0) || (target<0 && actual<0)) already=true;
      }

      if(already) continue;
      if(BridgeOpenPositions()>=MaxPositions) break;

      string sym=NormalizeBrokerSymbol(canonical);
      int cmd=(target>0?OP_BUY:OP_SELL);
      double lots=MathAbs(target);
      double req=(cmd==OP_BUY?MarketInfo(sym,MODE_ASK):MarketInfo(sym,MODE_BID));

      ResetLastError();
      int ticket=OrderSend(sym,cmd,lots,req,SlippagePoints,0,0,"FIO MacroFX",MagicNumber,0,clrNONE);
      if(ticket<0)
      {
         Print("MacroFX OrderSend failed ",canonical," err=",GetLastError());
         continue;
      }

      if(OrderSelect(ticket,SELECT_BY_TICKET))
         SendFill(canonical,(cmd==OP_BUY?"OPEN_LONG":"OPEN_SHORT"),lots,ticket,req,OrderOpenPrice(),"target_reconciliation");
   }
}

void PollTargets()
{
   string url=ApiBaseUrl+"/api/macrofx/targets-text?api_key="+UrlEncode(ApiKey)+"&account_id="+UrlEncode(AccountId());
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
   if(DemoOnly && !IsDemoAccount())
   {
      Alert("FIO MacroFX Bridge is DEMO ONLY. Attach to a demo account.");
      return(INIT_FAILED);
   }

   EventSetTimer(MathMax(10,PollSeconds));
   Print("FIO MacroFX Bridge ",EA_VERSION," initialized. Trading=",EnableTrading?"ON":"OFF");
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
   SendHeartbeat();
   SendPositions();
   UploadDailyBarsIfNeeded();
   PollTargets();
}

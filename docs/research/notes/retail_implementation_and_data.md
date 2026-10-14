# Running a weekly G8 FX system (carry, value, trend) on a ~$1,000 MetaTrader 4 (MT4) account: retail costs, free data and position sizing

Research date: 2026-10-14. Account context: MidasFX MT4 demo, ~$1,000, 0.01-lot minimum, 28 G8 crosses, weekly rebalance. The backtest uses Fed H.10 rates through the GitHub `datasets/exchange-rates` repo (loaded in `scripts/backtest_macrofx.py`).

"Computed" findings come from the H.10 daily file at https://raw.githubusercontent.com/datasets/exchange-rates/main/data/daily.csv (last row 2026-10-09). The calculations were run in this session; the code is in the research transcript and is not committed.

---

## 1. Retail swap/rollover: how brokers set it, the markup, triple Wednesday, and how much carry a retail trader keeps

### Takeaway
Retail brokers pass through the interbank tom-next swap and add an admin fee of about 0.5–1.0% a year to both the long and the short rate. The fee costs you whichever way you hold the pair. On today's G8 rates you keep about 55–85% of a 2–4.5% differential and only about 35–65% of a 1.5% differential. On a $1,000 account carrying ~8x gross notional, the fee alone costs about 4–8% of equity a year.

### Cited Findings
- **OANDA (US).** Funding rates are "a blend of underlying liquidity providers' tom-next swap rates," adjusted by an admin fee. Each instrument has separate long and short rates, quoted annually and changing daily. — [OANDA financing fees](https://www.oanda.com/us-en/trading/financing-fees/)
- **OANDA formula:** financing = position value × applicable funding rate × 1/365. Position value is units × price at 5 p.m. ET. A negative rate is a debit and a positive rate is a credit. — [OANDA](https://www.oanda.com/us-en/trading/financing-fees/)
- **OANDA admin fee schedule (annualised):** 1.00% for "other pairs" (all G8 pairs fall here), 2.00% for CZK/HUF/SAR/THB/ZAR pairs, 4.00% for TRY pairs. — [OANDA](https://www.oanda.com/us-en/trading/financing-fees/)
- **OANDA worked example:** long 100,000 EUR/USD at 1.15826 with a −3.00% long rate gives (100,000 × 1.15826) × −3.00% × 1/365 = −9.52 USD per day. Indicative rates can differ from final rates, which are published shortly after the 5 p.m. ET close. — [OANDA](https://www.oanda.com/us-en/trading/financing-fees/)
- **OANDA triple day:** positions held over Wednesday 5 p.m. are charged for the weekend, "typically three times" a normal day. There is no financing on Saturday or Sunday, and holidays can make one charge cover several days. — [OANDA](https://www.oanda.com/us-en/trading/financing-fees/)
- **IG.** Forex funding is the tom-next rate plus an admin fee of 0.8% for mini contracts or 0.5% for standard contracts. Fee value = "Price in points × 0.8% (mini) / 0.5% (standard) ÷ 360", which is an annual rate on notional. Shorts receive tom-next minus the fee; longs pay tom-next plus the fee. — [IG help: overnight funding](https://www.ig.com/sg/help-and-support/cfds/fees-and-charges/why-is-overnight-funding-charged-and-how-is-it-calculated)
- **IG triple day:** holding through Wednesday 10 p.m. UK time incurs three days of tom-next and one day of admin fee. Holding through Friday 10 p.m. incurs three days of admin fee and one day of tom-next. — [IG](https://www.ig.com/sg/help-and-support/cfds/fees-and-charges/why-is-overnight-funding-charged-and-how-is-it-calculated)
- **IG worked example:** short one EUR/USD standard contract at 1.0650 with tom-next 0.34 bid / 0.39 offer. Fee value = 10650 × 0.5% ÷ 360 = 0.15, so the swap is 0.34 − 0.15 = 0.19, a $1.90 credit. About 44% of the bid-side tom-next is lost to the fee in this example. — [IG](https://www.ig.com/sg/help-and-support/cfds/fees-and-charges/why-is-overnight-funding-charged-and-how-is-it-calculated)
- **FXCM:** positions open at "5 PM EST sharp" are held overnight and the credit or debit posts within about an hour. Three days are booked on Wednesday, and "most liquidity providers still apply interest for those two days." The page gives no formula and does not disclose a markup. — [FXCM help: when is rollover booked](https://www.fxcm.com/au/help/rollover-when-is-rollover-booked/)
- **CME:** in OTC spot, the value date rolls and overnight financing is applied in the 5:00–6:00 p.m. New York window. — [CME Group, "When FX futures pause" (2026)](https://www.cmegroup.com/articles/2026/when-fx-futures-pause.html)
- **Latest OECD 3-month interbank rates on FRED, used for the carry-kept calculations below:** US 3.82 (Aug 2026), AU 4.51 (Aug 2026), JP 1.45845 (Jul 2026), CH −0.045 (Aug 2026), CA 2.28 (Aug 2026), NZ 2.98 (Aug 2026). — [FRED IR3TIB01USM156N](https://fred.stlouisfed.org/series/IR3TIB01USM156N), [AUM156N](https://fred.stlouisfed.org/series/IR3TIB01AUM156N), [JPM156N](https://fred.stlouisfed.org/series/IR3TIB01JPM156N), [CHM156N](https://fred.stlouisfed.org/series/IR3TIB01CHM156N), [CAM156N](https://fred.stlouisfed.org/series/IR3TIB01CAM156N), [NZM156N](https://fred.stlouisfed.org/series/IR3TIB01NZM156N)
- **Computed carry kept after a fee of 0.5% / 0.8% / 1.0%,** using the FRED rates above:

  | Long pair | Gross differential | Net at 0.5% / 0.8% / 1.0% fee | Share kept |
  |---|---|---|---|
  | AUDCHF | 4.55% | 4.05 / 3.75 / 3.55% | 89 / 82 / 78% |
  | USDCHF | 3.86% | 3.36 / 3.06 / 2.86% | 87 / 79 / 74% |
  | AUDJPY | 3.05% | 2.55 / 2.25 / 2.05% | 84 / 74 / 67% |
  | USDJPY | 2.36% | 1.86 / 1.56 / 1.36% | 79 / 66 / 58% |
  | AUDCAD | 2.23% | 1.73 / 1.43 / 1.23% | 78 / 64 / 55% |
  | NZDJPY | 1.52% | 1.02 / 0.72 / 0.52% | 67 / 47 / 34% |

  — computed from the FRED values above and the [OANDA](https://www.oanda.com/us-en/trading/financing-fees/) and [IG](https://www.ig.com/sg/help-and-support/cfds/fees-and-charges/why-is-overnight-funding-charged-and-how-is-it-calculated) fee levels.

### Inferences
- **The fee is direction-agnostic.** It lowers the credit on the long-carry side and raises the debit on the short side, so it is a fixed annual drag on gross notional for every position (carry, value or trend). With 8 micro positions averaging about $1,000 notional ($8,000 gross on $1,000 equity), a 0.5–1.0% fee costs about $40–80 a year, or 4–8% of equity, before any differential.
- **Pairs with less than about 1% differential become negative-swap in both directions after the fee.** A carry backtest should model net swap as (r_base − r_quote − fee) for longs and (r_quote − r_base − fee) for shorts, not the raw differential.
- **3-month interbank rates differ from tom-next.** Retail swap follows overnight tom-next, while the 3-month rate embeds expected policy moves. Around policy turns, the 3-month differential will lead the realised swap. Policy rates (BIS CBPOL) are a closer proxy for the swap actually paid; 3-month rates are a reasonable signal input.
- **Triple Wednesday does not affect a weekly-held book.** A position held Monday to Friday collects 7 days of carry either way. It only matters for positions opened or closed mid-week, which the backtest should date correctly.
- **The actual MidasFX markup has to be measured.** No public MidasFX swap methodology was found. The practical step is to have the EA log `MarketInfo(sym, MODE_SWAPLONG)`, `MODE_SWAPSHORT` and `MODE_SWAPTYPE` (points or percent) for all 28 symbols every day to the backend. The implied fee is (swap_long + swap_short) / 2 against the differential. Demo swaps may not match live swaps, so verify again on live.

### Gaps
- No MidasFX swap or contract-specification page was found; the search returned only unrelated broker pages.
- Interactive Brokers' financing methodology was not retrieved this session.
- The OANDA UK and global-entity fee levels were not separately checked; the 1.00% figure is from the US page.
- No independent study measuring retail swap against interbank tom-next across many brokers was found.

---

## 2. Typical retail spreads by pair and time (Sunday reopen, 5 p.m. ET rollover) and slippage

### Takeaway
The internal Sunday-open spreads (13–36.5 pips) are 15–60× the weekday fills (0.6–0.9 pips). A weekly rebalance executed at the Sunday open would cost 50–150% of a $1,000 account a year, versus about 4% on weekdays. The 5–6 p.m. New York rollover hour is the documented low-liquidity window. No authoritative measured study of Sunday-open retail spreads was found.

### Cited Findings
- **Internal observation (task brief, MacroFX demo fills):** 6–9 points (0.6–0.9 pip) on weekday fills and 130–365 points (13–36.5 pips) at the Sunday reopen.
- **CME:** the 5–6 p.m. New York rollover is "the least liquid hour of the FX day." Bank desks cut risk into the book close and "many liquidity providers scale back or step away entirely." A spread "of a fraction of a pip during liquid hours can expand to several pips through the rollover." Its illustrative (not measured) EUR/USD case shows a widening from 0.5 to 18 pips, with a stop at 1.0830 hit by a 1.0829 bid while the mid stayed at 1.0838. — [CME Group, "When FX futures pause" (2026)](https://www.cmegroup.com/articles/2026/when-fx-futures-pause.html)
- **The repo backtest already uses** `COSTS_PIPS = {"none": 0.0, "weekday": 1.0, "sunday": 20.0}`. — `/home/claude/mt5-trading-/scripts/backtest_macrofx.py` line 43
- **Computed cost per 0.01 lot of a USD-quoted pair** (pip value $0.10):

  | Fill | Full spread | Cost per micro lot | % of notional |
  |---|---|---|---|
  | Weekday, 6–9 points | 0.6–0.9 pips | $0.06–0.09 | about 0.01% |
  | Sunday, 130 points | 13 pips | $1.30 | 0.12% |
  | Sunday, 365 points | 36.5 pips | $3.65 | 0.33% |

  Notional is $1,119 for EURUSD at 1.1193 on 2026-10-09. — computed from [H.10 daily.csv](https://raw.githubusercontent.com/datasets/exchange-rates/main/data/daily.csv)
- **Computed annual cost** of 8 micro positions with one full spread paid per position per week (100% weekly turnover) over 52 weeks:
  - 9-point weekday fills: about $37 a year, 4% of $1,000.
  - 130-point Sunday fills: about $541, 54%.
  - 365-point Sunday fills: about $1,518, 152%.

  — computed

### Inferences
- **Never rebalance at the Sunday reopen.** Schedule the weekly rebalance for Monday after the London open (about 03:00–11:00 ET, when London and later New York overlap). Block orders from about 16:45 to 18:30 ET every day and for the first 1–2 hours after the Sunday open.
- **Add a spread gate in the EA:** skip or defer an order if the live spread exceeds about 2–3× that symbol's trailing median weekday spread, and log the skipped orders.
- **The backtest's 20-pip Sunday cost sits inside the observed 13–36.5 pip range,** but the weekday 1-pip cost understates crosses. EURUSD-like fills are not representative of NZDCHF, GBPNZD or NZDCAD. Measure per-symbol median spreads from the EA's own fill log and feed them into the backtest as a per-pair cost table.
- **Use hysteresis and partial rebalances.** The backtest's `select(..., buffer=...)` hysteresis and trading only the changed positions cut turnover well below the 100%-turnover worst case above.
- **Slippage on market orders at 0.01 lot should be small in liquid hours;** the spread dominates. No measured slippage source was found.

### Gaps
- No primary or academic source with measured retail spreads at the Sunday open was found. Results were forums and blogs (for example babypips threads), which were not used.
- No published per-pair retail spread table covering all 28 G8 crosses was retrieved. MidasFX's spread page was not found.
- No BIS microstructure paper on intraday or weekly-open FX liquidity was retrieved this session.

---

## 3. Free historical short-term interest-rate data for the 8 currencies (carry signal from ~2000)

### Takeaway
The FRED OECD series `IR3TIB01xxM156N` cover all 8 currencies monthly, and 6 of 8 are current to Jul or Aug 2026. Three problems need fixing:
- The **euro area and UK** series stopped at Jan 2026 (last updated 2026-02-16).
- **Japan** only starts in Apr 2002.
- **Switzerland** is negative.

The BIS policy-rate dataset (CBPOL, daily) is the best complement. From this sandbox, FRED, BIS, OECD, ECB, the Fed and DBnomics are all proxy-blocked; only raw.githubusercontent.com works. The only G8 short-rate mirror found on GitHub is `datasets/euribor` (3-month, monthly, through Sep 2026).

### Cited Findings
- **FRED `IR3TIB01` series.** Title pattern: "Interest Rates: 3-Month or 90-Day Rates and Yields: Interbank Rates: Total for …". All are monthly, percent per annum, not seasonally adjusted, from OECD Main Economic Indicators. No page carries a discontinuation notice; each says "Next Release Date: Not Available".

  | ID | Currency | First obs | Last obs | Latest value | Last updated |
  |---|---|---|---|---|---|
  | [IR3TIB01USM156N](https://fred.stlouisfed.org/series/IR3TIB01USM156N) | USD | 1964-06 | 2026-08 | 3.82 | 2026-09-15 |
  | [IR3TIB01EZM156N](https://fred.stlouisfed.org/series/IR3TIB01EZM156N) | EUR, "Euro Area (19 Countries)" | 1994-01 | **2026-01** | 2.02773 | **2026-02-16** |
  | [IR3TIB01GBM156N](https://fred.stlouisfed.org/series/IR3TIB01GBM156N) | GBP | 1957-01 | **2026-01** | 3.71 | **2026-02-16** |
  | [IR3TIB01JPM156N](https://fred.stlouisfed.org/series/IR3TIB01JPM156N) | JPY | **2002-04** | 2026-07 | 1.45845 | 2026-09-15 |
  | [IR3TIB01CHM156N](https://fred.stlouisfed.org/series/IR3TIB01CHM156N) | CHF | 1999-07 | 2026-08 | **−0.045** | 2026-09-15 |
  | [IR3TIB01CAM156N](https://fred.stlouisfed.org/series/IR3TIB01CAM156N) | CAD | 1956-01 | 2026-08 | 2.28 | 2026-09-15 |
  | [IR3TIB01AUM156N](https://fred.stlouisfed.org/series/IR3TIB01AUM156N) | AUD | 1968-01 | 2026-08 | 4.51 | 2026-09-15 |
  | [IR3TIB01NZM156N](https://fred.stlouisfed.org/series/IR3TIB01NZM156N) | NZD | 1973-12 | 2026-08 | 2.98 | 2026-09-15 |

- **The US FRED page names no specific interbank benchmark.** It shows only the OECD filters (REF_AREA USA, MEASURE IR3TIB, FREQ M). — [FRED IR3TIB01USM156N](https://fred.stlouisfed.org/series/IR3TIB01USM156N)
- **BIS central bank policy rates (CBPOL):** released since Sep 2017 for more than 40 central banks, some series from 1945. Daily data are released around mid-week; monthly values are the last business day of the month. Where a central bank publishes a band, the midpoint is shown. The documentation was updated 24 Sep 2026. — [BIS cbpol documentation (PDF)](https://www.bis.org/pages/statistics/cbpol-doc.pdf)
- **CBPOL definitions by currency:** — [BIS cbpol doc](https://www.bis.org/pages/statistics/cbpol-doc.pdf)
  - **US:** midpoint of the Fed target from Dec 1985; effective fed funds from Jul 1954 to Dec 1985.
  - **Euro area:** starts 5 Jan 1999. Minimum bid rate from 2000, fixed main refinancing rate from Oct 2008, deposit facility rate from 18 Sep 2024. Pre-1999 rates are separate national series (for example Germany: Lombard rate 1979–84, repo rate 1985–98).
  - **UK:** repo rate 1997–2006, Bank Rate from Aug 2006.
  - **Japan:** guidance for the uncollateralised overnight call rate. **No policy rate was adopted in some periods, including 2001–2006 and 2013–2016,** so the series has gaps.
  - **Switzerland:** discount rate 1946–1999, midpoint of the SNB target range 2000 to Jun 2019, SNB policy rate from 13 Jun 2019.
  - **Canada:** official bank rate 1960–94, overnight target from Jun 1994.
  - **Australia:** cash rate target from 2 Aug 1990.
  - **New Zealand:** official cash rate from 17 Mar 1999; overnight cash rate Jan 1985 to Mar 1999.
- **CBPOL mirrors:**
  - DBnomics hosts it as "[WS_CBPOL] Central bank policy rates". — [DBnomics BIS/WS_CBPOL](https://db.nomics.world/BIS/WS_CBPOL)
  - François Geerolf's site shows CBPOL daily with last observation 6 Oct 2026, page updated 9 Oct 2026, but gives no direct download link. — [fgeerolf.com CBPOL](https://fgeerolf.com/data/bis/CBPOL.html)
- **GitHub `datasets/euribor`:** Euribor by maturity from EMMI, monthly. `data/euribor-3m-monthly.csv` runs from 1999-01-01 (3.245) to 2026-09-01 (2.608). — [datasets/euribor README](https://raw.githubusercontent.com/datasets/euribor/main/README.md), [3-month file](https://raw.githubusercontent.com/datasets/euribor/main/data/euribor-3m-monthly.csv)
- **GitHub `datasets/bond-yields-us-10y`:** monthly from 1953-04 to 2026-08 (US only; long-term rate, not a carry input). — [CSV](https://raw.githubusercontent.com/datasets/bond-yields-us-10y/main/data/monthly.csv)
- **Repos probed that do not exist** (raw `datapackage.json` returned 404 on both main and master): `datasets/interest-rates`, `datasets/policy-rates`, `datasets/central-bank-rates`, `datasets/libor`. — e.g. https://raw.githubusercontent.com/datasets/interest-rates/main/datapackage.json
- **Network reachability from this research sandbox on 2026-10-14:**
  - **Blocked** (proxy CONNECT 403): fred.stlouisfed.org (`fredgraph.csv`), api.stlouisfed.org, data.bis.org, stats.bis.org, www.bis.org bulk zips, sdmx.oecd.org, the ECB data API, federalreserve.gov, db.nomics.world, github.com, codeload.github.com and datahub.io.
  - **Available:** raw.githubusercontent.com returned 200 and pypi.org is reachable. The GitHub search API is session-blocked ("sessions are bound to their configured repositories").
  - Tested endpoints include https://fred.stlouisfed.org/graph/fredgraph.csv?id=IR3TIB01USM156N and https://data.bis.org/static/bulk/WS_CBPOL_csv_flat.zip.
- **The existing FX price file is current and uniformly quoted as currency per USD,** contrary to its README. The README says Australia, Euro, Ireland, New Zealand and the UK have a "USD/currency ratio". But the data shows Euro 0.628 on 2008-07-15 (= 1/1.592 EURUSD), UK 0.4782 on 2007-11-09 (= 1/2.09) and Australia 0.9069 on 2011-07-27 (= 1/1.10). On 2026-10-09 the values are EUR 0.8934, GBP 0.7559, AUD 1.4329, NZD 1.7822, JPY 158.34, CHF 0.8308 and CAD 1.4269. Coverage runs from 1971-01-04 (Euro from 1999-01-04) to 2026-10-09. — [README](https://raw.githubusercontent.com/datasets/exchange-rates/main/README.md), [daily.csv](https://raw.githubusercontent.com/datasets/exchange-rates/main/data/daily.csv)
- **The repo's loader handles this correctly.** `load_prices()` treats every series as per-USD and builds `closes[p] = u[q] / u[b]`. — `/home/claude/mt5-trading-/scripts/backtest_macrofx.py` lines 47–65

### Inferences
- **Practical carry stack from 2000:**
  - Use FRED 3-month interbank rates as the base for USD, CAD, AUD, NZD and CHF.
  - **EUR:** FRED EZ to Jan 2026, then splice in GitHub Euribor 3-month. They are near-identical concepts; check the overlap months.
  - **GBP:** FRED GB to Jan 2026, then BIS Bank Rate, or keep the last value until FRED resumes.
  - **JPY:** FRED JP from Apr 2002. For 2000 to Mar 2002 use BIS CBPOL where available. CBPOL Japan has gaps in 2001–2006, so a near-zero placeholder (BoJ zero-rate era) or another call-rate series is needed.
  - **CHF:** keep negative values signed; do not floor at zero.
- **Avoid look-ahead.** OECD monthly values post about 2–7 weeks after month end (the August value was updated on Sep 15). Lag the monthly rate by at least one full month, forward-filled to the weekly rebalance date.
- **Because FRED and BIS are unreachable from this sandbox,** the workable route is one of:
  - Fetch the 8 FRED CSVs plus BIS `WS_CBPOL` once from a machine with open egress (Casey's laptop or the Railway backend, whose egress was not verified here). Commit them under a `data/rates/` folder with a refresh script, or have the backend serve them.
  - Ask for fred.stlouisfed.org and data.bis.org to be allowlisted for these sessions.
- **The EZ and GB stall is unexplained.** That both stopped at the same update suggests an OECD-side change for those two aggregates. Possible causes include the "19 Countries" euro-area definition (Croatia made it 20 in 2023) and the end of GBP LIBOR. This is speculation; treat both as possibly discontinued until FRED updates them.

### Gaps
- Whether IR3TIB01EZM156N and IR3TIB01GBM156N will resume could not be determined. There is no notice on the FRED pages.
- The exact underlying benchmark per country in OECD's 3-month interbank series (for example TIBOR vs other, or the post-LIBOR replacement for CHF and GBP) is not stated on the FRED pages and was not retrieved from OECD (blocked).
- The FRED immediate or call-money series (IRSTCI01xxM156N) were not checked because FRED is blocked here. They might fill Japan 2000–2002 but are unverified.
- No community GitHub mirror of OECD MEI rates or BIS CBPOL could be found: the GitHub search API is blocked and only guessed repo names could be probed.

---

## 4. Free data for a value signal (PPP and BIS real effective exchange rates)

### Takeaway
The best free value input is the BIS real effective exchange rate (monthly, CPI-based, Index 2020 = 100). It is mirrored on FRED as `RB{cc}BIS` (broad) and `RN{cc}BIS` (narrow), current to Jul 2026. The FRED PPP series `PPPTTL…` are stale (Penn World Table 7.1, ending 2010). A World Bank PPP mirror on GitHub (`datasets/ppp`) is reachable from here and covers 7 of the 8 currencies annually from 1990 to 2024, with no euro area.

### Cited Findings
- **BIS effective exchange rates (EER):** — [BIS data portal: EER topic](https://data.bis.org/topics/EER)
  - Nominal (NEER) and real (REER) indices. The broad basket covers 64 economies; the narrow basket covers 26 (nominal) or 27 (real) "major trading partners".
  - Monthly; daily data exist only for nominal indices.
  - Broad: monthly from 1994, daily from 1996. Narrow: monthly from 1964, daily from 1983.
  - Units are Index 2020 = 100. Monthly data are released around mid-month: the last release was 8 Oct 2026 and the next is 15 Oct 2026.
  - Bulk downloads are at data.bis.org/bulkdownload.
- **FRED mirror of BIS REER:** — [FRED RBUSBIS](https://fred.stlouisfed.org/series/RBUSBIS)
  - "Real Broad Effective Exchange Rate for United States", `RBUSBIS`: monthly, Index 2020 = 100, Jan 1994 to Jul 2026 (latest 108.25), last updated 2026-08-20. It is a weighted average of bilateral rates adjusted for relative consumer prices.
  - Related IDs listed on the page: `RBXMBIS` (euro area), `RBJPBIS` (Japan), `RBGBBIS` (UK), `NBUSBIS` (nominal broad US) and `RNUSBIS` (real narrow US).
- **FRED `PPPTTLJPA618NUPN`:** "Purchasing Power Parity over GDP for Japan", annual, national currency per USD, 1950–2010. Source is Penn World Table 7.1, last updated 2012-09-17. It is stale for a 2000–2026 backtest. — [FRED PPPTTLJPA618NUPN](https://fred.stlouisfed.org/series/PPPTTLJPA618NUPN)
- **GitHub `datasets/ppp`:** World Bank International Comparison Program "PPP conversion factor, GDP (LCU per international $)", indicator PA.NUS.PPP. — [README](https://raw.githubusercontent.com/datasets/ppp/main/README.md), [ppp-gdp.csv](https://raw.githubusercontent.com/datasets/ppp/main/data/ppp-gdp.csv)
  - Computed from the file: US, UK, Japan, Switzerland, Canada, Australia and New Zealand each have 35 annual values from 1990 to 2024.
  - 2024 values: UK 0.664, JP 94.46, CH 0.949, CA 1.150, AU 1.367, NZ 1.464, US 1.
  - **"Euro area" is absent.**
- **GitHub `datasets/cpi`:** World Bank annual CPI, 1960–2024 for all 7 non-euro G8 countries plus "Euro area" (to 2023). Annual only. — [cpi.csv](https://raw.githubusercontent.com/datasets/cpi/main/data/cpi.csv)

### Inferences
- **Preferred value signal:** per-currency BIS real broad EER from FRED (`RB{US,XM,GB,JP,CH,CA,AU,NZ}BIS`), measured as a z-score or percentile against a long rolling window (for example 5–10 years). A pair score is value(quote) − value(base).
- **The CH, CA, AU and NZ REER IDs are unverified.** Following FRED's naming pattern they should be `RBCHBIS`, `RBCABIS`, `RBAUBIS` and `RBNZBIS`, but only US, XM, JP, GB (and the nominal and narrow US variants) were confirmed this session. Lag by 1–2 months: Jul data was posted on Aug 20.
- **A PPP-gap alternative that works from this sandbox today:** log(spot / PPP) from `datasets/ppp`, using Germany's PPP as the euro proxy if it is present in the file (not checked). It is annual with a roughly one-year publication lag, so only a slow signal is possible.
- **Value is a slow signal by nature,** so monthly or annual data frequency is not a binding constraint for a weekly-rebalanced system. It also means far fewer trades, which helps against the swap fee and spread costs above.

### Gaps
- No GitHub mirror of BIS REER was found (search blocked).
- OECD PPP (as opposed to World Bank or Penn World Table) on FRED was not identified.
- Whether `datasets/ppp` includes Germany or another euro member as a euro proxy was not checked.

---

## 5. Position sizing on $1,000 with a 0.01-lot minimum

### Takeaway
One 0.01 lot is $561–$1,323 of notional depending on the base currency. That is 0.56–1.32× leverage per position on $1,000, and 1 standard deviation of annual P&L is $33–$97 per micro lot.

At a 10% volatility target, the right size per position on $1,000 is only 0.34–0.84 micro lots, so the minimum lot already overshoots by 1.2–3×. **Volatility targeting is not possible at $1,000. Sizing becomes reasonably granular (rounding step ≤ ~25%) around $10,000 for 4–8 positions, and fine (≤ ~12%) around $25,000.**

### Cited Findings
All values are computed from [H.10 daily.csv](https://raw.githubusercontent.com/datasets/exchange-rates/main/data/daily.csv), using 2026-10-09 prices and 1,000 base units per 0.01 lot.

- **USD per unit of base:** EUR 1.1193, GBP 1.3229, AUD 0.6979, NZD 0.5611, CAD 0.7008, CHF 1.2037, JPY 0.0063.
- **Notional per 0.01 lot:**

  | Base currency | Notional per 0.01 lot |
  |---|---|
  | GBP | $1,323 |
  | CHF | $1,204 |
  | EUR | $1,119 |
  | USD | $1,000 |
  | CAD | $701 |
  | AUD | $698 |
  | NZD | $561 |

- **Pip value per 0.01 lot by quote currency:**

  | Quote currency | Pip value |
  |---|---|
  | GBP | $0.132 |
  | CHF | $0.120 |
  | USD | $0.100 |
  | CAD, AUD | $0.070 |
  | JPY | $0.063 |
  | NZD | $0.056 |

- **Annualised vol, last 252 days** (2025-10-07 to 2026-10-09): median 5.9%, from EURGBP 3.6% to AUDJPY and NZDJPY 8.8%. The full sample from 2000-01-03 to 2026-10-09 (6,713 days) has a median of 10.5%, from EURCHF 6.4% to AUDJPY 14.7%. **Sep 2008 to Mar 2009: median 23.2%, AUDJPY 51.1%, NZDJPY 44.1%.**
- **1 SD of annual P&L per micro lot (last-12-month vol):** from $33 (NZDCHF) and $34 (AUDNZD) to $96.5 (GBPJPY), with EURUSD at $61 and USDJPY at $82. That is 3.3–9.7% of $1,000 equity per micro lot, in a calm year.
- **Minimum-size book at $1,000** (one micro lot each, average notional about $1,150, last-12-month median vol):

  | Positions | Gross notional | Annual vol, uncorrelated | Annual vol, correlation 0.3 |
  |---|---|---|---|
  | 4 | $4,600 (4.6×) | about 14% | about 19% |
  | 8 | $9,200 (9.2×) | about 19% | about 34% |

  At full-sample vol these figures are about 1.8× higher; at 2008-crisis vol, about 4×.
- **10% vol target with equal risk** (micro lots per position at the median 5.9% vol; the rounding step is one 0.01 lot as a share of target size):

  | Equity | 4 pos, ρ 0 | 4 pos, ρ 0.3 | 8 pos, ρ 0 | 8 pos, ρ 0.3 |
  |---|---|---|---|---|
  | $1,000 | 0.84 (step 118%) | 0.61 (163%) | 0.60 (167%) | 0.34 (295%) |
  | $2,500 | 2.11 (47%) | 1.53 (65%) | 1.49 (67%) | 0.85 (118%) |
  | $5,000 | 4.22 (24%) | 3.06 (33%) | 2.99 (33%) | 1.70 (59%) |
  | $10,000 | 8.45 (12%) | 6.13 (16%) | 5.97 (17%) | 3.39 (29%) |
  | $25,000 | 21.1 (5%) | 15.3 (7%) | 14.9 (7%) | 8.48 (12%) |

### Inferences
- **What $1,000 can actually do:** fixed one-micro-lot positions, on or off, with 3–4 positions at most. Expect realised volatility of about 15–20% in calm markets and 50%+ in a 2008-type episode. Size changes can only happen by dropping positions, not by scaling.
- **Sensible minimum account for a diversified 4–8 position G8 book with real volatility targeting:** about $10,000 for 4 positions, and about $25,000 for 8 correlated positions at 10% target vol.
- **Margin is not the binding constraint;** risk is. 9× gross notional is allowed by typical retail leverage but is about 3× too much risk for a 10% target. MidasFX's leverage was not verified.
- **The 0.01-lot = 1,000-unit contract size is the standard MT4 convention.** Confirm it on MidasFX with `MarketInfo(sym, MODE_LOTSIZE)`, `MODE_MINLOT` and `MODE_LOTSTEP`. If MidasFX offers a cent or nano account (0.001 lot or a cent-denominated account), the granularity problem disappears; this was not verified.
- **Size by net currency exposure, not pair count.** With 28 crosses, 8 pair positions can stack into a 4–6× exposure to a single currency (for example short JPY across AUDJPY, NZDJPY and CADJPY). Aggregate pair positions into 8 currency exposures before sizing.

### Gaps
- No MidasFX contract-specification, leverage or account-type (cent or micro) page was found.
- The vol figures above are computed from H.10 noon fixes (one print a day), which slightly understates intraday and weekend-gap risk.

---

## 6. Practical risk controls for retail systematic FX (volatility targeting, max-drawdown stop, correlation limits)

### Takeaway
Carry has negative skew and drawdowns that cluster with volatility spikes: AUDJPY vol went from about 15% to 51% in 2008–09. The academic evidence supports risk-rebalanced, differential-weighted carry over naive equal-weight carry. The retail-specific controls below are practitioner inferences; no retail-focused study was retrieved.

### Cited Findings
- **Daniel, Hodrick & Lu** (NBER WP 20433, 2014; *Critical Finance Review* 2017), studying G10 carry: — [NBER w20433](https://www.nber.org/papers/w20433)
  - Carry performance depends on the base currency.
  - Dynamically weighting positions by interest-rate spread and rebalancing them for risk improves performance.
  - Dollar-neutral carry earns abnormal returns that are not statistically significant; the dollar-exposure component earns significant abnormal returns with little skewness.
  - Equity, bond, FX and volatility risks do not explain the profits.
  - Negative skewness of longer-horizon returns is attributed to time-varying autocorrelation.
  - Option hedging reduces but does not eliminate the abnormal returns.
- **Computed regime shift:** AUDJPY annualised vol was 14.7% over 2000–2026 versus 51.1% over Sep 2008 to Mar 2009, and the median G8 pair went from 10.5% to 23.2%. — computed from [H.10 daily.csv](https://raw.githubusercontent.com/datasets/exchange-rates/main/data/daily.csv)
- **The 5–6 p.m. ET hour** is when stops get hit on wide spreads, even when the mid-price does not move. — [CME Group (2026)](https://www.cmegroup.com/articles/2026/when-fx-futures-pause.html)

### Inferences (practitioner design, not directly sourced)
- **Volatility targeting:** use an EWMA or 60-day vol per pair, plus a portfolio covariance estimate, recomputed at the weekly rebalance, and scale gross exposure to the target. At $1,000 this degrades to "cut the weakest-signal positions when forecast portfolio vol exceeds the cap."
- **Net-currency exposure cap:** after netting the 28-pair book into 8 currency exposures, cap any single currency at about 1.5–2× one position's risk budget. This matters most for JPY and CHF funding legs in carry, and for USD in trend.
- **Correlation and cluster limits:** treat AUD, NZD and CAD (commodity bloc), and EUR, CHF and GBP (European bloc) as clusters, and limit to one same-direction position per cluster at small account sizes. Optionally require the forecast pairwise correlation of new positions to be below about 0.6.
- **Drawdown stop:** portfolio-level circuit breaker, for example halve exposure at −15% from peak and go flat at −25%, with a re-entry rule (for example after N weeks or a new signal regime). Test it in the backtest; drawdown stops often cut both tail losses and recovery gains.
- **Gap risk:** a weekly system is always exposed to weekend gaps, so size for gap risk rather than relying on stops.
- **Execution gates:** spread filter, a no-trade window around the 5 p.m. ET rollover and the Sunday open, and a daily swap-sign check so a position does not silently become a large negative-carry hold.
- **Carry-specific:** consider a dollar-neutral versus dollar-exposure split, given Daniel, Hodrick & Lu's finding that the dollar-exposure component carries the significant returns. Weight positions by the size of the differential net of the broker fee (see section 1).
- **Prior knowledge, not re-verified this session:** Brunnermeier, Nagel & Pedersen, "Carry Trades and Currency Crashes" (NBER Macroeconomics Annual 2008), links carry losses to sudden unwinds when risk appetite drops (VIX spikes). A VIX- or vol-spike de-risking filter is a common practitioner response. — listed at [NBER chapter c7286](https://www.nber.org/chapters/c7286); its content was not fetched.

### Gaps
- No retail-specific empirical study of vol-targeting, drawdown stops or correlation caps in FX was retrieved.
- Drawdown magnitudes from Daniel, Hodrick & Lu were not extracted (only the abstract was read).
- Brunnermeier, Nagel & Pedersen was not fetched this session, so its specific findings are not verified here.

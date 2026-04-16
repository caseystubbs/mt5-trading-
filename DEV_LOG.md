# EST Liquidity Breakout EA — Development Log

## System overview

Automated S&P 500 breakout trading system that trades liquidity sweeps at key intraday levels.

**Stack:** MQL5 EA (MetaTrader 5) → FastAPI (Railway) → PostgreSQL → Dashboard

**Live dashboard:** https://mt5.freedomincomeoptions.com/

**Daily summary:** https://mt5.freedomincomeoptions.com/summary

**Infrastructure:**
- EA runs on Windows VPS with MT5 (Coinexx demo, SPXUSD)
- Real-time trade events sent via WebRequest to Railway API
- PostgreSQL stores all events, daily summaries, patterns, changelog
- Dashboard + daily summary page accessible from phone/laptop anywhere
- Nightly PowerShell script pushes CSV journals + daily logs to GitHub
- Pattern analysis auto-tracks win rate by level, direction, trend alignment, candle strength

## Changelog

### v3.1.2 — 2026-04-15
**Type:** Bug fixes + diagnostics

- **ea_version column widened:** `VARCHAR(10)` → `VARCHAR(100)` in both `trade_events` and `daily_summaries` tables. The version string `"3.1.2 | Plan: Apr 15"` (22 chars) was crashing every webhook POST with `StringDataRightTruncationError`. Fixed via asyncpg ALTER TABLE from Codespaces. `main.py` CREATE TABLE statements patched so fix persists on redeploy.
- **Premarket log spam fixed:** `CalculatePremarketLevels()` was printing "Premarket ready" on every tick after finalization — produced 34,000+ identical log lines per session. Throttle logic corrected: logs once on first ready, once on finalization, silent after that.
- **Timezone diagnostic added to OnInit():** Prints GMT time, broker time, EA-calculated EST time, EDT/EST mode, entry window open/closed, past force close yes/no, and broker GMT offset in hours. Confirmed broker is GMT+3 (EDT mode active, correct EST offset).

### v3.1.2 session — 2026-04-15
**Type:** Trading day (EA 0 trades, Casey 0 manual trades)

**The plan was right. Everything else failed.**

Today's plan levels — PMH 6983.0 and PML 6961.8 — were the exact session pivots. Price held PML as support and broke above PMH, then ran 84 points to 7045+. The PMH breakout long setup was textbook: entry ~6984, stop ~6978 (PMH - $5 buffer), price ran 60+ points. Hypothetical P&L: **+$240–$480** depending on trail — would have been the biggest single winning day in system history.

**Why the EA didn't trade:**
1. **Webhook 500 all morning** — VARCHAR(10) bug crashed every event POST. No trade events logged until fix applied at ~4:30 PM EST.
2. **EA confirmed running at 10:34 EST** — price was already at 6997, 14+ points above plan levels. Outside MaxProximityPrice = 20.0 window.

**Timezone diagnostic confirmed:**
- Broker = GMT+3 ✅
- EDT active (GMT-4) ✅  
- EST calc = 10:34 at load time ✅
- Entry window = OPEN ✅
- Force close = NO ✅

**Key action items:**
- EA must be loaded, compiled, and webhook verified (200 response) BEFORE 9:15 EST every day
- Add pre-session checklist: (1) EA attached, (2) plan levels coded, (3) webhook returning 200, (4) status bar showing SCANNING
- Consider adding a startup webhook ping so we can confirm connectivity before the session opens

### v3.1.1 — 2026-04-14
**Type:** Entry logic fix + features
- **Entry logic rewritten:** Removed IsStrongBullishClose/IsStrongBearishClose filters from CheckLong/ShortSetup. CheckPlanLevel simplified — breakout long now just requires candle close above level + candle within proximity + bullish candle (close > open). Bounce long requires candle low within proximity of level + bullish + close at or above level. Same mirrored for shorts.
- **PM levels live from 4:00 AM:** CalculatePremarketLevels now calculates running high/low from pmStart to NOW during the PM session, instead of waiting until 9:29. Updates every tick.
- **Historical scan expanded:** HistoricalDaysToScan default 20 (was 10), HistLevelProximity default $100 (was $50).
- **Debug prints in CalculateHistoricalLevels:** Shows each day scanned with high/low and distance from current bid. Prints total days found and unique levels.
- **Plan page password removed:** Save button no longer prompts for API key.
- **Broker price offset identified:** MidasFX prices are ~$5 lower than Coinexx for SPXUSD. Casey's 6913.6 entry = ~6918 on Coinexx.

### v3.1.1 session — 2026-04-14
**Type:** Trading day (EA 0 trades, Casey +$26.70 manual)
- EA took 0 trades — third consecutive day. Plan levels were set but entry logic still not triggering.
- Historical levels now showing on chart (D-2 H, D-3 H, D-3 L, D-4 H confirmed in Experts tab).
- PM levels now updating live (PMH=6920.0, PML=6898.5 shown before 9:29).
- Multiple EA restarts during session (v3.1 → v3.1.1) — OR levels only available after 12:49 PM, missing entry window.
- Today's levels: PDH=6893.2, PDL=6795.2, PMH=6920.0, PML=6898.5, ORH=6931.4, ORL=6907.9

**Casey's manual trades (MidasFX, +$5 offset to Coinexx):**

Trade 1: Buy 6903.1 (≈6908 Coinexx) → 6904.3 = +$1.20 (7 min, PM Low zone test)

Trade 2: Buy 6913.6 (≈6918 Coinexx) → TP 6934.0 = +$20.40 (41 min, THE TRADE)
- Entry at exactly PlanLong1 level (6918)
- Stop set at 6906.8 (≈6912 Coinexx, below OR Low)
- TP set at 6934.0 (≈6939 Coinexx, OR High area)
- Trail management: 9:50 trailed stop to 6914.9 (near BE), 10:10 trailed to 6917.0 (plan level), 10:17 TP hit
- Risk $7, Reward $20 = 3:1 R:R

Trade 3: Sell 6957.8 (≈6963 Coinexx) → TP 6952.7 = +$5.10 (2 min, afternoon resistance scalp)

**Casey's trade management framework (learned from journal):**
1. Entry near plan level with directional conviction
2. Stop at nearest key level below/above (OR Low, PM Low — not fixed buffer)
3. Target at next key level above/below (OR High, PM High)
4. Trail stop in stages: first near breakeven → then to the plan level → then let TP hit
5. Does NOT use fixed 1R/2R system — uses level-to-level targets
6. Active management, not set-and-forget
7. Quick to take profit when available (Trade 3: 2 min)

**Why EA didn't trade (diagnosis):**
- Plan levels were set (PlanLong1=6918, PlanLong2=6898, PlanShort1=6918, PlanShort2=6893)
- Price reached all plan levels during the session
- Entry logic was updated but EA was restarted multiple times, OR levels not available during entry window
- Need debug prints on candle-by-candle evaluation to see exactly why CheckPlanLevel returns false

**Action items for tomorrow:**
- Add debug print inside CheckPlanLevel to log every candle evaluation near plan levels
- Casey pastes plan in chat, Claude updates EA code with levels before session
- No more manual EA input — workflow is chat → code → compile → deploy

**Late session fixes (applied to v3.1.1):**
- **Entry window changed to 9:30 EST** (was 9:45). Casey took the main trade at 9:36 — PMH broke before OR was complete. The 15-minute OR wait was costing trades.
- **D-3 H and D-2 H respected perfectly today.** Price bounced off both historical levels during the session. Historical levels are proving reliable as support/resistance zones. Must include relevant historical levels in daily plan going forward.
- **Live status line added (top-left).** Single line shows EA state: waiting for session with plan levels listed, scanning with nearest level and distance, managing trade with live P&L/stop/target, or session over. Updates every tick. Shows "NO PLAN LEVELS SET" if inputs empty — instant visual confirmation EA is configured.
- **PM levels now recalculate every tick during premarket.** Was only calculating once when `!g_pmReady`. Now calls CalculatePremarketLevels on every tick so PM High/Low update live as overnight session develops.

### v3.1 — 2026-04-13
**Type:** Major cleanup + feature
- **Stripped EA down to essentials.** Removed 412 lines (2781 → 2369). 15 inputs removed, 2 old setup detection functions removed, status panel removed, trend arrow display removed.
- **Inputs removed:** UsePDH_PDL, UsePremarketLevels, UseOpeningRangeLevels, RequireBullish/BearishBreakoutCandle, UseStrongCloseFilter, StopBufferPrice, UseLevelBasedStops, AllowLongTrades, AllowShortTrades, OneTradePerDay, UseDailyTrendFilter, DrawEntryMarkers, DrawStopAndTargets, UseDailyPlan, ShowDailyTrendArrow, DailyEMAPeriod
- **Functions removed:** GetLongSetup() and GetShortSetup() — the old 12-setup-type system. Replaced by plan-only detection (GetPlanLongSetup/GetPlanShortSetup).
- **Top-left panel removed:** Clock, status text, levels summary, trigger text — all gone. Chart is clean with just level lines and the bottom-left legend.
- **Legend updated:** Now shows version number (v3.1) and historical levels (D-2 H, D-3 L, etc.) with prices.
- **Defaults updated:** FixedLots=2.0, WebhookURL=mt5.freedomincomeoptions.com, PlanStopBuffer=5.0
- **Plan page auto-levels:** Key levels field auto-populates from EA's DAILY_OPEN webhook. Refresh button for PM/OR after 9:30.

### v3.1 session — 2026-04-13
**Type:** Trading day (plan-based, EA took 0 trades, Casey +$21.50 manual)
- EA deployed with plan levels: PlanLong1=6811.5 (PDL), PlanLong2=6745 (D-4L), PlanShort1=6811.5 (PDL rejection), PlanShort2=6848.2 (PDH), PlanShort3=6767 (D-3L)
- EA took 0 trades all session — price crossed above PDL but entry detection didn't trigger
- Likely cause: candle didn't straddle 6811.5 cleanly enough for proximity check, or breakout happened before 9:45 entry window
- Casey manually traded on MidasFX account (separate broker): 2 trades, +$21.50
  - Short 6799.1 → 6798.1 = +$1.00 (quick scalp near PDL zone)
  - Long 6803.6 → 6824.1 = +$20.50 (bought the PDL/PMH/D-4H stacked support zone, rode 20 pts)
- Today's actual levels: PDH=6848.2, PDL=6811.5, PMH=6803.1, PML=6771.0, ORH=6808.3, ORL=6795.2
- Historical: D-2H=6848, D-3H=6841, D-3L=6767, D-4H=6801, D-4L=6745

**Key observations:**
- Casey's plan correctly identified the PDL zone as the key level — stacked with PMH (6803) and D-4H (6801)
- The long from 6803.6 was in the exact zone the plan highlighted
- EA's entry trigger is too rigid for plan-based trading — needs rethinking
- "Casey's plan was smarter than the EA" — second day in a row this is true
- Entry logic for plan levels may need a different approach than M5 candle straddle

### v2.9.1 session — 2026-04-10
**Type:** Strategy review (worst day — critical lessons)
- 4 trades taken, 0 wins, -$66.80 (real MT5 P&L: -$68.40)
- ALL 4 trades were ORL Bounce Long at the same level (6832.3) with the same stop (6830.3)
- EA has no memory — keeps taking the same losing trade
- Casey's morning plan was excellent but the EA completely ignored it
- Dashboard showed wrong levels (yesterday's data) due to multiple EA restarts sending stale DAILY_OPEN events

**Casey's plan vs EA's actions:**
- Plan identified 6848 (PMH/ORH/PDH convergence) as the decision level
- Plan identified 6812 (PML) as key support
- Plan said: "Long above 6848 on breakout. Short on 6848 rejection. Short below 6812."
- EA did: 4x ORL Bounce Long at 6832 — a level NOT IN the plan
- The only real trade per Casey: short bounce off ORH/PMH/PDH resistance zone at the top
- Price ranged 14 points all day — classic chop between major levels

**Strategy decisions made:**
1. **Phase 1: Better levels** — EA needs to identify quality levels, not just any level. Level hierarchy: PDH/PDL > PML/PMH > ORL/ORH. Stacked levels (multiple levels near each other) rank highest. Add historical levels from past 5-20 days.
2. **Phase 2: Better plans** — Casey and Claude build daily plan together each morning. Eventually an AI agent auto-generates the plan.
3. **Phase 3: Better candles** — Current close % filter is too simple. Need candle range size relative to recent candles (momentum), not just close position.
4. **Phase 4: EA follows the plan** — Plan sets guardrails (focus levels, bias, max trades, chop flag). EA only trades within those guardrails.
5. **One good trade per session** is the goal — not 4-6 shots hoping one works.
6. **Historical daily levels** — scan back 5-20 days for swing highs/lows near current price. Previous PDH/PDL that price keeps reacting to are still live levels.

**Key insight from Casey:**
- "ORL was not a real level. PML was the real support."
- "The only real trade was the short from ORH — 3 levels stacked (PMH + ORH + PDH) with a strong rejection candle."
- "There is probably one good trade per session."
- "We need to get better at finding levels and better at seeing what a candle with momentum looks like."

### v2.9.1 — 2026-04-09
**Type:** Bug fix + features
- **P&L fix (critical):** Added `PriceToDollar()` helper — converts price distance to actual dollar P&L using tick size, tick value, and lot size. Dashboard was showing -$2.10 when real MT5 P&L was -$6.50 (2 lots). Fixed in all close paths: TARGET_2R, FORCE_CLOSE, DetectBrokerSideClose, and NO_BE_HYPOTHETICAL.
- **Added `g_originalLots` global** — stores lot size at trade open for accurate P&L calculation even after partial close
- **Premarket range shading** — dark teal rectangle on chart from 4:00-9:29 EST between PM High and PM Low
- **Opening range shading** — dark yellow rectangle from 9:30 for first 15 min between OR High and OR Low
- **Added `DrawSessionShade()` and `GetESTSessionTime()` helper functions**
- **Daily plan page** — new `/plan` route on Railway dashboard with form for: bias, bias reason, yesterday summary, premarket notes, key levels, long/short setups, invalidation, stop plan, notes
- **`daily_plans` PostgreSQL table** — stores plans by date with `POST /api/plan` and `GET /api/plan/{date}` endpoints
- **Plan tab** added to all dashboard navigation (Dashboard, Summary, Plan)
- **Reason:** Dashboard P&L was wrong with 2-lot positions. Plan page needed for Casey's pre-market preparation workflow.

### v2.9.1 session — 2026-04-09
**Type:** Trading day + strategy development
- 6 trades taken on 3 different setup types (OneTradePerDay OFF)
- 1 win (+$36.50 at 2R), 2 partial wins at 1R (+$4.20, +$3.20), 3 SL losses
- Real MT5 P&L: -$6.50 (Balance: -$8.90 with swap/commission)
- Biggest single trade win ever: #6 PMH Breakout Long +$36.50
- Partial close working correctly with 2 lots (1 lot at 1R, 1 lot rides to 2R)
- Proximity detection working — all trades at real levels (PMH 6777.7 or ORL 6774.0)
- Setup names visible on chart: "#1 PMH Breakout Long", "#2 PMH Bounce Short", etc.
- Level-based stops working (stop at PMH - $2 = 6775.7)

**No-BE tracking results (3 trades):**
- Trade #4 PMH Bounce Short: Actual +$3.90 (partial + BE) → Without BE: +$5.90 on remaining. BE cost $6.20
- Trade #5 ORL Bounce Long: Actual +$2.70 (partial + BE) → Without BE: +$5.90 on remaining. BE cost $6.40
- Trade #6 PMH Breakout Long: Actual +$36.50 (2R) → Without BE: +$24.50 (same 2R). Same outcome.
- Running total: BE has cost ~$12.60 across the two trades that hit BE then reversed

**Key observations:**
- PMH was contested for 90 minutes (Trades 1-4) before the real breakout (Trade 6)
- Trading the same level repeatedly in chop is expensive: -$50.40 in losses before the +$36.50 win
- The winning breakout came AFTER consolidation at ORL — matches Casey's "consolidation then continuation" framework
- Trade #2 (PMH Bounce Short) hit SL in 8 seconds — entered on same candle that stopped out Trade #1. Whipsaw.
- Three distinct setup types fired today: PMH Breakout Long, PMH Bounce Short, ORL Bounce Long

**Casey's strategy direction:**
- Wants a daily plan workflow: analyze yesterday, assess premarket, identify key levels, plan specific setups, define invalidation
- Stops should be placed below key levels, not based on R:R math
- The level IS the invalidation — if price reclaims the level, you're wrong
- Ignore BE discussion for now — gathering more data
- Premarket and OR shading on chart helps visualize session boundaries

### v2.8 session — 2026-04-08
**Type:** Strategy review (critical learning day)
- First day with trades executing end to end via webhook pipeline
- 7 trades taken (OneTradePerDay intentionally OFF by Casey)
- 1 win (+$21.60 at 2R target), 6 losses, net -$32.00
- First ever 2R target hit (Trade 8: LONG PDH continuation)
- Trade 3 (SHORT PML) hit 1R, moved to BE, closed at BE -$0.30 — would have been big winner without BE
- Error 4756 appeared once mid-session (Trade 4) — may be related to partial close attempt on previous trade
- Navigation tabs added to dashboard and summary pages

**Strategy insights from Casey's review:**
- Current entry logic ("strong candle above level = buy") is fundamentally wrong
- PDH at 6628.6 with price at 6780 doesn't mean every bullish candle is a PDH breakout
- PDH breakout is a CAMPAIGN — the initial break, the consolidation, then the continuation
- Trade 8 won because it caught the continuation wave after consolidation, not because of a simple candle pattern
- Levels have two roles: BIAS (PDH/PDL tell you direction) and TRIGGER (PML/ORL/ORH/PMH are where trades happen)
- Bounce setups: price comes to a level and reverses (PDH as support, PML as support, etc.)
- Breakout setups: price crosses through a level (PMH breakout, PML breakdown, etc.)
- Stop placement should be based on levels (above/below the trigger level) not candle highs/lows
- Breakeven at 1R needs evaluation — may be killing winners. Track "no BE" hypothetical P&L
- Each setup needs a human-readable name, daily trade number, and chart label
- DO NOT add filters without understanding the entry logic first
- The trend display is observation only — not a filter

### API v1.1 — 2026-04-07
**Type:** Feature + bug fix
- Added `/summary` and `/summary/{date}` pages — auto-generated daily trading reports
- Report includes: day grade (A/B/C/D), auto-analysis, levels, trade cards, event timeline, notes, lessons
- Date navigation between available trading days
- Fixed `/api/daily-log-markdown/{date}` returning "Not Found" — UTC/EST date mismatch in query
- Events now queried across date boundaries to handle UTC offset
- CORS middleware added for browser-based API testing
- Custom domain live: mt5.freedomincomeoptions.com

### v2.8 — 2026-04-06
**Type:** Feature (major)
- Added Railway API webhook system — EA sends real-time events via HTTP POST
- New inputs: `UseWebhook`, `WebhookURL`, `WebhookAPIKey`
- 8 webhook functions mirror all CSV log events (DAILY_OPEN, SETUP_FOUND, SETUP_REJECTED, TRADE_OPENED, TRADE_CLOSED, etc.)
- Non-blocking 5-second timeout so webhooks never delay trading
- Railway API deployed with PostgreSQL: trade events, daily summaries, pattern tracking, changelog
- Dashboard live at https://mt5.freedomincomeoptions.com/
- API endpoints: /api/event, /api/stats, /api/today, /api/daily-log/{date}, /api/cumulative-log, /summary
- Auto-generates daily markdown reports for GitHub
- Pattern analysis: win rate by level, direction, trend alignment, candle strength, rejection reasons
- **Reason:** Need remote monitoring while travelling + systematic pattern tracking for improvement

### v2.7 — 2026-04-03
**Type:** Bug fix (critical)
- Fixed OneTradePerDay: `g_tradeTakenToday` now set in ALL close paths (broker SL, target, force close)
- Added `DetectBrokerSideClose()` — queries broker deal history for actual close price/P&L
- Fixed phantom P&L in journal — stale `g_entryPrice` was contaminating calculations
- Added `g_hadPositionLastTick` state tracker
- Added `ResetTradeState()` calls after every close path
- **Reason:** Journal reported +$274 profit when actual was -$56.70 loss

### v2.6 — 2026-04-02
**Type:** Feature
- Added CSV trade journal system (MQL5/Files/ESTLB_Journal_YYYYMMDD.csv)
- Logs: DAILY_OPEN, SETUP_FOUND, SETUP_REJECTED, TRADE_OPENED, TRADE_CLOSED, DAILY_SUMMARY
- Fixed partial close log spam (prints once instead of every tick)

### v2.5 — 2026-04-01
**Type:** Bug fix
- Changed MinimumBreakoutPoints/MaximumStopPoints from MT5 points to price values
- Now works on any broker regardless of Point size (0.01 vs 0.1)
- Defaults: MinBreakout=$2.50, MaxStop=$30.00

### v2.4 — 2026-04-01
**Type:** Feature + fix
- Version number displayed in chart legend
- Legend background color as configurable input
- Fixed point scaling for US500 broker

### v2.3 — 2026-04-01
**Type:** Revert
- Entry window reverted to 9:45-11:30 EST (was incorrectly widened based on wrong timezone data)

### v2.2 — 2026-03-31
**Type:** Bug fix (critical)
- GMT-based timezone system — no broker offset calculation needed
- `GetESTNow()` uses `TimeGMT()` directly, converts to EST/EDT
- Automatic DST handling (second Sunday March → first Sunday November)
- **Reason:** Clock showed 16:23 when it was 9:23 EST, all session windows were 7 hours off

### v2.1 — 2026-03-31
**Type:** Attempt (replaced by v2.2)
- Auto-detect broker-to-EST offset (had rounding issues, replaced)

### v2.0 — 2026-03-31
**Type:** Feature
- Legend moved to bottom-left corner
- PM High/Low colors changed from blue to cyan (better visibility)
- Live EST clock with session timer and countdown

### v1.9 — 2026-03-31
**Type:** Feature
- Legend panel with dark grey background
- Color-coded level descriptions
- Background color as input setting

### v1.8 — 2026-03-31
**Type:** Config change (reverted in v2.3)
- Entry window widened to 9:45-15:00 (based on incorrect timezone analysis)

### v1.7 — 2026-03-30
**Type:** Feature
- Added level legend on chart with descriptions and prices
- Version number in legend header

### v1.6 — 2026-03-30
**Type:** Feature
- Live status panel: SCANNING/IN LONG/Done/Session over
- Levels summary line
- Next trigger prices for long and short

### v1.5 — 2026-03-30
**Type:** Bug fix
- PDH/PDL scans back up to 5 days for weekends/holidays

### v1.4 — 2026-03-29
**Type:** Bug fix
- Log spam eliminated (failure messages print once per day)
- Better error messages for level calculation failures

### v1.3 — 2026-03-29
**Type:** Bug fix
- SymbolSelect no longer blocks init (some demo brokers return false for valid symbols)
- Validates symbol by checking bid price and point value instead

### v1.2 — 2026-03-29
**Type:** Bug fix
- Added version constant and startup print
- Added OnDeinit for cleanup

### v1.1 — 2026-03-28
**Type:** Bug fix
- Fixed 'TradeSymbol' constant cannot be modified error
- Added `g_tradeSymbol` mutable global

### v1.0 — 2026-03-28
**Type:** Initial release
- PDH/PDL, Premarket, Opening Range levels
- Strong candle breakout filter
- 1R partial + breakeven + 2R target management
- One trade per day
- Force close at 15:55 EST

---

## Trading rules

**Entry (current v2.8 — being redesigned):** M5 candle closes beyond a key level by MinimumBreakoutPrice ($2.50) with a strong close (top/bottom 30% of candle range)

**Stop (current):** Breakout candle's low (longs) or high (shorts)

**Stop (planned):** Based on levels — stop goes below/above the trigger level with a buffer, not at the candle extreme

**Targets:** 1R = same distance as stop, 2R = 2x distance

**Management:** At 1R: close 50% + move stop to breakeven. At 2R: close remaining. Force close at 15:55 EST.

**Management (under review):** Breakeven at 1R may be killing winners. Tracking "no BE" hypothetical P&L to evaluate.

---

## Casey's trading framework (growing daily)

*This section captures Casey's market understanding as it develops. The EA should be built to match this framework, not the other way around.*

### Level roles

Levels serve two distinct purposes:

**Bias levels (where are we in the bigger picture):**
- Price above PDH = bullish day bias
- Price below PDL = bearish day bias
- These tell you WHICH DIRECTION to look for trades, not where to enter

**Trigger levels (where do trades actually happen):**
- PMH, PML, ORH, ORL = intraday levels where price interacts
- PDH and PDL are ALSO triggers when price is actually near them and crossing through
- A trade needs a trigger — being above a bias level is not enough

### Setup types (named)

**Breakout/Breakdown setups** — price crosses through a level:
- PDH Breakout Long
- PDL Breakdown Short
- PMH Breakout Long
- ORH Breakout Long
- PML Breakdown Short
- ORL Breakdown Short

**Bounce setups** — price comes to a level and reverses:
- PDH Bounce Long (price pulls back to PDH as support)
- PDL Bounce Short (price rallies up to PDL as resistance)
- PML Bounce Long
- ORL Bounce Long
- PMH Bounce Short
- ORH Bounce Short

### Key principles learned

**From Apr 10 — level quality matters more than candle quality:**
- ORL is a weak level (just where the first 15 min printed). PML is real support. PDH/PDL are the anchors.
- Level hierarchy: PDH/PDL > PML/PMH > ORL/ORH. EA must prioritize major levels.
- Stacked levels (3 levels near each other like PMH + ORH + PDH) are much stronger than single levels.
- A 98% close candle at a weak level still loses. Level quality > candle quality.

**From Apr 10 — the plan was smarter than the EA:**
- Casey's plan identified 6848 as the decision level and 6812 as support. The EA traded ORL (6832) — not in the plan.
- The only real trade was a short off the 6848 zone (3 stacked levels). EA was long at ORL and couldn't see it.
- The EA needs to be plan-aware — either read the plan from the API or have built-in level scoring that reaches the same conclusions.

**From Apr 10 — chop detection:**
- Overnight was in a range. PM range was tight. Price sat between major levels all day.
- 14-point range = chop day. The EA should recognize this and either wait for a breakout or skip the day.
- "There is probably one good trade per session" — the goal is finding THE trade, not taking every signal.

**From Apr 10 — historical levels:**
- EA only looks at yesterday's PDH/PDL. But levels from 3, 5, 10 days ago can still be live if price keeps reacting to them.
- Need to scan back further and identify swing highs/lows that are near current price.
- Previous PDH/PDLs that haven't been broken are still key charting zones.

**From Apr 9 — contested levels eventually break:**
- PMH was tested 4 times (Trades 1-4) before the real breakout (Trade 6). 
- Trade 6 came after consolidation at ORL — confirming the "consolidation then continuation" pattern from Apr 8.
- But Apr 10 showed the opposite — ORL was tested 4 times and never held. Not every contested level breaks through.

**From Apr 8 — PDH continuation:**
- A PDH breakout is a CAMPAIGN, not a single candle. The initial break launches price, then it consolidates, then the continuation wave comes.
- Trade 8 won because it caught the continuation after consolidation — price based around 6757, then pushed to 6789.
- The consolidation zone after a big move IS the setup forming. The breakout of the consolidation is the trigger.

**From Apr 8 — entry context:**
- Just being above PDH doesn't mean buy every strong candle. Price at 6780 with PDH at 6628 = bullish bias, but you need a TRIGGER (bounce off support, breakout of consolidation, crossover of PMH/ORH).

**From Apr 8 — PML breakdown:**
- Trade 3 (SHORT PML) was a correct setup — price broke through PM Low with conviction.
- It hit 1R, moved to BE, then got stopped at BE for -$0.30. Without BE it would have been a big winner.

**From Apr 8 — level relationships:**
- When PML breaks and PDL is 130 points below, there's room to run → good short opportunity.
- The distance between the trigger level and the next support/resistance below/above tells you the potential reward.

**From Apr 8 — stops:**
- Stop placement should be based on the level itself (above/below the trigger level) not the candle high/low.
- If you short a PML breakdown, the trade is wrong when price reclaims PML → stop goes above PML.

**From Apr 1 — stop distance:**
- Trade 1 had a 9.8pt stop, got clipped. Trade 2 had 21.2pt stop, worked. Wider stops survive better.

**From Apr 2 — OneTradePerDay:**
- Casey intentionally turns this ON or OFF depending on the day. The setting works correctly.

### Things we don't know yet (track and learn)

- [ ] Does breakeven at 1R help or hurt overall? (Early data: BE cost ~$26.60 across 4 tracked trades)
- [ ] Which setup types have the highest win rate?
- [ ] Does candle range size (momentum) predict winners better than close %?
- [ ] How to distinguish "contested level about to break" (Apr 9) from "weak level, stop trading it" (Apr 10)?
- [ ] What's the optimal number of historical days to scan for levels? (5? 10? 20?)
- [ ] Does level stacking (multiple levels near each other) predict higher win rate?
- [ ] How tight is "too tight" for a PM range? (chop detection threshold)
- [ ] One good trade per session — what does the ideal trade look like across all our data?

---

## Patterns observed

*Updated daily from trade journal analysis and Railway API pattern tracking*

### Confirmed patterns
- **Broker-side SL closes not detected** — Fixed in v2.7 with `DetectBrokerSideClose()`
- **OneTradePerDay flag resets on EA restart** — Fixed in v2.7 with proper state management
- **Journal P&L can be fictional** — Fixed in v2.7 by reading actual broker deal history
- **Partial close fails at minimum lot size** — Logged but not fixed (broker min = 1.0 lot, can't split)
- **Error 4756 intermittent** — May be related to partial close attempt leaving position in liminal state (Apr 8, Trade 4)
- **"PDH breakout" 150pts above PDH is not a breakout** — No market context. Need trigger level or consolidation pattern.

### Pending observations (needs more data)
- [ ] Stop placement too tight — breakout bar low gets clipped on normal pullback (seen on Apr 1)
- [ ] Breakeven at 1R killed a winner on Apr 8 Trade 3 — need "no BE" tracking
- [ ] Winning trade (Apr 8 Trade 8) had strongest candle close of the day (92.5%) — does close strength predict winners?
- [ ] Counter-trend setups (SHORT while Bullish) can work — Apr 8 Trade 3 was counter-trend and hit 1R
- [ ] Time of day: Trade 8 (the winner) was at 11:24, later in the session

### Pattern tracking (auto-calculated by Railway API)
- Win rate by level: `/api/stats?days=30` → `by_level`
- Win rate by direction + trend: `/api/stats?days=30` → `by_trend_alignment`
- Win rate by candle strength: `/api/cumulative-log` → `by_close_strength`
- Rejection analysis: `/api/cumulative-log` → `rejection_analysis`

---

## Performance metrics

*Auto-updated nightly from Railway API via push-journal.ps1*

| Metric | Value | Updated |
|--------|-------|---------|
| Total trades | — | — |
| Win rate | — | — |
| Avg P&L per trade | — | — |
| Total P&L | — | — |
| Max drawdown | — | — |
| Profit factor | — | — |

---

## Trading days log

| Date | Version | Trend | Trades | Wins | P&L | Key observation |
|------|---------|-------|--------|------|-----|-----------------|
| 2026-04-01 | v2.5 | Bullish | 2 | 1 | ~+$14 | First live trade day. Stop too tight on trade 1, trade 2 hit 1R+ |
| 2026-04-02 | v2.6 | Bullish | 8 | 0 | -$56.70 | OneTradePerDay broken, journal reported fake P&L. All 8 trades hit SL |
| 2026-04-07 | v2.8 | Bullish | 0 | 0 | $0.00 | 7 SHORT setups on PDL all rejected — FixedLots=0.01 vs broker min 1.0. Would have caught 35pt drop |
| 2026-04-08 | v2.8 | Bullish | 7 | 1 | -$32.00 | First 2R hit (+$21.60). PDH continuation trade won. PML breakdown hit 1R then BE'd out. Entry logic too simplistic — needs redesign |
| 2026-04-09 | v2.9 | Bullish | 6 | 1 | -$6.50 | Biggest win +$36.50 (PMH Breakout Long 2R). Proximity detection working. 3 setup types fired. Partial close working. PMH contested 90min before real breakout. |
| 2026-04-10 | v2.9.1 | Bullish | 4 | 0 | -$68.40 | Worst day. 4x ORL Bounce Long at same weak level, all SL. Casey's plan identified 6848 as key level — EA ignored it. Strategy redesign started. |
| 2026-04-13 | v3.1 | Bullish | 0 (EA) | 0 | $0.00 (EA) | EA took 0 trades — entry too rigid. Casey manual: +$21.50 (long from PDL/PMH/D-4H stacked zone). Plan was right, EA couldn't execute. |
| 2026-04-14 | v3.1.1 | Bullish | 0 (EA) | 0 | $0.00 (EA) | EA 0 trades again (restarts during session). Casey manual: +$26.70. Trade 2 was exactly PlanLong1=6918, rode to OR High for +$20.40. Trade management documented. |

---

## Next improvements planned

1. ~~**VPS setup**~~ ✅ MT5 running on VPS with Coinexx demo
2. ~~**Webhook pipeline**~~ ✅ Real-time events flowing to Railway API
3. ~~**Dashboard**~~ ✅ Live at mt5.freedomincomeoptions.com
4. ~~**Daily summary page**~~ ✅ Auto-generated at /summary
5. **Fix FixedLots** — change from 0.01 to 1.0 so trades actually execute (CRITICAL for tomorrow)
6. **Stop placement options** — test level-based stop vs candle-low stop vs ATR-based stop
7. **Multi-instrument** — add NQ100, Russell 2000
8. **Backtest** — run MT5 strategy tester over 2 years of data
9. **Volatility filter** — skip low-ATR days where breakouts fail more often
10. **GitHub auto-push** — nightly script pushes journals + daily logs to repo
11. **Improve stop logic** — consider ATR-based stops or level-based stops instead of candle low

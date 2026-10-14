### 2026-10-14 — MacroFX research: can a G8 FX system work long term?

**Agent:** Claude
**Model:** Claude Opus 5.5
**Requested by:** Casey — deep research on this system and on other FX systems that could succeed long term.
**Files:** `docs/research/LONG_TERM_FX_SYSTEMS.md` (report), `docs/research/notes/*.md` (5 cited research notes), `scripts/research_backtests.py` (new), `docs/backtest/research_results.json` (new), `macrofx_dashboard.py` + `static/macrofx_dashboard.html` (report rendered on the Backtest tab), `docs/MACROFX_UPGRADES.md` (#4 priority, #11 findings), `.gitignore`.

**Research (5 parallel research tracks: momentum, carry, value/combinations, post-2010 performance, retail implementation/data):**
- G10 currency momentum has a structural break around Aug 2001: Hutchinson et al. 2022 report a 2010–20 out-of-sample Sharpe of −0.68, and 123 variants averaged −0.42. AQR puts post-publication Sharpe at 0.08. Our −0.24 is consistent with this; it is not a bug.
- Carry paid before 2008. The DB G10 carry index never regained its 2007 peak through 2022, and the DBV ETF was liquidated in Mar 2023. Carry has revived in 2022–26.
- Value is the most durable style (AQR post-publication 0.69). The multi-style blend is the only construction with a defensible post-2010 record (Russell 3.4%/yr at 3.7% vol, 1999–2024).
- Retail swap fees (OANDA 1.00%, IG 0.5–0.8%) take one-third to one-half of a G10 premium.
- A $1,000 account cannot size these strategies; sizing becomes reasonable at about $10,000.

**Own tests** (`scripts/research_backtests.py`, H.10 + World Bank CPI from GitHub, spot-only, 2 bp/side):
- Spec 0: our exact v1.1 engine over 1975–1999 on 7 currencies earned +13.53%/yr, Sharpe +0.75, t +3.78. This confirms the harness.
- Academic 3m/1m momentum: Sharpe +0.56 over 1975–99, −0.12 over 2000–26, −0.54 over 2013–26.
- Value (−Δ60m real FX, CPI lagged 12 months): Sharpe +0.30, both halves positive (+0.34 / +0.25), max DD −21%.
- 12m trend: Sharpe +0.11. Value + trend: Sharpe +0.35, max DD −12%; 2013–26 only +0.13. This fails a 1% swap-fee net test (about 0.1–0.2 net Sharpe).
- Carry was not tested: no rate history is reachable from the sandbox (FRED, BIS and OECD are blocked; only GitHub raw is reachable).

**Recommendation recorded:**
- Retire momentum as a signal and keep the demo for infrastructure.
- EA should log MidasFX swaps and spreads.
- One-time off-sandbox fetch of rates and REER data.
- Backtest carry + value and dollar carry against pre-registered pass criteria.
- Real money only at $10,000+.

**No trading or strategy changes made.**
**Test fix:** 6 plan tests failed when run after 16:00 ET. Approving with "run at next window" correctly schedules for the next morning, but the tests assumed the window was open. They now set the plan due explicitly; window behaviour stays covered by `test_window_and_schedule`. The production code is unchanged. `pytest` 48/48 after hours.

### 2026-10-14 — MacroFX backtest results published on the dashboard

**Agent:** Claude
**Model:** Claude Opus 5.5
**Requested by:** Casey — "update logs and publish the results of your backtest in a new tab called backtest".
**Status:** The **Backtest** tab was already deployed to production with commit `a4fe8f5` (Dashboard deployment `4cdba5f1-5063-4d82-a8d4-9a9956c581f0`).
**Verified live 2026-10-14 ~19:25 UTC:**
- `/macrofx` shows the Backtest tab.
- `/api/macrofx/backtest` returns the 6 variants: weekday −7.5%/yr Sharpe −0.30; Sunday −24.9%/yr Sharpe −1.34; no costs −6.5%/yr Sharpe −0.24; buffer −7.2%/yr; stop −7.6%/yr; buffer+stop −7.1%/yr. Data 1999-01-04 to 2026-10-09, 1,397 rebalances.
- `/api/macrofx/doc/backtest` renders the report.
**Log fix:** the changelog entry for this work had no "MacroFX" in its title, so the dashboard's Changelog tab filtered it out. Retitled, and a dedicated "backtest published" changelog entry added.

### 2026-10-14 — Merged to main; Dashboard switched to main; executor live

**Agent:** Claude
**Model:** Claude Opus 5.5
- PR #2 marked ready and merged into `main` (merge commit `a4fe8f5`; branch head `4389084`). `main` had no other commits, so the merge was clean.
- Dashboard service source switched from the feature branch to `main` (follows the branch, not pinned). Deployment `4cdba5f1-5063-4d82-a8d4-9a9956c581f0` SUCCESS at 19:13 UTC. MacroFX Weekly (cron `0 1 * * 6`, already on `main`) rebuilt as `47cc606f-154a-41a9-b985-6db8dae58def` SUCCESS. It did not run outside its schedule (no deploy logs), so Friday's run will now save the full pair ranking.
- **Production check:**
  - `/macrofx`, `/api/macrofx/backtest`, `/api/macrofx/dashboard-data`, `/api/macrofx/health` and `/api/macrofx/v2/proposals` all return 200.
  - The executor built plan #1 for week ending 2026-10-09 by itself: **NO_CHANGES** (holds NZDUSD SHORT and EURAUD SHORT, matching targets; scheduled slot Mon 2026-10-12 04:00 ET).
  - Remote control stays off; 0 unresolved commands; EA v2.02 online; no executor errors in the logs.
- **Not done:** deleting the `macrofx-verify-runner` service was declined again. It is idle, and an older staged (uncommitted) patch on it remains; both are safe to leave or remove in the Railway dashboard. The drawdown kill switch is still untested on the terminal.
- **Next live event:** Friday 2026-10-16 ~9 PM ET weekly run → plan built automatically → needs Casey's approval on the This Week tab → runs Monday 2026-10-19 from 04:00 ET.

# EST Liquidity Breakout EA — Development Log

## 2026-10-08 — Permanent evidence-based agent reporting instructions

**Agent:** Adaptive
**Model:** openrouter/openai/gpt-6.1-sol
**Files changed:** AGENTS.md, DEV_LOG.md, changelog.md.
**Work completed:** Saved Casey's ten permanent reporting rules in AGENTS.md, including both source logs, actual agent/model separation, commit/PR and verification evidence, truthful deployment status, preserved continuity, and independent Roadmap task statuses.
**Verification:** Read existing logs and recent history; reviewed the documentation diff and `git diff --check`. No runtime code changed or application tests rerun. No recent historical backfill was supported by the review.
**Commit/PR:** This documentation changeset, based on 0613985.
**Deployment:** No deployment command executed; automatic deployment from a documentation push is unverified. No trading/risk setting, runtime code, or Roadmap change.

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
### 2026-10-14 — Weekly approval queue, Monday execution, complete records, backtest

**Agent:** Claude
**Model:** Claude Opus 5.5
**Requested by:** Casey — "do all 4": (1) approval queue + Monday execution + records, (2) backtest, (3) hold strategy changes, (4) housekeeping.
**Files:** `macrofx_proposals.py` (new), `macrofx_control_v2.py`, `macrofx.py`, `macrofx_engine.py` (`snapshot_from_factors` split out; identical maths), `macrofx_dashboard.py`, `static/macrofx_dashboard.html`, `main.py`, `scripts/backtest_macrofx.py` (new), `docs/backtest/results.json` + `REPORT.md` (new), `docs/MACROFX_RULES.md`, `docs/MACROFX_UPGRADES.md`, `tests/test_proposals.py` (new, 12 tests), `tests/conftest.py`, `tests/app_under_test.py`.

**1. Weekly plan → approval → Monday execution** (`macrofx_proposals.py`)
- An executor loop runs inside the Dashboard service (every 30 s, Postgres advisory lock, single runner). After each weekly run it builds a plan from the EA's latest position snapshot: closes first, then opens, 2-position cap. Status is NO_CHANGES when what's held already matches.
- Nothing trades until approved. Approve / Reject / Cancel / Rebuild are on the dashboard (This Week tab) and need `MACROFX_ADMIN_KEY`. The key is held only in page memory.
- Approved plans run from Monday 04:00 ET (DST-aware), only Mon–Fri 04:00–16:00 ET, one step at a time through the normal v2 command path (claim token, EA checks).
- Opens run with a 30-point spread cap; a spread block retries hourly, up to 8 times.
- A command not claimed within 5 min is cancelled and resent (up to 4 tries).
- Claimed but not acknowledged after 3 min → NEEDS_REVIEW; never retried. The same applies to `local_safety_block` and broker errors.
- Revalidated before every step: fresh heartbeat (≤3 min), demo, EA v2.x; closes skip tickets already closed; opens skip pairs already held. A position closed by hand is never reopened that week.
- Remote control is on only while a step is in flight and switched off at every terminal state.
- Older unstarted plans are superseded by a newer run; unapproved plans expire after 7 days.

**2. Complete records**
- Commands carry `signal_score`, `strategy_version`, `proposal_id`.
- On ACK the matching fill (posted by the EA just before the ack) is tagged; plan trades are labelled `target_open` / `target_removed`, so the analysis counts them as model trades.
- Weekly runs save the full 28-pair ranking (`pair_ranking_json`); this applies to the weekly service after the merge to main.

**3. Backtest** (`scripts/backtest_macrofx.py`)
- Data: Fed H.10 daily rates (datasets/exchange-rates on GitHub), 1999-01-04 to 2026-10-09, 28 crosses built from 7 USD rates.
- Uses the live engine functions. The live path (520 calendar days of closes) and the backtest path (factor slice) were verified identical to ~1e-14 on 3 dates, with identical targets.
- 1,397 weekly rebalances, 2000–2026; each position at 1× equity notional.
- Results:
  - v1.1 with weekday costs (1 pip/side): −7.5%/yr, Sharpe −0.30, max DD −89%, t −1.55.
  - Before costs: −6.5%/yr.
  - Sunday-reopen costs (20 pips/side): −24.9%/yr.
  - Rotation buffer 0.25: −7.2%/yr (trades 57 → 31/yr). Volatility stop 2×: −7.6%/yr.
  - Both halves negative (2000–12 −7.2%, 2013–26 −7.7%).
  - v1.1 beat 17% of 30 random-pair runs.
- Independent recomputation agrees (gross Sharpe −0.25). Single-horizon checks (1/3/6/12 months) all have Sharpe ≤ 0.
- Swap not modelled. Conclusion: **no evidence of an edge**; keep demo-only and research a different signal (Upgrades #11).

**Dashboard:** plan panel on This Week, new Backtest tab (growth-of-$1 log chart, variants, year by year, report).
**Verification:** `pytest` 48 passed / 0 failed. Twelve new tests run a simulated EA end to end: full rotation with approval, no approval no trades, wrong/missing key 403, outside window, before schedule, spread retry hourly with no immediate resend, claimed-but-unacked → NEEDS_REVIEW with no retry, manual close respected and not reopened, reject/cancel, stale EA blocks, public endpoint clean. Local render checked with Playwright.
**Holds (item 3):** no signal changes, size increase or live account; recorded in Upgrades #7/#8/#10/#11.

### 2026-10-14 — MacroFX Batch 2: terminal restart + network outage PASSED (17/17)

**Agent:** Claude
**Model:** Claude Opus 5.5
**Run:** `tests/live_restart_tests.py`, runner deployment `eec8e768-d8e1-490b-a111-7760abe331af` (redeploy of the `668de0b` build). Casey performed the terminal actions. An earlier attempt on 2026-10-13 timed out because no restart happened within the hour.
**Restart:** last heartbeat 17:46:32Z (MT4 closed). Runner enabled remote control with entries paused and queued PAUSE_ENTRIES `243c4554-cc6b-400d-9a15-98da9b7f0da9` at 17:48:14Z (expired 17:53:14Z). MT4 back online at 17:56:25Z. Over 3 poll cycles the expired command stayed PENDING and was never claimed; positions unchanged (EURAUD #8992699, NZDUSD #8992632); remote control restored to disabled.
**Network outage:** Casey disconnected the PC. Last heartbeat 18:03:25Z, next 18:11:25Z (480 s outage). The EA reconnected by itself; heartbeats and position snapshots resumed; positions unchanged; no commands created or executed.
**Correction:** In chat I first said heartbeats never stopped. That was a misread of an HTTP log window that ended at the outage start; the runner's own record shows the outage.
**Remaining untested on the terminal:** drawdown kill switch (needs Casey to change `MaxDrawdownPct`, or Upgrades #5). No orders were placed in this batch.

### 2026-10-14 — MacroFX dashboard: Feedback & analysis tab

**Agent:** Claude
**Model:** Claude Opus 5.5
**Requested by:** Casey — "what about feedback and analysis of the system".
**Files:** `macrofx_analysis.py` (new), `macrofx_dashboard.py`, `static/macrofx_dashboard.html`, `tests/test_macrofx_v2.py` (+3 tests).
**What it does:** New **Feedback** tab that evaluates the system from its own records on every page load:
- Sample-size gate: model-closed trades vs. 30 needed before judging the signal.
- Trades split by origin, **model** vs **test/manual**, so testing closes don't distort the signal's record.
- Execution cost by window (Sunday reopen vs weekday): average/max spread and estimated USD spread cost per fill, converted per quote currency from the latest closes, with a sanity guard against bad prices.
- Cost breakdown (price P&L, swap, commission, net, estimated spread inside P&L); week-to-week target turnover; max daily drawdown.
- Generated findings (Problem / Watch / Note) with evidence; the four research questions from the weekly review, with data-readiness status; the latest official weekly review rendered in full.
**Verification:** `pytest` 36 passed / 0 failed (+3: spread-cost conversion incl. JPY/CHF/AUD quotes and bad-price guard, ET Sunday window, model-vs-test split + turnover + findings). Local render checked with Playwright. Against realistic prices the estimate gives $12.91 spread over 6 Sunday-reopen fills vs $0.24 over 4 weekday fills, in line with the earlier manual estimate (~$12).
**Deployment:** Dashboard `d2a9739e-23bd-420d-a918-d298ab6b16ea`, live ~2026-10-14 17:25 UTC. Production analysis: 3 model trades (net −$5.75, PF 0.50) vs 5 closed overall (+$4.41); Sunday reopen avg spread 228 pts vs 7 weekday (31×), est. $12.85 vs $0.24; average target change 1.5 of 2 per week; closed trades gave back $6.10 on average from their best point (model trades: AUDCHF +1.65→−11.06, EURJPY +12.93→+5.85, USDCHF +5.72→−0.54).
**No writes, no commands, no strategy changes.**

### 2026-10-14 — MacroFX dashboard (/macrofx)

**Agent:** Claude
**Model:** Claude Opus 5.5
**Requested by:** Casey — dashboard in the Railway service tracking history, status, upcoming weekly trades and swap, the changelog, potential upgrades, and plain-language rules.
**Files:** `macrofx_dashboard.py` (new), `static/macrofx_dashboard.html` (new), `docs/MACROFX_RULES.md` (new), `docs/MACROFX_UPGRADES.md` (new), `main.py` (router registered), `requirements.txt` (+`markdown==3.7`), `tests/app_under_test.py`, `tests/test_macrofx_v2.py` (+5 tests), `tests/export_feedback.py` (read-only history export, not run), `.gitignore`.
**What it does:** Read-only page at `/macrofx` with six tabs:
- **Overview:** EA status, balance/equity, since-start P&L, swap, open positions with swap per day, daily equity chart.
- **This Week:** current targets, targets vs held (close/open/hold), next run time, a live "if the model ran now" ranking, and the last official currency ranking.
- **History:** trades with MAE/MFE, weekly runs, fills, remote commands.
- **How It Works:** rules. **Changelog:** MacroFX sections of `changelog.md` and `DEV_LOG.md`. **Upgrades:** proposed upgrade list.

Data API: `GET /api/macrofx/dashboard-data`. Docs: `GET /api/macrofx/doc/{rules|upgrades|changelog|devlog}` (markdown, or `?format=html`). No writes, no commands, claim tokens never returned. Markdown is rendered server-side, so the page has no script CDN dependency.
**Verification:** `pytest` 33 passed / 0 failed (28 existing + 5 dashboard: page/data keys, no claim tokens, docs + path safety, read-only, next-run schedule). Local render checked with Playwright in light, dark and 390px mobile against seeded data; fixed realized-commission double count, chart label overlap and log list rendering found in those checks.
**Deployment:** Dashboard deployment `22e7b502-27a1-4842-aba3-857f1ddb274a` (commit `7413025`) live 2026-10-14 ~17:06 UTC. Production check: `/macrofx` 200, data API 200 with real account data (EA v2.02 online, 2 positions matching week-ending-10-09 targets, 7 trades, 12 fills, 3 weekly runs, 19 equity days), no claim tokens in output; EA heartbeat endpoint still 200.
**Access note:** The page is public and read-only, like the existing `/` dashboard and `/api/macrofx/status`. It shows the demo account's balance and positions. Add a password if that should change.
**Not done:** Swap *rates* (expected nightly swap) need the EA to upload them (Upgrades #4); the dashboard currently shows swap already charged. Weekly target execution is still manual (Upgrades #1).

### 2026-10-13 — MacroFX Batch 1: EA entry guards on the real terminal PASSED (14/14)

**Agent:** Claude
**Model:** Claude Opus 5.5
**Authorization:** Casey 15:31 ET. Runner deployment `0def482b-ee28-4926-8d02-361974054388` (commit `b1a93b1`, `tests/live_guard_tests.py`). An earlier deployment `9c5ddf48…` stalled in Railway's builder and was removed without running.
| Step | Command | Result |
|---|---|---|
| Free slot: close EURAUD SHORT #8950352 | `2dd9868a-9ccf-45a2-b827-9b4e0f47774e` | ACKED `closed` — fill 1.60348, spread 9, slip 0, P&L +11.21, comm -0.06 |
| Open EURAUD while paused | `0f9677a3-6008-4592-b2e4-7a6a2fe098c0` | FAILED `entries_paused` |
| Open EURAUD with spread limit 0 | `cf083b3b-e5b8-4239-ae4e-404bb8788b33` | FAILED `spread_or_quote_block` |
| Duplicate NZDUSD open (slot free) | `cb47cbae-5703-4a10-8a78-fdce1b51c4fa` | FAILED `pair_already_open` |
| Unknown symbol ABCDEF | `1b69568d-75cd-4559-9e8d-c138853161eb` | FAILED `pair_or_lot_limit` |
| Restore EURAUD SHORT 0.01 | `db1f6c03-4159-4e8a-b29b-b2a5489ecd17` | ACKED `opened_ticket_8992699` — fill 1.6036, spread 7, slip 1, comm -0.06 |
**Positions after:** EURAUD SHORT 0.01 #8992699, NZDUSD SHORT 0.01 #8992632 (bridge-owned, match week 7). Remote control restored to disabled; nothing left CLAIMED.
**Still untested:** broker lot-step rejection (server allows only 0.01, so unreachable remotely), drawdown kill switch, restart, network outage.

### 2026-10-13 — MacroFX Phase D demo execution PASSED (22/22)

**Agent:** Claude
**Model:** Claude Opus 5.5
**Authorization:** Casey 14:58 ET; EA input `EnableTrading=true` set by Casey 15:13 ET.
**Run:** `tests/live_demo_trade.py`, runner deployment `93f273da-a5bd-479e-8445-ee0170562410` (redeploy of commit `b280833`). Demo account 1041307, EA v2.02.
| Step | Command | Claimed / Acked (UTC) | Result | Broker fill |
|---|---|---|---|---|
| Close NZDUSD SHORT #8984249 | `c65a4e33-b217-41e7-9f9f-c4bd54fc310e` CLOSE_TICKET | 19:16:34.77 / 19:16:35.09 | ACKED `closed` | 0.56148 req/fill, spread 7 pts, slip 0, P&L -1.13, comm -0.03 |
| Reopen NZDUSD SHORT 0.01 | `fc9f8ab7-039a-42d6-a39a-440f29a28367` OPEN_SHORT | 19:18:34.74 / 19:18:35.04 | ACKED `opened_ticket_8992632` | 0.56136 req/fill, spread 6 pts, slip 0, comm -0.03 |
| Duplicate open NZDUSD | `5ae538f7-7e66-4989-aaae-7b2a704e27cc` OPEN_SHORT | 19:20:34.79 / 19:20:34.84 | FAILED `position_limit` | none |
Railway snapshot confirmed close (ticket absent), new ticket 8992632 NZDUSD SHORT 0.01 magic 26092601, and exactly 2 bridge positions after the duplicate attempt. Both fills stored in `macrofx_fills`. Re-claim of executed commands rejected (409). Remote control restored to disabled; no command left CLAIMED.
**Open demo positions now:** NZDUSD SHORT 0.01 #8992632, EURAUD SHORT 0.01 #8950352 (week 7 targets, matching). No unintended test positions.
**Limits of this evidence:** the duplicate was stopped by the position limit; the separate pair-already-open guard was not reached. Spread/lot-step rejection, drawdown kill switch, restart and network-outage behavior remain code-reviewed only. EA `EnableTrading` is now ON (it only acts on claimed remote commands; remote control is disabled). Branch not merged.

### 2026-10-13 — MacroFX Phase D attempt 1: blocked by EA local safety (expected)

**Agent:** Claude
**Model:** Claude Opus 5.5
**Authorization:** Casey, 14:58 ET: "lets just test it now" (close one bridge position, reopen same pair/direction at 0.01, test duplicate-open guard).
**Run:** `tests/live_demo_trade.py`, runner deployment `acc18125-c49c-4c77-be2c-ee55974c560c`, commit `b280833`.
**Result:** CLOSE_TICKET `5d65da8f-30e1-42b9-8ad6-c4d7b4bfffca` for NZDUSD #8984249 was claimed by the terminal (19:00:54Z) and acknowledged `FAILED` / `local_safety_block`. This is the EA refusing because the local `EnableTrading` input is OFF (or the drawdown kill switch; heartbeat equity 1004.39 vs balance 994.25 makes the kill switch unlikely). The script aborted before any open; remote control restored to disabled; no command left CLAIMED. **No orders placed or closed.**
**Evidence gained:** trading-disabled-by-default enforcement verified on the real terminal for a CLOSE command.
**Next:** Casey sets EA input `EnableTrading=true`; rerun the same script. Note: `EnableTrading=true` alone does nothing — v2.02 executes only claimed remote commands, and remote control is disabled.

### 2026-10-13 — MacroFX v2.02 real-terminal PAUSE_ENTRIES lifecycle verified

**Agent:** Claude
**Model:** Claude Opus 5.5
**Files changed:** `tests/live_real_pause.py` (new), `DEV_LOG.md`, `changelog.md`.
**Precondition:** Casey compiled and attached EA v2.02; heartbeat 18:46:59Z shows `MacroFX-MT4-Bridge-2.02-claimtoken`, demo, account 1041307.
**Test:** Run inside Railway (`macrofx-verify-runner`, deployment `252894a7-285f-4a86-89f1-4f95e25f4cbf`, commit `11e48f5`). Remote control enabled with `pause_entries=TRUE` for the whole test; only a PAUSE_ENTRIES command created; settings restored afterwards.
**Result: 13 passed / 0 failed.** Command `b861cb57-71c1-42ef-b547-e40e24dbbc9c` created 18:49:04Z, claimed by the MT4 terminal 18:49:54Z (HTTP 200, UA MetaTrader 4 Terminal/4.1492), acked 45 ms later with `ACKED`/`paused`. Not redelivered; duplicate claim 409; foreign-token ack 409; stored result unchanged. Railway HTTP logs show exactly one EA claim and one EA ack. Final state: no v2 settings row (remote control disabled by default), 0 unresolved commands.
**Incident (no impact):** Railway created two deployments of the runner (`241a13a3-2d64-4d89-b207-7ff06b31357d` and `252894a7`). The second instance aborted at its "no unresolved commands" guard and did not create a command or cancel the first run's command; its restore wrote identical settings. Lesson: the pre-test guard is required for any runner that writes to the real account.
**Not done:** No orders placed or closed. Phase D still needs explicit authorization and a free position slot (account holds 2 of 2: NZDUSD #8984249, EURAUD #8950352). EA-side spread/lot-step/drawdown/restart checks still code-reviewed only.

### 2026-10-13 — MacroFX v2.02 verification, fixes and production backend deploy

**Agent:** Claude
**Model:** Claude Opus 5.5
**Files changed:** `macrofx_control_v2.py`, `mt4/FIO_MacroFX_Bridge_v2_0.mq4`, `mt4/FIO_MacroFX_Bridge_v2.mq4` (identical), `tests/conftest.py`, `tests/app_under_test.py`, `tests/test_macrofx_v2.py`, `tests/live_runner.py`, `pytest.ini`, `DEV_LOG.md`, `changelog.md`.

**Bugs found**
1. Ack had no claimant check: any instance with the EA key could ACK/FAIL a CLAIMED command (second chart could overwrite the first claimant's result). Server-side gap behind v2.01's EA-only fix.
2. EA processed `PAUSE_ENTRIES` *after* the `EnableTrading`/kill-switch gate, so pause returned `local_safety_block` whenever trading was OFF (handoff issue C, confirmed). Pause also only lived in memory until the next poll overwrote it.
3. No duplicate guard: multiple pending `OPEN_*` for the same pair (or `CLOSE_TICKET` for the same ticket) could be queued.
4. `reconcile-preview` raised 500 if `macrofx_v2_position_snapshots` did not exist yet (table only created by the positions upload).
5. v2 schema (including DROP/ADD CONSTRAINT) re-ran on every request, taking an ACCESS EXCLUSIVE lock on the command table on every EA poll. Not a correctness failure in tests, but unnecessary locking.

**Fixes**
- `/claim` returns a 32-hex `claim_token`; `/ack` requires the matching token. Token never returned in admin history.
- Creating `PAUSE_ENTRIES` latches `pause_entries=TRUE` in settings (revision+1) immediately — fail-safe direction.
- Duplicate pending/in-flight OPEN per pair and CLOSE per ticket rejected with 409, serialized by a per-account advisory lock.
- Snapshot table created in v2 schema; schema applied once per process; constraint migration idempotent. Migration from the deployed schema tested: existing rows preserved.
- EA v2.02: pause handled before trading gate (still demo-only); parses `claim_token`, sends it on ack; marker still written before execution; skips execution if token missing. Version `MacroFX-MT4-Bridge-2.02-claimtoken`.

**Tests executed**
- `python3 -m pytest -q` (isolated local PostgreSQL 16, throwaway keys). Baseline on deployed code `5c6215c`: 21 passed / 5 failed. After fixes: **28 passed / 0 failed** (auth, demo-only, stale heartbeat, defaults, validation, lifecycle, duplicate claim, 12-way concurrent claim, expiry, invalid/second-chart acks, uncertain-outcome no-redelivery, duplicate-open race, reconcile preview incl. suffixes/direction/size/magic/manual-close/duplicates/stale targets).
- Production, authenticated, run inside Railway (`tests/live_runner.py`, service `macrofx-verify-runner` 11134cbb-ed0d-497d-b30a-f6a6dadeaa4c, deployment aadca9d8-83c5-46fc-ae29-14cb333f3855): **43 passed / 0 failed**. Write tests used synthetic account `CLAUDE-TEST-1791916862`; all synthetic rows deleted (0 remaining). Real account 1041307 read-only.

**Deployment:** Dashboard deployment `c2bfad9a-3457-4533-915d-519c5de715cb` (commit `05a023f`) SUCCESS 2026-10-13T18:36Z. Post-deploy EA traffic (heartbeat, positions-csv, control-text) HTTP 200 from MT4 4.1492.

**Production state observed (read-only):** 1041307 demo, EA still v2.01 (heartbeat age 31s). No v2 settings row → remote control disabled by default. 0 unresolved commands. Two bridge-owned positions open: NZDUSD SHORT 0.01 #8984249, EURAUD SHORT 0.01 #8950352; reconcile preview (weekly run 7) shows them matching targets — no close/open candidates.

**Not verified / blockers**
- EA v2.02 not compiled (no MetaEditor here) and not installed. Real-EA receipt/claim/ack (Phase B 3–5 with the terminal) requires Casey to compile and attach v2.02. The running v2.01 cannot ack under the new server (no token) — harmless while remote control is disabled.
- Phase C EA-side controls (spread/slippage, lot step, drawdown kill, restart/network outage) are code-reviewed only, not executed.
- Phase D not run: no authorization given, and account is already at the 2-position limit, so a new 0.01 test order would be blocked by design.
- Weekly target → v2 command execution is not integrated (preview only), as intended.
- No demo orders placed. No positions opened or closed. Branch not merged.
- `macrofx-verify-runner` service left in place (deletion not approved); it is idle. Redeploying it reruns the suite.

### 2026-10-13 — MacroFX v2.01 command ACK race fix
Agent: ChatGPT. Updated both MT4 EA source variants to avoid ACKing a command already marked attempted by another chart; only successful claim owner proceeds. Bumped About version to 2.01 and heartbeat version to MacroFX-MT4-Bridge-2.01-claimfix. Source committed on development branch; MT4 compilation, local installation and broker demo command execution remain unverified. No live trades initiated.

# EST Liquidity Breakout EA — Development Log

## 2026-10-13 — MacroFX v2 compile-error corrections

**Agent:** ChatGPT (GPT-6)
**Evidence:** User MetaEditor screenshot reported six errors, including undeclared `spreadPoints` and invalid newline parsing. Fixed source ordering and newline delimiter in `mt4/FIO_MacroFX_Bridge_v2.mq4` (commit `4bc7853`).
**Verification:** Static source inspection only; awaiting fresh MetaEditor compile output. **Deployment:** None; existing EA unchanged.

## 2026-10-12 — MacroFX Bridge v2 EA implementation

**Agent:** ChatGPT (GPT-6)
**Files:** `mt4/FIO_MacroFX_Bridge_v2.mq4`, `macrofx_control_v2.py`, `DEV_LOG.md`, `changelog.md`.
**Implemented:** Separate v2 MT4 source with Railway remote settings/commands, broker execution and fill reporting, hard demo and local risk limits, durable marker written before each command attempt, and MT4-compatible acknowledgement endpoint. v2 weekly target reconciliation disabled pending manual-override precedence design.
**Evidence:** GitHub commits `4c0f555`, `6e135a6`, `43106dc`; draft PR #2.
**Verification:** Source committed; no MetaEditor compile, integration tests or demo broker verification. Duplicate safety is fail-closed but uncertain broker outcomes need manual review.
**Deployment:** None. Production v1.5 unchanged.
**Status:** IN PROGRESS — not production-ready.

## 2026-10-12 — MacroFX Bridge v2 development

**Agent:** ChatGPT (GPT-6)
**Status:** IN PROGRESS; not merged or deployed.
**Files:** `macrofx_control_v2.py`, `main.py`, `changelog.md`, `DEV_LOG.md`.
**Completed:** Added demo-only Railway control endpoints, disabled-by-default remote settings, expiring manual command queue, acknowledgements, and separate administrator authentication. Registered router in the FastAPI application.
**Commits:** `95f9a28`, `2e3648d`, `28899fc`; draft PR #2: https://github.com/caseystubbs/mt5-trading-/pull/2.
**Verification:** Repository source reviewed; GitHub commits confirmed. No automated integration tests, MT4 compilation, broker validation or deployment performed.
**Outstanding:** MT4 v2 execution agent, crash-safe deduplication, manual override precedence, integration tests, demo validation and deployment checklist.
**Trading:** Existing weekly strategy, EA v1.5 and production settings unchanged.

## 2026-10-08 — Permanent evidence-based agent reporting instructions

**Agent:** Adaptive
**Model:** openrouter/openai/gpt-6.1-sol
**Files changed:** AGENTS.md, DEV_LOG.md, changelog.md.
**Work completed:** Saved Casey's ten permanent reporting rules in AGENTS.md, including both source logs, actual agent/model separation, commit/PR and verification evidence, truthful deployment status, preserved continuity, and independent Roadmap task statuses.
**Verification:** Read existing logs and recent history; reviewed the documentation diff and `git diff --check`. No runtime code changed or application tests rerun. No recent historical backfill was supported by the review.
**Commit/PR:** This documentation changeset, based on 0613985.
**Deployment:** No deployment command executed; automatic deployment from a documentation push is unverified. No trading/risk setting, runtime code, or Roadmap change.

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

### 2026-10-13 — MacroFX v2 weekly-execution safety audit (not enabled)

**Agent:** ChatGPT
**Verified:** Railway Dashboard v2 commit dfbf76d deployed SUCCESS; MT4 demo heartbeats, position uploads and v2 control polls returned HTTP 200 repeatedly through 14:34 UTC. MacroFX Weekly service remains on main and the 2026-10-09 scheduled run produced SHORT EURAUD and SHORT NZDUSD at 0.01 lot each.
**Execution evidence limit:** HTTP 200 on positions-csv confirms uploads, NOT the individual live broker positions; latest account position rows and broker tickets were not independently read. No v2 /fill requests appeared in the checked recent HTTP window.
**Blocking defects:** (1) MT4 v2 OnTimer intentionally does not call PollTargets, so Friday signals do not currently drive Sunday execution; (2) multiple MT4 chart instances poll the same pending commands, while GlobalVariableCheck followed by GlobalVariableSet is not atomic; (3) remote settings remain disabled/paused, and no admin key is configured on the Dashboard; (4) changed MT4 source requires local MetaEditor compilation and demo broker tests before use.
**Decision:** Keep remote execution disabled; do not claim completed weekly reconciliation, command execution, or end-to-end validation. Implement server-side single-consumer command claiming and durable target-to-command reconciliation with manual-close precedence; verify actual positions and broker fills, then perform demo-only pause/open/close/restart tests. Do not change weekly signal logic or 2-position/0.01-lot caps.

### 2026-10-13 — v2 single-consumer claim and reconciliation preview (source only)

**Agent:** ChatGPT. **Branch:** feature/macrofx-bridge-v2-remote-control (draft PR #2). **No new Railway deployment and no broker actions.**
- Added PostgreSQL atomic PENDING→CLAIMED command transition; ACK now requires CLAIMED, and uncertain claimed commands are not automatically retried. The MT4 v2 source now requires HTTP 200 from /api/macrofx/v2/claim before a broker action, protecting against multiple chart instances consuming one instruction.
- Persisted a full latest-position snapshot on every EA position upload, including empty snapshots, so a future reconciliation does not mistake historical positions for currently open trades.
- Added authenticated read-only /api/macrofx/v2/admin/reconcile-preview using a fresh (<2 minute) snapshot and current weekly targets, with close-before-open ordering and explicit operator review to preserve manual-close precedence.
- **Not yet complete:** no automated Sunday reconciliation scheduler, no enqueue/apply step, no broker position verification, no Python integration tests, no MetaEditor compile of updated EA, and no demo execution tests. Trading stays disabled/paused. The live Dashboard remains pinned to dfbf76d, not these branch commits. EA source changes require manual recompile and reinstall.

### 2026-10-13 — Deployment request: MacroFX v2 safety backend

**Agent:** ChatGPT (GPT-6). Requested Railway Dashboard deployment of source changes: atomic PENDING→CLAIMED server command lock, latest complete position snapshots, and read-only weekly reconciliation preview. Deployment is limited to the Dashboard service on the v2 feature branch; weekly strategy service and MT4 installed binary are unchanged. Trading remains disabled/paused by default, with no MACROFX_ADMIN_KEY configured. Nine unrelated staged Railway changes (including service deletion) must NOT be accepted. Runtime deployment and HTTP checks recorded in a subsequent entry.

**Deployment evidence update (2026-10-13):** Railway Dashboard deployment ID `3d473bbe-8eeb-41ec-8e27-7012b9f5f246` was created for pinned commit `5f6bca4f20ffb555b90b0695626d09b20e40eaae`; Railway reported BUILDING at the last check, not SUCCESS. Prior `dfbf76d` deployment was still SUCCESS. No new-code runtime HTTP verification yet. Do not claim deployment completed until SUCCESS and endpoint checks.

### 2026-10-13 — Production 500 migration hotfix

**Agent:** ChatGPT (GPT-6). After deployment 3d473bbe reported SUCCESS, observed HTTP 500 on `/api/macrofx/v2/control-text` while heartbeat and positions-csv remained HTTP 200. Railway runtime traceback: `asyncpg.exceptions.PostgresSyntaxError: syntax error at or near "$"` in `macrofx_control_v2.py` SCHEMA. Replaced invalid `DO $ ... END $;` with standard PostgreSQL constraint DROP IF EXISTS / ADD statements; verified updated source blob SHA 891eda84. Hotfix commit `a16ac2fdaf666417b6c4e6314e6ada3be896c651` submitted to Railway Dashboard as pinned source, deployment `2b6e52f6-78be-4965-92f3-3b7499d2a100`. Verification of success and HTTP 200 still pending. Automatic trading remains disabled; MT4 binary unchanged.

### 2026-10-13 — Production hotfix verified

**Agent:** ChatGPT (GPT-6). Railway Dashboard deployment `2b6e52f6-78be-4965-92f3-3b7499d2a100` (commit `a16ac2fdaf666417b6c4e6314e6ada3be896c651`) reported SUCCESS at 15:09:14 UTC. HTTP logs after rollout through 15:13:13 UTC show repeated 200 responses for `/api/macrofx/heartbeat`, `/api/macrofx/positions-csv`, and `/api/macrofx/v2/control-text`. Earlier 500 errors occurred before rollout. SQL migration outage resolved. This verifies connectivity, not broker execution; remote trading remains disabled pending EA compilation and demo trade tests.

### 2026-10-13 — MT4 EA visible version label

**Agent:** ChatGPT (GPT-6). Added MQL4 `#property version "2.0"` and About-tab description to `mt4/FIO_MacroFX_Bridge_v2.mq4` (commit `d72faee`). Created a version-labeled copy `mt4/FIO_MacroFX_Bridge_v2_0.mq4` (commit `de586fe`) so the EA filename itself displays v2_0 in the MT4 expert properties title. Not compiled or installed; no backend redeployment and no trading actions.

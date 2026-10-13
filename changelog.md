## 2026-10-13 — MacroFX v2 MetaEditor compile fixes

**Agent:** ChatGPT (GPT-6). Corrected use of `spreadPoints` before declaration and replaced invalid newline delimiter in `StringSplit` with integer character code 10. Commit `4bc7853`. User screenshot reported 6 compiler errors; fresh compilation and zero-error confirmation are pending. Development branch only; no deployment.

## 2026-10-12 — MacroFX MT4 Bridge v2 source

**Agent:** ChatGPT (GPT-6). Added `mt4/FIO_MacroFX_Bridge_v2.mq4` with Railway v2 polling, remote open/close/pause command handling, hard demo/local risk checks, persistent pre-execution deduplication marker and authenticated command acknowledgement. Adapted `macrofx_control_v2.py` acknowledgement endpoint for MT4 query parameters. Disabled v2 weekly auto-reconciliation pending explicit override semantics so remote closes are not immediately undone. Commits `4c0f555`, `6e135a6`, `43106dc`. **Not compiled, tested, merged or deployed.** Manual review required for uncertain command outcomes. Existing EA v1.5 remains untouched.

## 2026-10-12

### [wip] MacroFX Bridge v2 Railway control foundation

**Agent:** ChatGPT (GPT-6)
**Changes:** Added `macrofx_control_v2.py` and registered its router in `main.py` on the development branch. The new API provides demo-only remote settings, an expiring command queue, acknowledgements and a separate admin key. Existing MT4 v1.5 and strategy rules were not modified.
**Evidence:** Commits `95f9a28` and `2e3648d`; draft PR #2.
**Verification:** GitHub commits verified; no automated tests, MetaEditor compilation or demo execution yet.
**Deployment:** Not merged or deployed. No broker orders or production configuration changes.
**Remaining:** MT4 v2 client, deduplication, override reconciliation, tests and demo validation.

## 2026-10-08

### [docs] Persist evidence-based agent reporting rules
Saved the permanent reporting contract in AGENTS.md, including both source logs, actual agent/model attribution, commit/PR and verification evidence, truthful deployment status, unique backfills, and independent Roadmap task statuses.
**Agent:** Adaptive
**Model:** openrouter/openai/gpt-6.1-sol
**Files:** AGENTS.md, DEV_LOG.md, changelog.md.
**Verification:** Documentation diff reviewed; `git diff --check` passed. No speculative historical backfill.
**Commit/PR:** This documentation changeset, based on 0613985.
**Status:** Documentation complete; no deployment command executed. Automatic deployment from a documentation push is unverified. No trading operation.

## 2026-04-15

### [fix] ea_version VARCHAR(10) → VARCHAR(100) in trade_events and daily_summaries

EA version string "3.1.2 | Plan: Apr 15" exceeded the 10-character column limit, causing 500 errors on every webhook POST all day. Fixed by ALTER TABLE on both tables via Codespaces + asyncpg. main.py CREATE TABLE statements patched to VARCHAR(100) so fix persists on redeploy.

### [fix] Premarket log spam — 34,000+ identical lines per session

CalculatePremarketLevels() was logging "Premarket ready" on every tick after finalization due to inverted throttle logic. Fixed: now logs once when first ready, once more when finalized at 9:29 EST, silent after that.

### [feature] Timezone diagnostic block in OnInit()

Added detailed startup diagnostic printing GMT, broker, and EST times, EDT/EST mode, entry window status, force close status, and broker GMT offset. Helps diagnose timezone issues without guessing.

### [session] Day 9 — Apr 15 — Plan A+, EA 0 trades (technical failures)

Plan was perfect — PMH at 6983 and PML at 6961.8 were the exact session pivots. Price broke above PMH and ran 84 points to 7045+. Hypothetical PMH breakout long would have been +$240–$480, the largest single-day result in system history. EA missed due to: (1) VARCHAR bug causing 500 errors all morning, (2) EA confirmed running at 10:34 EST after price already through 6983.

---

## 2026-04-14

### [deploy] EA v3.1.1 — flexible entry logic, live PM levels, wider historical scan

Entry logic rewritten: removed strong close filter, simplified to zone proximity + directional candle. PM levels now update live from 4:00 AM (not waiting until 9:29). Historical scan expanded to 20 days / $100 proximity. Debug prints added for historical level diagnosis. Password removed from plan page save.

### [fix] Historical levels now showing on chart

Fixed proximity filter ($50 was too tight, levels at $60+ distance were filtered out). Increased to $100. Debug prints confirmed levels are being found. Legend now shows D-2 H, D-3 H, D-3 L, D-4 H with prices.

### [wip] EA still not triggering entries — third consecutive day

Casey's plan identified 6918 as the key level. Casey manually traded exactly at 6918 for +$20.40 on MidasFX. EA had the same level programmed but took zero trades. Entry logic or plan level loading issue — needs debug prints on candle evaluation to diagnose.

### [docs] Casey's trade management style documented

From journal analysis: stop at nearest key level (not fixed buffer), target at next key level, trail stop in stages (near BE → plan level → let TP hit), 3:1 R:R on main trade. Level-to-level trading with active management.

### [feature] Live status line on chart (top-left)

Single line showing what EA is doing at all times: waiting for session, scanning with nearest plan levels and distance, managing trade with live P&L/stop/target, or session over. Updates every tick. Shows "NO PLAN LEVELS SET" if inputs are empty.

### [fix] Entry window starts at 9:30 EST (was 9:45)

Casey's main trade today was at 9:36 AM — PMH broke before OR was complete. The 15-minute wait for OR to form was preventing trades. OR range still shaded on chart for reference but EA can now trade from market open.

### [docs] Historical levels D-3 H and D-2 H respected perfectly

Price bounced off both D-3 H and D-2 H during today's session — validates that historical daily levels are real support/resistance. These should be included in daily plans as bounce/rejection zones.

## 2026-04-13

### [deploy] EA v3.1 — clean build, plan-driven only

Stripped EA down to essentials: level identification (PDH, PDL, PMH, PML, ORH, ORL, D2-D10 historical) + plan-based trading. Removed 412 lines of dead code, 15 unused inputs, old setup detection system, and top-left status panel. Chart is clean — just levels and the legend.

### [feature] Auto-populated levels on daily plan page

Plan page now pulls levels automatically from EA's DAILY_OPEN webhook event. No more typing PDH/PDL/PM/OR prices manually. Refresh button updates levels after 9:30 when PM and OR are calculated.

### [wip] Casey's plan was right, EA missed the trade

Plan identified PDL (6811.5) as the key level. Price broke above PDL and rallied 25 points. EA took zero trades — entry detection too rigid. Casey manually traded +$21.50 on the same levels. Entry logic needs to be more flexible.

## 2026-04-10

### [wip] Strategy redesign — daily plan driven trading

Major strategy shift: EA should follow a daily plan instead of trading every level it sees. Casey's manual plan identified 6848 as the decision level and 6812 as key support. EA ignored both and took 4 ORL bounce longs that all lost. Building toward AI-generated plans and plan-aware EA.

### [wip] Historical levels identification planned

EA currently only looks at yesterday's PDH/PDL. Need to scan back 5-20 days for significant swing highs/lows near current price. These are levels big money trades off of.

### [fix] Identified level hierarchy problem

Not all levels are equal. PDH/PDL and PML/PMH are the heavy levels. OR levels are minor. EA treated them all the same — resulted in 4 trades at a weak ORL level while major levels were ignored.

## 2026-04-09

### [feature] Daily plan page for pre-market preparation

New /plan tab on the dashboard. Fill out market bias, key levels, setups to watch, invalidation conditions, and stop plan before market open each morning. Saves to database with date navigation.

### [feature] Premarket and opening range shading on chart

Premarket range (4:00-9:29 EST) shaded in dark teal. Opening range (first 15 min) shaded in dark yellow. Makes session boundaries visually clear on the M5 chart.

### [fix] P&L now shows real dollar amounts

Dashboard was showing price distance instead of actual dollar P&L. Fixed — EA now calculates lots x tick value for accurate reporting. With 2 lots, a 10-point move = $20, not $10.

### [deploy] Biggest single trade win: +$36.50

Trade #6 PMH Breakout Long hit 2R target after price tested PM High four times and consolidated at OR Low. Partial close worked correctly — 1 lot at 1R, remaining lot rode to 2R.

### [wip] No-BE tracking producing early results

Three trades tracked so far. Breakeven cost approximately $12.60 across two trades that would have been winners without it. Gathering more data before making changes.

## 2026-04-08

### [deploy] First 2R target hit — system works end to end

EA executed 7 trades, hit first ever 2R target for +$21.60. Full pipeline working: EA detects setup → executes trade → manages position → hits target → logs to Railway API → shows on dashboard.

### [feature] Navigation tabs on dashboard

Dashboard and daily summary pages now have tab navigation to switch between views.

### [wip] Trading logic redesign in progress

Major strategy review after today's session. Current "strong candle above level = buy" logic is too simplistic. Building toward liquidity-based framework: PDH/PDL breakout campaigns, consolidation patterns, bounce/breakout triggers at PM and OR levels.

## 2026-04-07

### [feature] Auto-generated daily summary page

New /summary page generates a complete daily trading report with grade, analysis, trade details, and event timeline. Navigate between days at mt5.freedomincomeoptions.com/summary.

### [fix] Daily log API no longer returns "Not Found"

Events stored in UTC were not matching EST date queries. Fixed date lookup to handle timezone offset.

### [wip] First full day on VPS with webhook pipeline

EA found 7 valid SHORT setups on PDL breakdown but all rejected — FixedLots was 0.01 instead of broker minimum 1.0. Config fix pending for tomorrow.

### [deploy] Custom domain live at mt5.freedomincomeoptions.com

Trade journal dashboard accessible at mt5.freedomincomeoptions.com with SSL.

## 2026-04-06

### [feature] Real-time trade dashboard live on Railway

EA now sends every trade event to a live dashboard you can check from your phone. Shows today's trades, P&L, win rate, and daily history.

Dashboard: https://mt5.freedomincomeoptions.com/

### [feature] Automatic pattern tracking

API tracks win rate by level (PDH vs OR High vs PM High), by direction, by trend alignment, and by candle strength. Patterns accumulate over time to guide system improvements.

### [deploy] Trade journal API deployed to Railway

FastAPI + PostgreSQL backend receives trade events via webhook, stores history, generates daily markdown reports, and serves the dashboard.

## 2026-04-03

### [fix] OneTradePerDay now actually works

EA was taking unlimited trades per day because the trade-taken flag wasn't set when the broker closed positions at stop loss. Fixed — flag is now set in all close paths.

### [fix] Trade journal no longer reports fake P&L

Journal was calculating P&L against stale entry prices from previous trades. Now reads actual close price and reason from broker deal history.

### [feature] Broker-side stop loss detection

EA now detects when the broker closes a position at SL/TP and logs the real result instead of missing it entirely.

## 2026-04-02

### [feature] CSV trade journal system

EA writes daily journal files tracking every setup found, rejected, trade opened, and trade closed. Files saved to MQL5/Files/ for daily review.

## 2026-04-01

### [fix] Settings now use price values instead of broker points

MinimumBreakout and MaximumStop settings switched from MT5 points to actual dollar values. EA works correctly on any broker regardless of point size.

### [deploy] First live trade executed

EA successfully detected PDH breakout and placed a buy trade on Coinexx demo. Partial close failed (broker min lot = 1.0) but breakeven and target management worked.

### [feature] Live status panel and level legend on chart

Chart now shows real-time status (scanning/in trade/session over), EST clock with countdown, and a legend explaining every level with current prices.

## 2026-03-31

### [fix] Automatic timezone detection

EA now calculates EST/EDT directly from GMT — no manual broker offset needed. Handles daylight saving time changes automatically.

### [feature] Chart display system

PDH, PDL, Premarket, and Opening Range levels drawn on chart with color-coded labels. Daily trend arrow shows EMA position.

### [deploy] EA running on live MT5

EST Liquidity Breakout EA v2.0 deployed on Coinexx demo account trading SPXUSD M5.

## 2026-03-29

### [wip] EST Liquidity Breakout EA initial build

S&P 500 breakout trading system. Trades PDH/PDL, premarket, and opening range level breakouts with strong candle confirmation. 1R partial close + breakeven + 2R final target.

### [fix] Symbol initialization for demo brokers

SymbolSelect fails on some demo accounts. EA now validates via bid price check instead of blocking on init failure.

## 2026-10-13 — MacroFX v2 backend safety improvements (deployment requested)

**Agent:** ChatGPT (GPT-6). Added atomic server-side command claiming before MT4 broker actions; retained fail-closed/no-retry behavior. Added complete latest position snapshots and authenticated, read-only weekly target reconciliation preview. Changes are on draft feature branch; Railway Dashboard deployment requested. No weekly execution scheduler or automatic trading enabled; MT4 source must be compiled and installed separately. Unrelated Railway staged changes are intentionally excluded.

**Deployment tracking:** Railway Dashboard deployment `3d473bbe-8eeb-41ec-8e27-7012b9f5f246` triggered for `5f6bca4`; BUILDING at last check, pending verification. The existing MT4 EA and automatic trading remain unchanged.

## 2026-10-13 — MacroFX v2 production migration hotfix

**Agent:** ChatGPT (GPT-6). Fixed invalid PostgreSQL anonymous block syntax causing v2 control-text HTTP 500 after the preceding Dashboard deployment. Replaced it with ordinary DROP CONSTRAINT IF EXISTS / ADD CONSTRAINT SQL. Hotfix commit `a16ac2f` submitted to Railway Dashboard; deploy ID `2b6e52f6-78be-4965-92f3-3b7499d2a100`, pending runtime verification. No trading enablement or MT4 installation.

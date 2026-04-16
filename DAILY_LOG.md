# EST Liquidity Breakout EA — Daily Trading Log

This file is auto-updated after each trading day by the push-journal.ps1 script.
Individual daily reports are also saved in the `daily-logs/` folder.
Live daily summaries: https://mt5.freedomincomeoptions.com/summary

---

## 2026-04-15 — Day 9

**EA Version:** v3.1.2 | **Trend:** Bullish | **Symbol:** SPXUSD
**Grade:** Plan A+, EA Execution N/A (technical issues — would have been biggest win day yet)

### Session overview

| Metric | Value |
|--------|-------|
| EA trades | 0 |
| EA P&L | $0.00 |
| Casey manual trades | 0 |
| Market move | 6961 → 7045+ (+84 pts) |
| Plan accuracy | ✅ Both levels hit perfectly |

### Levels

| Level | Price |
|-------|-------|
| PDH | 6977.2 |
| PDL | 6907.9 |
| PM High | 6984.5 |
| PM Low | 6961.8 |
| OR High | 6994.3 |
| OR Low | 6973.8 |

### Casey's plan

- **Bias:** Neutral — PM range after big run up
- **PMH:** 6983.0 | **PML:** 6961.8
- **Long setups:** PMH breakout above 6983, PML bounce at 6961.8
- **Short setups:** PMH rejection at 6983, PML breakdown at 6961.8

### What actually happened

Price opened the session right at the plan levels — PM Low at 6961.8 held as support and price broke out above PM High at 6983/6984.5, then ripped straight up to 7045+ by end of day. An 84-point bull run that touched both key plan levels perfectly.

**The PMH breakout long at 6983 was the trade of the day.** Entry near 6983-6984, stop below PM Low at 6961.8 (~$21 risk), price ran to 7045+ = **60+ points of reward**. At 2 lots that would have been approximately **+$120 on the remaining lot after partial** — the biggest single-day result in the system's history.

The PML bounce long at 6961.8 was also a valid setup if price had tested it first before breaking out.

### Why the EA didn't trade

Two compounding technical failures:

1. **Webhook 500 errors all morning** — the `ea_version` field `"3.1.2 | Plan: Apr 15"` exceeded the `VARCHAR(10)` column limit in the database, crashing every POST to `/api/event`. Fixed at ~4:30 PM EST by altering both `trade_events` and `daily_summaries` columns to `VARCHAR(100)` and patching `main.py`.

2. **EA loaded late** — by the time the EA was confirmed running and diagnostics checked (~10:34 EST), price had already broken through 6983 and was trading at 6997+. The plan levels were 14+ points below price, outside the `MaxProximityPrice = 20.0` window. The EA was watching the right levels — the market had already moved through them.

### The hypothetical trade

| | Value |
|-|-------|
| Setup | PMH Breakout Long at 6983 |
| Entry | ~6984 (ask at breakout) |
| Stop | 6978 (PMH - $5 buffer) |
| Risk | ~$6 price / ~$120 at 2 lots |
| 1R target | ~6990 |
| 2R target | ~6996 |
| Actual high | 7045+ |
| Hypothetical P&L | **+$240–$480** depending on trail |

This would have been by far the largest winning day in the system's history.

### Lessons learned

1. **The plan was perfect — fourth consecutive day of accurate level identification.** PMH and PML were the exact pivots the market used. The system works.
2. **Technical debt is costing real money.** The VARCHAR(10) bug was introduced when `EA_VERSION` was changed to include the date string. A schema constraint caused a full day of missed webhook events.
3. **EA must be loaded and confirmed BEFORE the session starts.** The 9:30 entry window is critical — if the EA isn't running and verified by 9:15 EST, the first move off the open will be missed.
4. **Tomorrow:** Confirm EA running and webhook returning 200s before 9:15 EST. Update plan levels to reflect new price area (7045+).

### System fixes made today

- `ea_version VARCHAR(10)` → `VARCHAR(100)` in both `trade_events` and `daily_summaries` tables
- `main.py` patched and pushed to GitHub so fix persists on redeploy
- Timezone diagnostic block added to `OnInit()` for future debugging
- Premarket log spam bug fixed — was printing 34,000+ identical lines per session

---

## 2026-04-14 — Day 8

**EA Version:** v3.1.1 | **Trend:** Bullish | **Symbol:** SPXUSD
**Grade:** Plan A+, EA Execution F (third day in a row)

### Session overview

| Metric | Value |
|--------|-------|
| EA trades | 0 |
| EA P&L | $0.00 |
| Casey manual trades | 3 |
| Casey manual P&L | +$26.70 |
| Market move | 6907 → 6978 (+71 pts) |

### Levels

| Level | Price |
|-------|-------|
| PDH | 6893.2 |
| PDL | 6795.2 |
| PM High | 6920.0 |
| PM Low | 6898.5 |
| OR High | 6931.4 |
| OR Low | 6907.9 |
| D-2 H | 6951.9 |
| D-3 H | 6920.7 |
| D-4 H | 6920.2 |

### Casey's plan

- **Bias:** Bullish — price above PDH overnight
- **Yesterday:** Breakout in first minutes, rallied all day, very bullish
- **Overnight:** Hit 6918 high
- **Key decision level:** 6918 (old daily level, respected on daily chart)
- **Long setups:** Breakout above 6918. Bounce at 6890-6900 PDH zone.
- **Short setups:** Rejection at 6918. Break below PDH 6893.
- **Additional level identified:** D-3 L at 6767 if PML/ORL stack near it.

### Casey's manual trades (MidasFX, ~$5 offset to Coinexx)

**Trade 1: Buy 6903.1 (≈6908) → 6904.3 = +$1.20 (7 min)**
PM Low zone test. Small scalp.

**Trade 2: Buy 6913.6 (≈6918) → TP 6934.0 (≈6939) = +$20.40 (41 min) ⭐**
- Entry at exactly PlanLong1 (6918 on Coinexx)
- 9:36 AM — entered on a bullish push near the level
- 9:38 AM — SL set at 6906.8 (below OR Low 6907.9), TP set at 6934.0 (OR High area)
- 9:50 AM — trailed SL to 6914.9 (near breakeven, +$1.30 locked)
- 10:10 AM — trailed SL to 6917.0 (plan level, +$3.40 locked)
- 10:17 AM — TP hit at 6934.0 for +$20.40
- Risk: ~$7 | Reward: ~$20 | R:R = 3:1

**Trade 3: Sell 6957.8 (≈6963) → TP 6952.7 (≈6958) = +$5.10 (2 min)**
Afternoon resistance rejection. SL at 6965.8, TP at 6952.5. Hit TP in 2 minutes.

### Casey's trade management framework

| Step | What Casey does | How it differs from EA |
|------|----------------|----------------------|
| Entry | Near plan level, bullish/bearish candle | EA: candle must straddle level with close % filter |
| Stop | At nearest key level (OR Low, PM Low) | EA: fixed buffer beyond plan level ($5) |
| Target | At next key level (OR High, PM High) | EA: fixed 2R from entry |
| Trail 1 | Move stop to near breakeven after price moves | EA: move to exact breakeven at 1R |
| Trail 2 | Move stop to plan level as price extends | EA: no second trail |
| Exit | TP at key level OR trail catches | EA: 2R target or force close |

### What the EA needs to learn from this

1. Stop placement should be at the nearest key level below entry (OR Low, PM Low), not a fixed $5 buffer
2. Target should be at the next key level above entry (OR High, PM High), not fixed 2R
3. Trail should be progressive — near BE first, then to the plan level, then wider if running
4. Entry needs to fire when price is near the plan level and makes a directional candle — the current logic may be working but the EA was restarted during session and missed the window

### Lessons learned

1. Casey is now 3 for 3 on profitable manual trading days while the EA takes zero trades
2. The plan is consistently identifying the right levels — the execution gap is purely technical
3. Trade 2 was textbook: entry at plan level, stop at key level, target at key level, trail in stages
4. Tomorrow: paste plan in chat → Claude codes levels → compile → deploy BEFORE session starts — no restarts during entry window
5. **CRITICAL: Entry window must start at 9:30, not 9:45.** Casey took Trade 2 at 9:36 AM — PMH broke before OR was complete. The 15-minute wait was costing us trades. Changed to 9:30 open.
6. **D-3 H and D-2 H levels were respected perfectly.** Price bounced off both historical levels during the session. These are valid bounce/rejection trade zones and should be included in tomorrow's plan if near current price. Historical levels are proving to be reliable support/resistance.
7. **Live status line added.** Top-left shows what EA is doing at all times — scanning, managing, waiting, or no levels set. No more guessing if the EA is working.

---

## 2026-04-13 — Day 7

**EA Version:** v3.1 | **Trend:** Bullish (Above 10 EMA) | **Symbol:** SPXUSD
**Grade:** Plan A, Execution F

### Session overview

| Metric | Value |
|--------|-------|
| EA trades | 0 |
| EA P&L | $0.00 |
| Casey manual trades | 2 |
| Casey manual P&L | +$21.50 |

### Levels

| Level | Price |
|-------|-------|
| PDH | 6848.2 |
| PDL | 6811.5 |
| PM High | 6803.1 |
| PM Low | 6771.0 |
| OR High | 6808.3 |
| OR Low | 6795.2 |
| D-2 H | ~6848 |
| D-3 H | ~6841 |
| D-3 L | ~6767 |
| D-4 H | ~6801 |
| D-4 L | ~6745 |

### Casey's pre-market plan

- **Bias:** Bullish but cautious — war news pushing lower, 7 days up, expecting pullback
- **Yesterday:** Bounced off PDH and broke down below PDL. Bearish below those levels. Price going to D-3 L support.
- **Overnight:** In a range
- **Key levels:** 6848 (PDH/D-2H resistance), 6811.5 (PDL), 6801 (D-4H), 6767 (D-3L), 6745 (D-4L)
- **Longs:** Level at D-4L or break above PDL — if price breaks above, look for retest of PDL
- **Shorts:** Bounce off PDL or D-4H, or break below D-4L
- **Invalidation:** Levels control the plan
- **Stops:** Clearly below the levels

### EA plan levels programmed

| Input | Value | Why |
|-------|-------|-----|
| PlanLong1 | 6811.5 | PDL bounce/breakout |
| PlanLong2 | 6745.0 | D-4 Low deep support |
| PlanShort1 | 6811.5 | PDL rejection short |
| PlanShort2 | 6848.2 | PDH resistance short |
| PlanShort3 | 6767.0 | D-3 Low breakdown |

### What happened

Price opened around 6790-6800, below PDL. Dipped to ~6795 in premarket/OR area, then rallied steadily from 6795 up through 6811.5 (PDL) and kept going to 6835+ by afternoon. A clean bullish day.

The EA took zero trades despite having PDL (6811.5) programmed as PlanLong1. The breakout through 6811.5 likely happened either before the 9:45 entry window or without a candle cleanly straddling the level.

### Casey's manual trades (MidasFX account)

**Trade 1: Short at 6799.1 → 6798.1 = +$1.00**
Quick scalp near PDL/D-4H zone. Small win.

**Trade 2: Long at 6803.6 → 6824.1 = +$20.50**
THE trade of the day. Bought the stacked support zone: PDL (6811.5), PM High (6803.1), D-4 High (6801). Three levels converging = strong support. Rode it 20 points as price broke above PDL and kept going. This is exactly what the plan said to do.

### What went right

- The plan was excellent — correctly identified PDL zone as key level with stacked support (PMH + D-4H)
- Casey saw the setup and executed manually for +$21.50
- Historical levels (D-4H at 6801) visible on chart and used in the plan
- v3.1 chart is clean — just levels and legend, no clutter

### What went wrong

- EA took zero trades on a +20 point move that the plan identified
- Entry detection too rigid — requires M5 candle to straddle level with proximity check
- Price may have crossed PDL before 9:45 entry window
- The way Casey enters (sees price in the zone, buys the move) doesn't translate to the EA's candle-straddle logic

### Key insight

Casey's second consecutive day of profitable manual trading on the plan levels while the EA does nothing. The plan is working — the execution bridge between plan and EA is not. The entry logic needs a fundamentally different approach for plan-based levels.

### System changes made today

- EA v3.1 deployed: stripped down, clean chart, plan-only trading
- Plan page auto-populates levels from EA webhook
- Refresh button for PM/OR levels after 9:30
- Top-left status panel removed from chart
- Legend updated with version and historical levels

---

## 2026-04-10 — Day 6

**EA Version:** v2.9.1 | **Trend:** Bullish (Above 10 EMA) | **Symbol:** SPXUSD
**OneTradePerDay:** OFF | **Grade:** F (worst day)

### Session overview

| Metric | Value |
|--------|-------|
| Setups found | 4 |
| Setups rejected | 0 |
| Trades taken | 4 |
| Wins / Losses | 0 / 4 |
| Total P&L (MT5) | -$68.40 |
| Best trade | none |
| Worst trade | -$25.60 (#4 ORL Bounce Long) |

### Levels (actual from chart, dashboard had stale data)

| Level | Price |
|-------|-------|
| PDH | 6841.1 |
| PDL | 6767.7 |
| PM High | 6850.3 |
| PM Low | 6815.9 |
| OR High | 6846.7 |
| OR Low | 6832.3 |

### Casey's pre-market plan (filled out at ~7:45 AM)

- **Bias:** Bullish. "6848 is bullish we trade long above that."
- **Yesterday:** "Price is above the PDH for 5 days in a row and there is key resistance around 6848"
- **Overnight:** "Was in a range"
- **Key levels:** "6848 if price breaks above look for bullish trade. If rejection and strong move to downside, look for selling candle to short off that range."
- **Long setups:** "6848 breakout, or breakout and retest with strong bullish bounce"
- **Short setups:** "Rejection of 6848 with strong selling candle. If price breaks below 6812, short or retest of 6812 breakdown."
- **Invalidation:** "If PDH is moved above we are looking for longs. If price fails or breaks below PDL then we short around 6812."
- **Stops:** "Above 6812 for shorts. Below 6848 for longs, maybe around 6845."
- **Notes:** "I don't have PM or OR prices yet but because it is in a range we will be focusing on PDH and PDL."

### What the EA actually did (ignored the plan completely)

| # | Setup | Entry | Stop | P&L | Duration |
|---|-------|-------|------|-----|----------|
| 1 | ORL Bounce Long | 6838.7 | 6830.3 | -$16.80 | 5 min |
| 2 | ORL Bounce Long | 6837.5 | 6830.3 | -$14.40 | 5 min |
| 3 | ORL Bounce Long | 6835.1 | 6830.3 | -$10.00 | 2 min |
| 4 | ORL Bounce Long | 6842.1 | 6830.3 | -$25.60 | 85 min |

All 4 trades: same setup, same level, same stop. The EA has no memory — keeps trying the same failing trade.

### The trade that should have been taken (per Casey)

Short bounce off ORH/PMH/PDH resistance zone at ~6848. Three levels stacked there — strongest resistance zone on the chart. A strong rejection candle there with a short entry would have been the one good trade of the day.

### Why the trades failed

1. **ORL is a weak level** — just the first 15 min of trading. PML (6815.9) was the real support 16 points below.
2. **Range day** — only 14 points of movement. No trend to ride. EA was trying to bounce-trade inside chop.
3. **Same stop hit 4 times** — 6830.3 (ORL - $2). Price kept wicking below. Either the level isn't holding or the buffer is too tight. Doesn't matter — ORL wasn't the right level to trade.
4. **No level hierarchy** — EA treated ORL the same as PDH/PDL/PMH. It shouldn't.

### Strategy decisions made today

1. **Level hierarchy needed:** PDH/PDL > PML/PMH > ORL/ORH. EA must prioritize major levels.
2. **Level stacking:** When PMH + ORH + PDH converge at 6848, that's a mega-level. Single ORL is weak.
3. **Historical levels:** Scan back 5-20 days for swing highs/lows near current price. Previous PDH/PDLs are still live levels.
4. **Daily plan drives trading:** The plan should set the guardrails. EA should only trade the levels in the plan.
5. **One good trade per session:** Stop taking 4-6 shots. Wait for THE setup where plan + level + candle all align.
6. **AI agent will generate the plan:** Build toward automated plan generation using Casey's framework.
7. **Chop detection:** Tight PM range + price between major levels = flag as range day, require breakout before trading.

### Lessons learned

1. Casey's manual plan was better than the EA's automated trading. The plan is the path forward.
2. Level quality matters more than candle quality. A 98% close at a weak level still loses.
3. The one good trade today was the short from 6848 — the EA was long at a weak level and couldn't see it.
4. "There is probably one good trade per session" — this changes the entire approach.

---

## 2026-04-09 — Day 5

**EA Version:** v2.9 | **Trend:** Bullish (Above 10 EMA) | **Symbol:** SPXUSD
**OneTradePerDay:** OFF | **Grade:** B-

### Session overview

| Metric | Value |
|--------|-------|
| Setups found | 6 |
| Setups rejected | 0 |
| Trades taken | 6 |
| Wins / Losses | 1 / 5 (+ 2 partial wins at 1R) |
| Total P&L (MT5) | -$6.50 |
| Best trade | +$36.50 (#6 PMH Breakout Long, 2R) |
| Worst trade | -$23.40 (#1 PMH Breakout Long) |

### Levels

| Level | Price |
|-------|-------|
| PDH | 6801.2 |
| PDL | 6745.8 |
| PM High | 6777.7 |
| PM Low | 6757.6 |
| OR High | 6786.6 |
| OR Low | 6774.0 |

### Trade-by-trade review

**#1 PMH Breakout Long → -$23.40 (SL 11 min)**
Entry 6787.2, Stop 6775.7 (PMH - $2). Candle 76% close. Legitimate breakout setup at PMH — price was right at the level. But PMH was contested; price reversed immediately.

**#2 PMH Bounce Short → -$8.60 (SL 8 seconds!)**
Entry 6775.5, Stop 6779.7. Candle 21% close. Entered on the same candle that stopped #1. Whipsaw — two opposing trades in 11 min at the same level = chop, not a clean signal.

**#3 PMH Breakout Long → -$18.40 (SL 15 min)**
Entry 6784.5, Stop 6775.7. Candle 93% close — very strong. Third trade at PMH in 15 minutes. Price still chopping at this level.

**#4 PMH Bounce Short → +$4.20 partial, -$0.30 BE = +$3.90 net**
Entry 6774.8, Stop 6779.7, Risk $4.10. Hit 1R — partial close worked (1 lot at 1R for +$4.20). BE set on remaining. Remaining stopped at BE.
No-BE: best price 6768.9, hypothetical +$5.90. BE cost $6.20.

**#5 ORL Bounce Long → +$3.20 partial, -$0.50 BE = +$2.70 net**
Entry 6777.9, Stop 6772.0. OR Low bounce — different level from the PMH battle. 81% close. Hit 1R, partial worked. BE stopped remaining.
No-BE: best price 6783.8, hypothetical +$5.90. BE cost $6.40.

**#6 PMH Breakout Long → +$36.50 (2R TARGET HIT! 33 min)**
Entry 6788.0, Stop 6775.7, Risk $12.20. 88% close. Partial at 1R (1 lot), BE set. Price ran to 2R at 6812.4. Remaining lot closed at +$36.50. Biggest win ever.
No-BE: same outcome — 2R hit either way. Hypothetical +$24.50 vs actual +$23.90 on remaining lot.
This was THE trade. Price tested PMH four times (#1-#4), consolidated at ORL (#5), then made the real breakout.

### What the system did right

- Proximity detection working — all trades at real levels, not 150pts away like Apr 8
- Three named setup types fired: PMH Breakout Long, PMH Bounce Short, ORL Bounce Long
- Setup labels visible on chart for easy review
- Partial close working correctly with 2 lots
- Level-based stops gave logical invalidation points
- The 2R winner (#6) was the biggest single trade gain yet

### What needs improvement

- Trading the same level 4 times in chop cost -$50.40 before the +$36.50 win
- Trade #2 entered 8 seconds after #1 stopped out — needs cooldown between trades at same level
- P&L on dashboard was wrong (price distance not dollars) — fixed in v2.9.1
- No daily plan existed — building plan page for tomorrow

### No-BE running scorecard

| Trade | Date | Actual | Without BE | Impact |
|-------|------|--------|-----------|--------|
| Apr 8 #3 PML Breakdown Short | Apr 8 | -$0.30 (BE) | Would have been ~+$14 winner | BE cost ~$14 |
| Apr 9 #4 PMH Bounce Short | Apr 9 | +$3.90 | +$5.90 remaining | BE cost $6.20 |
| Apr 9 #5 ORL Bounce Long | Apr 9 | +$2.70 | +$5.90 remaining | BE cost $6.40 |
| Apr 9 #6 PMH Breakout Long | Apr 9 | +$36.50 | +$24.50 | Same outcome |
| **Total** | | | | **BE has cost ~$26.60 over 4 trades** |

### Lessons learned

1. A contested level (4 tests of PMH) eventually breaks — the question is whether we can survive the chop to catch the breakout.
2. The winning trade came after consolidation at a different level (ORL) — this confirms the pattern from Apr 8.
3. Partial close at 2 lots is working perfectly — first time position management is fully functional.
4. Need a daily plan to avoid blind entries in chop zones.

---

## 2026-04-08 — Day 4

**EA Version:** v2.8 | **Trend:** Bullish (Above 10 EMA) | **Symbol:** SPXUSD
**OneTradePerDay:** OFF (Casey's choice) | **Grade:** Learning Day

### Session overview

| Metric | Value |
|--------|-------|
| Setups found | 8 |
| Setups rejected | 1 (Error 4756) |
| Trades taken | 7 |
| Wins / Losses | 1 / 6 |
| Win rate | 14% |
| Total P&L | -$32.00 |
| Best trade | +$21.60 (2R target!) |
| Worst trade | -$14.10 |

### Levels

| Level | Price |
|-------|-------|
| PDH | 6628.6 |
| PDL | 6537.9 |
| PM High | 6812.1 |
| PM Low | 6781.6 |
| OR High | 6801.2 |
| OR Low | 6778.1 |

### Trade-by-trade review

**Trade 1: LONG "PDH" at 09:50 → -$14.10 (SL in ~1 min)**
- Entry ~6793, Stop 6780, candle close 79.2%
- Pre-daily-reset trade — used stale levels. No valid setup.
- Casey's take: No market context. Above PDH is just bias — needed a trigger level.

**Trade 2: LONG "PDH" at 10:05 → -$7.90 (SL in 1 min)**
- Entry 6783.7, Stop 6776.4 (candle low), Risk $6.80
- Same problem as Trade 1. Strong candle above PDH but no trigger — no support bounce, no level breakout.
- Casey's take: Same as Trade 1. Being above PDH doesn't mean buy every candle.

**Trade 3: SHORT PM Low at 10:30 → -$0.30 (breakeven)**
- Entry 6771.6, Stop 6777.7, Risk $6.10
- PML Breakdown Short — price broke through PM Low (6781.6) with bearish candle (21% close).
- Hit 1R at 6765.5. Partial close failed (min lot). Stop moved to breakeven. Price bounced back, hit BE.
- Casey's take: GOOD SETUP. Would have been a big winner without breakeven. ORL also broke. PDL is 130pts below = room to run. Track "no BE" outcome.
- **No-BE hypothetical:** Price reached at least 6757 area → would have been ~14+ point winner.

**Trade 4: SHORT PM Low at 10:43 → REJECTED Error 4756**
- Setup found immediately after Trade 3 closed. Order failed.
- May be related to Trade 3's partial close attempt leaving position in liminal state.

**Trade 5: LONG "PDH" at 10:50 → -$9.10 (SL in 3 min)**
- Entry 6766.3, Stop 6757.4, candle close 84.6%
- Same PDH problem — no trigger level, just strong candle far above PDH.

**Trade 6: LONG "PDH" at 11:05 → -$11.00 (SL in 4 min)**
- Entry 6769.1, Stop 6758.4, candle close 72.3%
- Same pattern. Enters, immediately reverses.

**Trade 7: SHORT PM Low at 11:10 → -$11.20 (SL in 14 min)**
- Entry 6756.8, Stop 6767.8, Risk $10.60
- PML Breakdown Short — second attempt. Price was choppy at this level. Stopped out.

**Trade 8: LONG "PDH" at 11:24 → +$21.60 (2R TARGET HIT! 80 min hold)**
- Entry 6767.6, Stop 6756.8, Risk $10.80. Candle close 92.5% — strongest of the day.
- Hit 1R at 11:49, partial skipped (min lot), stop moved to BE. Hit 2R at 12:45.
- Casey's take: This was a PDH CONTINUATION trade. The massive PDH breakout (6628→6812) was the campaign. Price consolidated around 6757 (the red box zone). Trade 8 caught the continuation wave out of consolidation. The trade wasn't just "above PDH" — it was the next leg of the PDH breakout campaign.

### Key strategy lessons (from Casey's review)

1. **PDH breakout is a campaign, not a candle.** The initial break launches price, consolidation follows, then the continuation wave. Trade 8 caught the continuation.

2. **Being above PDH = bullish bias, not a trade signal.** Need a specific trigger: bounce off support, breakout of consolidation, or crossover of PMH/ORH/PML/ORL.

3. **PML Breakdown Short was the right trade (Trade 3).** Price broke through PM Low with conviction. The setup was valid. Breakeven killed the winner.

4. **The consolidation zone IS the setup forming.** The red box Casey drew (6740-6757 area) was where smart money consolidated after the big PDH move before launching the next wave.

5. **Distance between levels = reward potential.** PML breakdown with PDL 130pts below = room to run = good short. Need to consider level spacing.

6. **Each setup needs a name.** "LONG PDH" means nothing when price is 150pts above PDH. Need: "PDH Continuation Long", "PML Breakdown Short", etc.

7. **Breakeven at 1R needs evaluation.** Trade 3 hit 1R, moved to BE, got stopped. Without BE it would have been a big winner. Track "no BE" hypothetical going forward.

8. **No filters until Casey understands the entry logic.** Don't add trend filters, distance filters, or any automated filters. Build understanding first.

### Issues

- Error 4756 appeared once (Trade 4) — intermittent, may be related to partial close
- Partial close still failing (min lot = 1.0, can't split)
- Entry logic needs complete redesign around the liquidity framework

---

## 2026-04-07 — Day 3

**EA Version:** v2.8 | **Trend:** Bullish (Above 10 EMA) | **Symbol:** SPXUSD
**Grade:** Config Error

### Session overview

| Metric | Value |
|--------|-------|
| Setups found | 7 |
| Setups rejected | 7 |
| Trades taken | 0 |
| Wins / Losses | 0 / 0 |
| Total P&L | $0.00 |

### Levels

| Level | Price |
|-------|-------|
| PDH | 6623.7 |
| PDL | 6581.7 |
| PM High | 6631.9 |
| PM Low | 6568.4 |
| OR High | 6603.9 |
| OR Low | 6576.2 |

### What happened

EA found 7 valid SHORT setups on PDL (6581.7) from 9:45-11:25 EST. Every single one was rejected with Error 4756 (TRADE_SEND_FAILED) because FixedLots was set to 0.01 but the Coinexx broker requires minimum 1.0 lot.

Price dropped from ~6580 at 9:45 EST to ~6545 by 10:10 EST — a 35-point move. The first setup at 9:45 would have had entry ~6577.7, stop at 6584.2 (candle high), risk of 6.5 points. The 2R target at ~6564.7 would have been hit within 25 minutes.

### Setups (all SHORT on PDL, all rejected Error 4756)

| Time EST | Candle Close | Close % | Bid |
|----------|-------------|---------|-----|
| 09:45 | 6577.4 | 15.0% | 6577.7 |
| 10:00 | 6567.9 | 2.5% | 6567.7 |
| 10:05 | 6562.4 | 22.2% | 6562.2 |
| 10:10 | 6550.9 | 26.2% | 6550.9 |
| 11:00 | 6554.8 | 15.2% | 6554.8 |
| 11:05 | 6546.2 | 13.1% | 6545.9 |
| 11:25 | 6551.4 | 3.0% | 6551.2 |

### Key observations

- All 7 candle close percentages were low (2.5-26%) = strong bearish momentum, closes near lows
- This was a counter-trend trade (daily trend Bullish, trading SHORT) — but the breakdown was real
- EA kept retrying same setup every 5 min because failed orders don't count as "trade taken"
- Webhook pipeline working correctly — all events visible on Railway dashboard in real-time
- First day with /summary page auto-generating reports

### Issues

- **FixedLots = 0.01** — must change to 1.0 before tomorrow (CRITICAL)
- Failed order retries not blocked by OneTradePerDay (order never executed so flag never set)
- Stop placement would have been excellent today: 6.5 pt risk for 13+ pt reward

### Lessons learned

- The strategy found the right trade at the right time — the signal is working
- Infrastructure (webhook, dashboard, summary) all functioning correctly
- Configuration errors (lot size) are the only thing preventing execution
- Counter-trend setups can be very profitable — don't enable trend filter yet

---

## 2026-04-02 — Day 2

**EA Version:** v2.6 | **Trend:** Bullish (Above 10 EMA) | **Symbol:** SPXUSD

### Session overview

| Metric | Value |
|--------|-------|
| Setups found | 9 |
| Setups rejected | 1 |
| Trades taken | 8 (OneTradePerDay bug) |
| Wins / Losses | 0 / 8 |
| Win rate | 0% |
| Total P&L | -$56.70 |
| Best trade | $0.00 |
| Worst trade | -$15.90 |

### Levels

| Level | Price |
|-------|-------|
| PDH | 6614.8 |
| PDL | 6559.2 |
| PM High | 6512.1 |
| PM Low | N/A |
| OR High | 6499.6 |
| OR Low | N/A |

### Trades

1. **SELL** on PDL — Entry: 6480.9, SL hit at 6496.8 → **-$15.90**
2. **BUY** on OR High — Entry: 6513.8, SL hit at 6510.1 → **-$3.70**
3. **BUY** on PM High — Entry: 6524.7, SL hit at 6520.3 → **-$4.40**
4. **SELL** on PDL — Entry: 6515.7, SL hit at 6526.3 → **-$10.60**
5. **BUY** on PM High — Entry: 6525.8, SL hit at 6523.3 → **-$2.50**
6. **SELL** on PDL — Entry: 6521.8, SL hit at 6535.0 → **-$13.20**
7. **BUY** on PM High — Entry: 6551.7, SL hit at 6548.5 → **-$3.20**
8. **BUY** on PM High — Entry: 6576.5, SL hit at 6573.3 → **-$3.20**

### Key issues discovered

- **OneTradePerDay completely broken** — EA took 8 trades instead of 1
- **Journal P&L was fictional** — reported +$274.30 when actual was -$56.70
- **g_entryPrice never reset** — all closes calculated P&L against first trade's entry
- **Short trades on PDL fired while price was below PDL** — stale level detection

### Lessons learned

- The EA's state management was fundamentally broken — position close detection, trade counting, and P&L calculation all needed rebuilding
- A trending bullish day with shorts on PDL is counter-trend → all shorts lost
- Stop loss on breakout candle low is too tight — gets clipped on normal pullback within 1-2 bars
- Need to verify journal accuracy by comparing against broker trade history every day

### System changes

- v2.7 built to fix OneTradePerDay, add DetectBrokerSideClose(), reset trade state properly

---

## 2026-04-01 — Day 1

**EA Version:** v2.4/v2.5 | **Trend:** Below 10 EMA → Above 10 EMA | **Symbol:** SPXUSD

### Session overview

| Metric | Value |
|--------|-------|
| Trades taken | 2 (EA) + 1 (manual) |
| Wins / Losses | 1 / 1 (EA), 1 / 0 (manual) |
| Total P&L | ~+$14 (estimated) |

### Trades

1. **BUY** on PDH — Entry: ~6582, SL hit at 6573 → **-$10** (stop too tight, 9.8 pt stop)
2. **BUY** on PDH — Entry: 6586.8, SL: 6565.6, 1R: 6607.8, 2R: 6628.8 → **+$24** (partial skipped, BE set, profitable)

### Key issues discovered

- First trade's stop was only 9.8 points — too tight, clipped on normal pullback before the real move
- Second trade had wider stop (21.2 points) and worked
- Partial close failed — broker min lot = 1.0, can't split
- EA reloaded mid-session, allowing second trade (OneTradePerDay reset)
- MinimumBreakoutPoints and MaximumStopPoints were in MT5 points, not price → wrong values for different brokers

### Lessons learned

- Wider stops survive better — the breakout was valid but the first entry got shaken out
- Point-based settings don't transfer between brokers — need price-based settings
- Partial close needs to check minimum volume before attempting
- First profitable EA trade — the strategy concept works when given room

### System changes

- v2.5 built: changed all settings to price-based values
- v2.6 built: added CSV trade journal system

---

## 2026-03-31 — Day 0 (setup day)

**EA Versions:** v1.4 → v2.0 | **Trend:** Below 10 EMA | **Symbol:** US500

### What happened

- EA loaded on MetaQuotes demo (US500) — no trades allowed (demo restriction)
- Levels calculated correctly: PDH=6435.50, PDL=6378.50, PM/OR levels found
- Timezone was wrong — clock showed 16:23 when it was 9:23 EST (7 hour offset)
- Multiple MT5 auto-updates restarted the platform during trading hours

### System changes

- v1.4: Fixed log spam
- v1.5: PDH/PDL lookback 5 days for weekends
- v1.6: Added live status panel
- v1.7: Added level legend
- v1.9: Legend with dark background
- v2.0: Bottom-left legend, cyan colors, EST clock + session timer

### Lessons learned

- Timezone detection is critical — all session windows were 7 hours off
- Disable MT5 auto-updates during market hours
- Need a real broker demo account (MetaQuotes demo blocks trading)

---

*This log is automatically updated by the push-journal.ps1 script on the VPS.*
*Individual daily reports with full event timelines are in the daily-logs/ folder.*
*Pattern analysis and cumulative stats available at: https://web-production-4c92.up.railway.app/api/cumulative-log*

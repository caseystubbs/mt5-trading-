# EST Liquidity Breakout EA — Daily Trading Log

This file is auto-updated after each trading day by the push-journal.ps1 script.
Individual daily reports are also saved in the `daily-logs/` folder.
Live daily summaries: https://mt5.freedomincomeoptions.com/summary

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

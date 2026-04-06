# EST Liquidity Breakout EA — Daily Trading Log

This file is auto-updated after each trading day by the push-journal.ps1 script.
Individual daily reports are also saved in the `daily-logs/` folder.

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

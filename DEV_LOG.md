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

**Entry:** M5 candle closes beyond a key level by MinimumBreakoutPrice ($2.50) with a strong close (top/bottom 30% of candle range)

**Levels (priority order):** PDH → PM High → OR High (longs), PDL → PM Low → OR Low (shorts)

**Stop:** Breakout candle's low (longs) or high (shorts)

**Targets:** 1R = same distance as stop, 2R = 2x distance

**Management:** At 1R: close 50% + move stop to breakeven. At 2R: close remaining. Force close at 15:55 EST.

---

## Patterns observed

*Updated daily from trade journal analysis and Railway API pattern tracking*

### Confirmed patterns
- **Broker-side SL closes not detected** — Fixed in v2.7 with `DetectBrokerSideClose()`
- **OneTradePerDay flag resets on EA restart** — Fixed in v2.7 with proper state management
- **Journal P&L can be fictional** — Fixed in v2.7 by reading actual broker deal history
- **Partial close fails at minimum lot size** — Logged but not fixed (broker min = 1.0 lot, can't split)

### Pending observations (needs more data)
- [ ] Stop placement too tight — breakout bar low gets clipped on normal pullback (seen on Apr 1)
- [ ] PDH breakouts may have different win rate than OR High breakouts — tracking via API
- [ ] Counter-trend trades (e.g. long when daily trend bearish) — need data on win rate
- [ ] Strong close % (90%+ vs 70-80%) — does stronger close predict better outcomes?
- [ ] Time of day effect — do earlier setups (9:45-10:15) win more than later ones?
- [ ] Spread at entry — does wider spread correlate with losses?

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

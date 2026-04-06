# EST Liquidity Breakout EA — Development Log

## System overview

Automated S&P 500 breakout trading system that trades liquidity sweeps at key intraday levels.

**Stack:** MQL5 EA (MetaTrader 5) → FastAPI (Railway) → PostgreSQL → Dashboard

## Changelog

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

*Updated daily from trade journal analysis*

### Pending observations (needs more data)
- [ ] Stop placement too tight — breakout bar low gets clipped on normal pullback
- [ ] Multiple trades on same level after reload — OneTradePerDay resets on EA restart
- [ ] Partial close fails when lot size = broker minimum (can't split 1 lot)

---

## Performance metrics

*Auto-updated from Railway API*

| Metric | Value | Updated |
|--------|-------|---------|
| Total trades | — | — |
| Win rate | — | — |
| Avg P&L per trade | — | — |
| Best trade | — | — |
| Worst trade | — | — |
| Profit factor | — | — |

---

## Next improvements planned

1. **Stop placement options** — test level-based stop vs candle-low stop vs ATR-based stop
2. **Multi-instrument** — add NQ100, Russell 2000
3. **Backtest** — run MT5 strategy tester over 2 years of data
4. **Trend filter** — enable UseDailyTrendFilter and track if it improves win rate
5. **Volatility filter** — skip low-ATR days where breakouts fail more often

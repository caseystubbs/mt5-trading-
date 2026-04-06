## 2026-04-06

### [feature] Real-time trade dashboard live on Railway

EA now sends every trade event to a live dashboard you can check from your phone. Shows today's trades, P&L, win rate, and daily history.

Dashboard: https://web-production-4c92.up.railway.app/

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

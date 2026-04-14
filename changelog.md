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

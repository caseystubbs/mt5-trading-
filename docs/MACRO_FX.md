# Macro FX / MidasFX MT4 bridge

This module adds a separate macro-currency strategy to the existing Railway trading journal.
It does not modify the existing EST Liquidity Breakout strategy.

## Architecture

MidasFX MT4 demo -> FIO_MacroFX_Bridge.mq4 -> HTTPS -> Railway FastAPI/Postgres

Railway stores:
- demo account heartbeats
- MT4 positions
- broker fills
- daily FX bars
- weekly currency-factor snapshots
- target positions
- weekly feedback reports

## Safety defaults
- Demo account only
- 0.01 lot maximum per pair
- 2 simultaneous MacroFX positions
- unique Magic Number 26092601
- flatten only positions with this Magic Number that are not in the current target set
- no martingale, grid, averaging down or recovery sizing

## MT4 setup
1. Compile mt4/FIO_MacroFX_Bridge.mq4 in MetaEditor.
2. Attach it to one chart in MidasFX desktop MT4.
3. Set ApiBaseUrl=https://mt5.freedomincomeoptions.com.
4. Set ApiKey to the same value as Railway EA_API_KEY.
5. MT4 -> Tools -> Options -> Expert Advisors -> Allow WebRequest for https://mt5.freedomincomeoptions.com.
6. Keep DemoOnly=true and EnableTrading=false for the first connectivity test.
7. Confirm /api/macrofx/health receives heartbeats and bars.
8. Run the first weekly analysis with POST /api/macrofx/run-weekly.
9. Inspect /api/macrofx/weekly-report and /api/macrofx/status.
10. Only then set EnableTrading=true on the demo EA.

## Weekly feedback loop

Friday after the trading week:
1. MT4 has already uploaded daily closes.
2. Railway decomposes pair returns into individual currency factors.
3. 21/63/126/252-day volatility-normalized momentum is calculated.
4. Currencies are ranked strongest to weakest.
5. Up to two independent strongest-vs-weakest pair expressions are selected.
6. Target set is written to Postgres.
7. MT4 reconciles only MagicNumber 26092601 positions to those targets.
8. MT4 posts fills, spreads, swaps and commissions.
9. Weekly report compares broker-demo reality with the macro model.

## Important
The weekly report is a feedback loop, not an automatic optimization loop. Strategy parameter changes must be versioned and retested rather than changed because of a single weak week.

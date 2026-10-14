# MacroFX v1.1 backtest, 2000–2026

**Generated:** 2026-10-14 by `scripts/backtest_macrofx.py`. **Data:** Federal Reserve H.10 daily noon buying rates (datasets/exchange-rates on GitHub), 1999-01-04 to 2026-10-09, all 28 crosses built from 7 USD rates. **Rebalances:** 1397 weekly (Friday close).

## Bottom line

**Over 26 years the v1.1 signal had no edge, even before costs.** With realistic weekday costs it lost -7.5% a year (Sharpe -0.30), and it lost in both halves: 2000–2012 -7.2%/yr and 2013–2026 -7.7%/yr. The loss is not statistically strong (t = -1.55), so the honest reading is "no evidence of an edge", not "reliably loses". Two random pairs held the same way scored a median Sharpe of -0.07; v1.1 beat only 17% of 30 random runs.

**Executing at the Sunday reopen would have been ruinous:** -24.9% a year. Moving execution to Monday (now built) is the single biggest fix available.

**The proposed tweaks don't rescue it.** A rotation buffer and a volatility stop each changed the result by less than half a percent a year.

## Results (each position sized at 1× equity notional, about 0.01 lot on $1,000)

| Variant | CAGR | Sharpe | Max drawdown | t-stat | Win rate | Trades/yr | Cost drag/yr |
|---|---:|---:|---:|---:|---:|---:|---:|
| v1.1 · weekday execution | -7.5% | -0.30 | -89% | -1.55 | 44% | 57 | -1.1% |
| v1.1 · Sunday-reopen execution | -24.9% | -1.34 | -100% | -6.94 | 44% | 57 | -21.9% |
| v1.1 · no costs (signal only) | -6.5% | -0.24 | -86% | -1.26 | 44% | 57 | -0.0% |
| v1.1 + rotation buffer 0.25 · weekday | -7.2% | -0.28 | -89% | -1.47 | 40% | 31 | -0.6% |
| v1.1 + volatility stop 2x · weekday | -7.6% | -0.31 | -89% | -1.60 | 44% | 58 | -1.1% |
| v1.1 + buffer + stop · weekday | -7.1% | -0.28 | -88% | -1.44 | 40% | 32 | -0.6% |

Random benchmark (30 runs, weekday costs): median Sharpe -0.07, 95th percentile +0.12.

## Why it doesn't work (component check, no costs)

Long the strongest / short the weakest currency on each horizon alone, held one week:

| Horizon | Sharpe | t-stat |
|---|---:|---:|
| 1 month | −0.33 | −1.72 |
| 3 months | −0.05 | −0.24 |
| 6 months | −0.24 | −1.25 |
| 12 months | −0.02 | −0.08 |

None of the four momentum horizons has paid in G8 currencies since 2000 on a weekly holding period. Published research has generally found currency-momentum profits concentrated in earlier decades and in less-traded currencies, and this data agrees for the G8 majors since 2000. The scoring formula isn't the main problem; the underlying effect is.

## What this does and doesn't cover

- **Not modelled:** swap/carry (no historical broker swap data), slippage beyond the spread, intraday stop fills (stops use daily closes), and the Fed's noon New York rates are used instead of broker closes.
- **No parameters were fitted** to this data. The rules are tested exactly as they run live, using the live engine code (verified identical to 1e-14).
- **Data sensitivity:** on the Fed's Oct 9 prices the model picks USDCHF where the broker's prices picked NZDUSD. The 0.0002 near-tie flips on small price differences.

## Recommendation

1. Keep v1.1 on the **demo only**. Don't add size or go live with this signal.
2. Use the demo for what it's proving well: the bridge, approval queue, execution and records.
3. Research a different signal before investing more in tuning this one: carry (interest-rate differential) or carry combined with momentum, and longer holding periods to cut turnover. Each new idea goes through this same backtest first.

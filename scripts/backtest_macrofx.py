"""Historical simulation of MacroFX v1.1 (and research variants) with trading costs.

Data: Federal Reserve H.10 daily noon buying rates (via the public GitHub
dataset datasets/exchange-rates), 7 currencies vs USD -> all 28 crosses.
Signal: the live engine itself (macrofx_engine.currency_factor_returns,
snapshot_from_factors, pair_scores, choose_targets): no re-implementation.

Simulation
- Rebalance on each Friday's close using data up to that day.
- Hold to the next Friday's close. Each position is sized at 1x account
  equity notional (about what 0.01 lots is on the $1,000 demo account).
- Costs are paid when a position is opened or closed, never on holds:
  "weekday" = 1 pip per side (what the demo has filled at on weekdays),
  "sunday"  = 20 pips per side (what the demo paid at the Sunday reopen).
- Swap is NOT modelled (no historical broker swap data). See notes.

Run:  python scripts/backtest_macrofx.py [path/to/daily.csv]
Writes docs/backtest/results.json and docs/backtest/REPORT.md
"""
from __future__ import annotations

import json
import math
import os
import random
import sys
import urllib.request
from datetime import datetime, timezone

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from macrofx_engine import (DEFAULT_PAIRS, MAX_POSITIONS, MIN_ABS_PAIR_SCORE,  # noqa: E402
                            currency_factor_returns, pair_scores, snapshot_from_factors)

DATA_URL = "https://raw.githubusercontent.com/datasets/exchange-rates/main/data/daily.csv"
COUNTRY = {"EUR": "Euro", "GBP": "United Kingdom", "JPY": "Japan", "CHF": "Switzerland",
           "CAD": "Canada", "AUD": "Australia", "NZD": "New Zealand"}
START = "2000-01-01"          # euro history starts 1999; one year of lookback needed
LOOKBACK_ROWS = 400           # >= 253 trading days needed by the 12-month horizon
COSTS_PIPS = {"none": 0.0, "weekday": 1.0, "sunday": 20.0}


# ------------------------------------------------------------------ data
def load_prices(path: str | None) -> pd.DataFrame:
    if not path:
        path = "/tmp/macrofx_fx_daily.csv"
        if not os.path.exists(path):
            urllib.request.urlretrieve(DATA_URL, path)
    raw = pd.read_csv(path)
    raw["Date"] = pd.to_datetime(raw["Date"])
    per_usd = {}
    for ccy, country in COUNTRY.items():
        s = raw[raw["Country"] == country].set_index("Date")["Exchange rate"].astype(float)
        per_usd[ccy] = s[s > 0]
    u = pd.DataFrame(per_usd).sort_index()
    u = u[u.index >= "1999-01-04"].ffill(limit=3).dropna()
    u["USD"] = 1.0
    closes = {}
    for p in DEFAULT_PAIRS:
        b, q = p[:3], p[3:]
        closes[p] = u[q] / u[b]           # units of quote per 1 base
    return pd.DataFrame(closes)


def pip(pair: str) -> float:
    return 0.01 if pair.endswith("JPY") else 0.0001


# ------------------------------------------------------------------ selection
def select(snap: pd.DataFrame, held: dict, buffer: float = 0.0):
    """choose_targets() with an optional hysteresis bonus for pairs already held."""
    ps = pair_scores(snap, DEFAULT_PAIRS)
    if ps.empty:
        return {}
    if buffer:
        ps = ps.copy()
        bonus = [buffer if (r.symbol in held and held[r.symbol] == r.direction) else 0.0 for r in ps.itertuples()]
        ps["rank_score"] = ps["abs_score"] + bonus
        ps = ps.sort_values("rank_score", ascending=False)
    out, used = {}, set()
    for r in ps.itertuples():
        if not r.eligible or r.abs_score < MIN_ABS_PAIR_SCORE:
            continue
        if out and (r.base in used or r.quote in used):
            continue
        out[r.symbol] = (r.direction, float(r.pair_score))
        used.update([r.base, r.quote])
        if len(out) >= MAX_POSITIONS:
            break
    return out


# ------------------------------------------------------------------ simulation
_SNAP_CACHE: dict = {}


def _snapshot(factors, d0):
    if d0 not in _SNAP_CACHE:
        fw = factors.loc[:d0].tail(LOOKBACK_ROWS)
        _SNAP_CACHE[d0] = snapshot_from_factors(fw) if len(fw) >= 260 else None
    return _SNAP_CACHE[d0]


def simulate(closes, factors, fridays, cost_pips=1.0, buffer=0.0, stop_k=None, picker=None, seed=0):
    rng = random.Random(seed)
    held = {}                     # pair -> direction
    weekly, trades, weeks_in = [], [], 0
    rows = closes.index
    daily_ret = closes.pct_change()
    for i in range(len(fridays) - 1):
        d0, d1 = fridays[i], fridays[i + 1]
        if picker != "random":
            snap = _snapshot(factors, d0)
            if snap is None:
                continue
        elif len(factors.loc[:d0]) < 260:
            continue
        if picker == "random":
            pairs = rng.sample(DEFAULT_PAIRS, 2)
            want = {p: (rng.choice(["LONG", "SHORT"]), 0.0) for p in pairs}
        else:
            want = select(snap, held, buffer)
        cost = 0.0
        # closes (anything held that is not wanted in the same direction)
        for p, d in list(held.items()):
            if p not in want or want[p][0] != d:
                cost += cost_pips * pip(p) / closes.at[d0, p]
                del held[p]
        for p, (d, sc) in want.items():
            if p not in held:
                cost += cost_pips * pip(p) / closes.at[d0, p]
                held[p] = d
                trades.append({"open": str(d0.date()), "pair": p, "dir": d, "score": sc, "ret": 0.0, "days": 0})
        # hold through the week, daily, with an optional volatility stop
        week_days = rows[(rows > d0) & (rows <= d1)]
        port = 0.0
        stopped = set()
        for p, d in list(held.items()):
            sgn = 1 if d == "LONG" else -1
            vol_w = daily_ret[p].loc[:d0].tail(60).std() * math.sqrt(5)
            cum = 0.0
            for day in week_days:
                cum = (1 + cum) * (1 + sgn * daily_ret.at[day, p]) - 1
                if stop_k and cum <= -stop_k * vol_w:
                    stopped.add(p)
                    cost += cost_pips * pip(p) / closes.at[day, p]
                    break
            port += cum
            t = next(t for t in reversed(trades) if t["pair"] == p)
            t["ret"] = (1 + t["ret"]) * (1 + cum) - 1
            t["days"] += len(week_days)
        for p in stopped:
            del held[p]
        if held or stopped:
            weeks_in += 1
        weekly.append({"date": str(d1.date()), "ret": port - cost, "gross": port, "cost": cost})
    return weekly, trades, weeks_in


def metrics(weekly, trades, weeks_in):
    r = np.array([w["ret"] for w in weekly])
    if len(r) == 0:
        return {}
    eq = np.cumprod(1 + r)
    years = len(r) / 52.0
    peak = np.maximum.accumulate(eq)
    dd = float((eq / peak - 1).min())
    sd = r.std(ddof=1)
    closed = [t["ret"] for t in trades]
    t_stat = float(r.mean() / (sd / math.sqrt(len(r)))) if sd > 0 else None
    return {
        "weeks": int(len(r)), "years": round(years, 1),
        "cagr": float(eq[-1] ** (1 / years) - 1), "total_return": float(eq[-1] - 1),
        "ann_vol": float(sd * math.sqrt(52)), "sharpe": float(r.mean() / sd * math.sqrt(52)) if sd > 0 else None,
        "max_drawdown": dd, "t_stat": t_stat,
        "trades": len(trades), "trades_per_year": round(len(trades) / years, 1),
        "win_rate": float(np.mean([x > 0 for x in closed])) if closed else None,
        "avg_trade": float(np.mean(closed)) if closed else None,
        "avg_trade_weeks": float(np.mean([t["days"] for t in trades]) / 5) if trades else None,
        "cost_drag_per_year": float(sum(w["cost"] for w in weekly) / years),
        "pct_weeks_invested": weeks_in / len(r),
    }


def yearly(weekly):
    out = {}
    for w in weekly:
        y = w["date"][:4]
        out[y] = (1 + out.get(y, 0.0)) * (1 + w["ret"]) - 1
    return out


def curve(weekly, step=4):
    eq, pts = 1.0, []
    for i, w in enumerate(weekly):
        eq *= 1 + w["ret"]
        if i % step == 0 or i == len(weekly) - 1:
            pts.append([w["date"], round(eq, 5)])
    return pts


def main():
    closes = load_prices(sys.argv[1] if len(sys.argv) > 1 else None)
    factors = currency_factor_returns(closes)
    idx = closes.index
    fridays = sorted({idx[idx <= d].max() for d in pd.date_range(START, idx.max(), freq="W-FRI") if (idx <= d).any()})
    split = pd.Timestamp("2013-01-01")

    variants = {
        "v1.1 · weekday execution": dict(cost_pips=COSTS_PIPS["weekday"]),
        "v1.1 · Sunday-reopen execution": dict(cost_pips=COSTS_PIPS["sunday"]),
        "v1.1 · no costs (signal only)": dict(cost_pips=0.0),
        "v1.1 + rotation buffer 0.25 · weekday": dict(cost_pips=COSTS_PIPS["weekday"], buffer=0.25),
        "v1.1 + volatility stop 2x · weekday": dict(cost_pips=COSTS_PIPS["weekday"], stop_k=2.0),
        "v1.1 + buffer + stop · weekday": dict(cost_pips=COSTS_PIPS["weekday"], buffer=0.25, stop_k=2.0),
    }
    results = {}
    for name, kw in variants.items():
        wk, tr, wi = simulate(closes, factors, fridays, **kw)
        first = [w for w in wk if w["date"] < str(split.date())]
        second = [w for w in wk if w["date"] >= str(split.date())]
        results[name] = {"params": kw, "all": metrics(wk, tr, wi),
                         "2000-2012": metrics(first, [t for t in tr if t["open"] < "2013"], 0),
                         "2013-2026": metrics(second, [t for t in tr if t["open"] >= "2013"], 0),
                         "yearly": yearly(wk), "curve": curve(wk)}
        print(f"{name:42s} CAGR {results[name]['all']['cagr']:+.2%}  Sharpe {results[name]['all']['sharpe']:.2f}  "
              f"MaxDD {results[name]['all']['max_drawdown']:.1%}  t {results[name]['all']['t_stat']:.2f}", flush=True)

    # Null benchmark: 2 random pairs, random direction, same costs and holding rule
    rnd = []
    for seed in range(30):
        wk, tr, wi = simulate(closes, factors, fridays, cost_pips=COSTS_PIPS["weekday"], picker="random", seed=seed)
        rnd.append(metrics(wk, tr, wi))
    sharpe_r = sorted(m["sharpe"] for m in rnd)
    base = results["v1.1 · weekday execution"]["all"]["sharpe"]
    results["_random_benchmark"] = {
        "runs": len(rnd), "sharpe_median": float(np.median(sharpe_r)),
        "sharpe_p95": float(np.percentile(sharpe_r, 95)), "sharpe_max": float(max(sharpe_r)),
        "model_beats_pct_of_random": float(np.mean([base > s for s in sharpe_r])),
    }
    print("random benchmark:", results["_random_benchmark"], flush=True)

    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "data": "Federal Reserve H.10 daily noon buying rates (datasets/exchange-rates on GitHub)",
        "data_first": str(closes.index.min().date()), "data_last": str(closes.index.max().date()),
        "test_start": START, "rebalances": len(fridays),
        "sizing": "each position = 1x account equity notional (about 0.01 lot on a $1,000 account)",
        "costs": {"weekday_pips_per_side": COSTS_PIPS["weekday"], "sunday_pips_per_side": COSTS_PIPS["sunday"]},
        "not_modelled": ["swap / carry", "slippage beyond the spread", "intraday stop fills (stops use daily closes)",
                         "noon NY rates instead of broker closes"],
        "parameters_fitted": False,
    }
    os.makedirs(os.path.join(ROOT, "docs", "backtest"), exist_ok=True)
    with open(os.path.join(ROOT, "docs", "backtest", "results.json"), "w") as f:
        json.dump({"meta": meta, "results": results}, f, indent=1, default=float)
    print("wrote docs/backtest/results.json")


if __name__ == "__main__":
    main()

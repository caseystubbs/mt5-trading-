"""Candidate FX strategies from the long-term research, tested on free data.

Data reachable from this environment (GitHub raw only):
- Spot: Fed H.10 daily rates (datasets/exchange-rates), currency per USD.
- Inflation: annual CPI inflation (datasets/cpi, World Bank), used for value.
Carry cannot be tested here: no historical short-term interest rates.

All portfolios are spot-only (no interest differential / swap), dollar-neutral
long-short across currencies unless noted, with 2 bp per side turnover cost.

Tests
 A. Engine check: MacroFX v1.1 (live engine code) on 1974-1999, 7 currencies
    (no EUR before 1999). Literature says FX momentum worked before ~2001.
 B. Academic momentum (Menkhoff/Hutchinson style): 3-month formation,
    1-month hold, long top 3 / short bottom 3 of 8 currencies (incl. USD).
 C. Value (Asness-Moskowitz-Pedersen style): long the 3 currencies whose real
    exchange rate fell most over 5 years, short the 3 that rose most; monthly.
 D. Time-series trend: each of 7 currencies vs USD, sign of 12-month return,
    inverse-volatility weights, monthly.
 E. 50/50 value + trend (equal risk).
"""
from __future__ import annotations

import json
import math
import os
import sys
import urllib.request

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import macrofx_engine as eng  # noqa: E402
import backtest_macrofx as bt  # noqa: E402

FX_URL = bt.DATA_URL
CPI_URL = "https://raw.githubusercontent.com/datasets/cpi/main/data/cpi.csv"
COUNTRY = {"EUR": "Euro", "GBP": "United Kingdom", "JPY": "Japan", "CHF": "Switzerland",
           "CAD": "Canada", "AUD": "Australia", "NZD": "New Zealand"}
CPI_CODE = {"USD": "USA", "EUR": "EMU", "GBP": "GBR", "JPY": "JPN", "CHF": "CHE", "CAD": "CAN", "AUD": "AUS", "NZD": "NZL"}
COST = 0.0002  # 2 bp per side of turnover (about 1 pip on majors)


def fetch(url, path):
    if not os.path.exists(path):
        urllib.request.urlretrieve(url, path)
    return path


def per_usd(fx_path):
    raw = pd.read_csv(fx_path)
    raw["Date"] = pd.to_datetime(raw["Date"])
    cols = {}
    for c, country in COUNTRY.items():
        s = raw[raw["Country"] == country].set_index("Date")["Exchange rate"].astype(float)
        cols[c] = s[s > 0]
    return pd.DataFrame(cols).sort_index().ffill(limit=3)


def usd_value_of(u):
    """Price of 1 unit of each currency in USD (up = currency strengthens)."""
    v = 1.0 / u
    v["USD"] = 1.0
    return v


def stats(r, periods=12):
    r = pd.Series(r).dropna()
    if len(r) < 12:
        return {}
    eq = (1 + r).cumprod()
    yrs = len(r) / periods
    sd = r.std(ddof=1)
    return {"months": int(len(r)), "cagr": float(eq.iloc[-1] ** (1 / yrs) - 1),
            "ann_vol": float(sd * math.sqrt(periods)),
            "sharpe": float(r.mean() / sd * math.sqrt(periods)) if sd > 0 else None,
            "t_stat": float(r.mean() / (sd / math.sqrt(len(r)))) if sd > 0 else None,
            "max_dd": float((eq / eq.cummax() - 1).min())}


def split(r, cut="2013-01-01"):
    r = pd.Series(r).dropna()
    return {"all": stats(r), "2000-2012": stats(r[r.index < cut]), "2013-2026": stats(r[r.index >= cut])}


def long_short(monthly_px, signal, n=3):
    """Each month: long top-n, short bottom-n by signal (known at month end), equal weight."""
    rets = monthly_px.pct_change().shift(-1)  # next month's return, aligned to signal date
    out, prev = {}, None
    for d in signal.index:
        s = signal.loc[d].dropna()
        if len(s) < 2 * n or d not in rets.index:
            continue
        s = s.sort_values()
        w = pd.Series(0.0, index=monthly_px.columns)
        w[s.index[-n:]] = 1.0 / n
        w[s.index[:n]] = -1.0 / n
        turn = (w - (prev if prev is not None else 0)).abs().sum()
        prev = w
        r = (w * rets.loc[d]).sum()
        if not np.isnan(r):
            out[d] = r - turn * COST
    s = pd.Series(out)
    s.index = s.index + pd.offsets.MonthEnd(1)  # label by the month the return is earned
    return s


def ts_trend(monthly_px, lookback=12):
    rets = monthly_px.pct_change()
    fwd = rets.shift(-1)
    vol = rets.rolling(36, min_periods=12).std()
    out, prev = {}, None
    cols = [c for c in monthly_px.columns if c != "USD"]
    for i, d in enumerate(monthly_px.index):
        if i < lookback:
            continue
        sig = np.sign(monthly_px.loc[d, cols] / monthly_px.iloc[i - lookback][cols] - 1)
        iv = 1 / vol.loc[d, cols]
        if iv.isna().any():
            continue
        w = sig * iv / iv.sum()
        turn = (w - (prev if prev is not None else 0)).abs().sum()
        prev = w
        r = (w * fwd.loc[d, cols]).sum()
        if not np.isnan(r):
            out[d] = r - turn * COST
    s = pd.Series(out)
    s.index = s.index + pd.offsets.MonthEnd(1)
    return s


def real_value_signal(val_m, cpi_path):
    """Value score = -(5y change in real exchange rate vs USD). Annual inflation, interpolated monthly."""
    cpi = pd.read_csv(cpi_path)
    idx = {}
    for c, code in CPI_CODE.items():
        s = cpi[cpi["Country Code"] == code].set_index("Year")["CPI"].astype(float).sort_index()
        if c == "EUR":  # euro area before its series starts: Germany as proxy
            de = cpi[cpi["Country Code"] == "DEU"].set_index("Year")["CPI"].astype(float)
            s = s.combine_first(de)
        level = (1 + s / 100).cumprod()
        last = level.index.max()
        for y in range(last + 1, 2027):  # carry the latest inflation forward (2025-26 not published yet)
            level.loc[y] = level.loc[y - 1] * (1 + s.iloc[-1] / 100)
        ts = pd.Series(level.values, index=pd.to_datetime([f"{y}-12-31" for y in level.index]))
        idx[c] = ts.resample("ME").interpolate("linear")
    # Lag 12 months: a year's CPI is only published after the year ends (no look-ahead).
    p = pd.DataFrame(idx).reindex(val_m.index).interpolate(limit_direction="both").shift(12)
    # Real value of each currency in USD terms: nominal USD value * (local price level / US price level)
    real = val_m * p.div(p["USD"], axis=0)
    return -(real / real.shift(60) - 1)


def engine_check(fx_path):
    """Run the live v1.1 engine on 1974-1999 with the 7 non-euro currencies."""
    u = per_usd(fx_path)
    u = u[(u.index >= "1973-01-01") & (u.index < "2000-01-01")].drop(columns=["EUR"]).dropna()
    u["USD"] = 1.0
    cur7 = ["USD", "GBP", "JPY", "CHF", "CAD", "AUD", "NZD"]
    pairs7 = [p for p in eng.DEFAULT_PAIRS if "EUR" not in p]
    orig = (eng.CURRENCIES, bt.DEFAULT_PAIRS)
    eng.CURRENCIES = cur7
    bt.DEFAULT_PAIRS = pairs7
    try:
        closes = pd.DataFrame({p: u[p[3:]] / u[p[:3]] for p in pairs7})
        factors = eng.currency_factor_returns(closes)
        idx = closes.index
        fridays = sorted({idx[idx <= d].max() for d in pd.date_range("1975-01-01", "1999-12-31", freq="W-FRI")})
        bt._SNAP_CACHE.clear()
        weekly, trades, wi = bt.simulate(closes, factors, fridays, cost_pips=0.0)
    finally:
        eng.CURRENCIES, bt.DEFAULT_PAIRS = orig
        bt._SNAP_CACHE.clear()
    m = bt.metrics(weekly, trades, wi)
    halves = {"1975-1987": bt.metrics([w for w in weekly if w["date"] < "1988"], [], 0),
              "1988-1999": bt.metrics([w for w in weekly if w["date"] >= "1988"], [], 0)}
    return {"all": m, **halves}


def main():
    fx_path = fetch(FX_URL, "/tmp/macrofx_fx_daily.csv") if len(sys.argv) < 2 else sys.argv[1]
    cpi_path = fetch(CPI_URL, "/tmp/macrofx_cpi.csv") if len(sys.argv) < 3 else sys.argv[2]
    out = {}

    out["A_engine_check_1975_1999"] = engine_check(fx_path)
    a = out["A_engine_check_1975_1999"]["all"]
    print(f"A engine v1.1 1975-1999 (7 ccy, no costs): CAGR {a['cagr']:+.2%} Sharpe {a['sharpe']:+.2f} t {a['t_stat']:+.2f}", flush=True)

    u = per_usd(fx_path)
    val = usd_value_of(u)
    val_m = val.resample("ME").last()
    # Pre-1999 B check on 7 currencies, then 2000-2026 on 8
    val7 = val_m.drop(columns=["EUR"])
    mom3_7 = val7 / val7.shift(3) - 1
    b_old = long_short(val7[val7.index < "2000-01-01"], mom3_7[mom3_7.index < "2000-01-01"], n=2)
    val8 = val_m[val_m.index >= "1999-01-31"]
    mom3 = val8 / val8.shift(3) - 1
    b_new = long_short(val8, mom3, n=3)
    b_new = b_new[b_new.index >= "2000-01-01"]
    out["B_momentum_3m_1975_1999"] = stats(b_old)
    out["B_momentum_3m_2000_2026"] = split(b_new)

    value = real_value_signal(val_m, cpi_path)
    v_new = long_short(val_m[val_m.index >= "1999-01-31"], value[value.index >= "1999-01-31"], n=3)
    v_new = v_new[v_new.index >= "2000-01-01"]
    out["C_value_5y_real_2000_2026"] = split(v_new)

    t_new = ts_trend(val_m[val_m.index >= "1997-01-31"], 12)
    t_new = t_new[t_new.index >= "2000-01-01"]
    out["D_trend_12m_2000_2026"] = split(t_new)

    both = pd.concat([v_new / v_new.std(), t_new / t_new.std()], axis=1).dropna().mean(axis=1)
    both = both * (v_new.std())  # rescale to value's risk level for readability
    out["E_value_plus_trend_2000_2026"] = split(both)

    for k, v in out.items():
        if k.startswith("A"):
            continue
        a = v.get("all", v)
        print(f"{k:32s} CAGR {a['cagr']:+.2%} vol {a['ann_vol']:.1%} Sharpe {a['sharpe']:+.2f} t {a['t_stat']:+.2f} MaxDD {a['max_dd']:.0%}", flush=True)
        if "2000-2012" in v:
            print(f"{'':32s} 2000-12 Sharpe {v['2000-2012']['sharpe']:+.2f} | 2013-26 Sharpe {v['2013-2026']['sharpe']:+.2f}", flush=True)
    corr = pd.concat({"value": v_new, "trend": t_new, "momentum": b_new}, axis=1).dropna().corr()
    out["correlations"] = {f"{i}-{j}": round(float(corr.loc[i, j]), 2) for i in corr.index for j in corr.columns if i < j}
    print("correlations", out["correlations"])
    out["meta"] = {"spot_only": True, "carry_tested": False, "cost_per_side": COST,
                   "notes": "Carry not testable without interest-rate history; all returns exclude interest differentials. "
                            "CPI is annual (World Bank), lagged 12 months, with 2025-26 carried forward; Germany proxies the euro area before 1999."}
    path = os.path.join(ROOT, "docs", "backtest", "research_results.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print("wrote", path)


if __name__ == "__main__":
    main()

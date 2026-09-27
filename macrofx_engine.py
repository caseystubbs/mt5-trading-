from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple
import math
import numpy as np
import pandas as pd

CURRENCIES = ["USD","EUR","GBP","JPY","CHF","CAD","AUD","NZD"]
HORIZONS = {21:0.15, 63:0.30, 126:0.35, 252:0.20}
MIN_AGREEMENT = 3
MAX_POSITIONS = 2
MIN_ABS_PAIR_SCORE = 0.50

DEFAULT_PAIRS = [
    "EURUSD","GBPUSD","AUDUSD","NZDUSD","USDJPY","USDCAD","USDCHF",
    "EURGBP","EURJPY","GBPJPY","AUDJPY","CADJPY","EURAUD","GBPAUD"
]

@dataclass
class Target:
    symbol: str
    direction: str
    lots: float
    score: float
    reason: str

def split_pair(pair: str) -> Tuple[str,str]:
    pair = pair.upper().replace(".","").replace("-","")
    if len(pair) < 6:
        raise ValueError(f"Invalid pair: {pair}")
    return pair[:3], pair[3:6]

def currency_factor_returns(close_df: pd.DataFrame) -> pd.DataFrame:
    pair_returns = close_df.pct_change()
    cidx = {c:i for i,c in enumerate(CURRENCIES)}
    out, dates = [], []
    for dt, row in pair_returns.iterrows():
        A, b = [], []
        for pair, ret in row.dropna().items():
            base, quote = split_pair(str(pair))
            if base not in cidx or quote not in cidx:
                continue
            x = np.zeros(len(CURRENCIES))
            x[cidx[base]] = 1.0
            x[cidx[quote]] = -1.0
            A.append(x)
            b.append(float(ret))
        if len(A) < 3:
            continue
        A.append(np.ones(len(CURRENCIES)))
        b.append(0.0)
        sol, *_ = np.linalg.lstsq(np.vstack(A), np.asarray(b), rcond=None)
        out.append(sol)
        dates.append(dt)
    return pd.DataFrame(out, index=pd.DatetimeIndex(dates), columns=CURRENCIES).sort_index()

def _annualized_vol(s: pd.Series, lookback: int = 60) -> float:
    x = s.dropna().tail(lookback)
    if len(x) < 20:
        return float("nan")
    return float(x.std(ddof=1) * math.sqrt(252))

def build_snapshot(close_df: pd.DataFrame) -> pd.DataFrame:
    factors = currency_factor_returns(close_df)
    if factors.empty:
        return pd.DataFrame()
    wealth = (1.0 + factors.fillna(0.0)).cumprod()
    rows = []
    for c in CURRENCIES:
        vol = _annualized_vol(factors[c], 60)
        if not np.isfinite(vol) or vol <= 0:
            continue
        moms = {}
        signs = []
        score = 0.0
        for h, w in HORIZONS.items():
            if len(wealth) <= h:
                moms[h] = float("nan")
                continue
            r = float(wealth[c].iloc[-1] / wealth[c].iloc[-1-h] - 1.0)
            m = r / vol
            moms[h] = m
            score += w * m
            signs.append(1 if m > 0 else -1 if m < 0 else 0)
        nonzero = [x for x in signs if x != 0]
        pos = sum(x > 0 for x in nonzero)
        neg = sum(x < 0 for x in nonzero)
        agreement = max(pos, neg)
        rows.append({
            "currency": c,
            "score": float(score),
            "agreement": int(agreement),
            "ann_vol": vol,
            **{f"m{h}": moms.get(h, float("nan")) for h in HORIZONS}
        })
    return pd.DataFrame(rows).sort_values("score", ascending=False).reset_index(drop=True)

def pair_scores(snapshot: pd.DataFrame, available_pairs: List[str]) -> pd.DataFrame:
    if snapshot.empty:
        return pd.DataFrame()
    s = snapshot.set_index("currency")
    sd = float(s["score"].std(ddof=0))
    z = (s["score"] - s["score"].mean()) / (sd if sd > 0 else 1.0)
    rows = []
    for pair in available_pairs:
        try:
            base, quote = split_pair(pair)
        except Exception:
            continue
        if base not in s.index or quote not in s.index:
            continue
        divergence = float(z[base] - z[quote])
        a1 = int(s.loc[base, "agreement"])
        a2 = int(s.loc[quote, "agreement"])
        opposite = np.sign(float(s.loc[base,"score"])) != np.sign(float(s.loc[quote,"score"]))
        eligible = a1 >= MIN_AGREEMENT and a2 >= MIN_AGREEMENT and bool(opposite)
        agreement = min(a1, a2) / 4.0
        liquidity = 1.0 if "USD" in (base,quote) else 0.8
        pair_score = (
            0.50 * divergence +
            0.20 * np.sign(divergence) * agreement +
            0.15 * np.sign(divergence) * liquidity +
            0.15 * np.sign(divergence) * agreement
        )
        rows.append({
            "symbol": pair,
            "base": base,
            "quote": quote,
            "pair_score": float(pair_score),
            "abs_score": abs(float(pair_score)),
            "eligible": eligible,
            "direction": "LONG" if pair_score > 0 else "SHORT",
            "base_score": float(s.loc[base,"score"]),
            "quote_score": float(s.loc[quote,"score"]),
            "agreement": float(agreement),
        })
    return pd.DataFrame(rows).sort_values("abs_score", ascending=False).reset_index(drop=True) if rows else pd.DataFrame()

def choose_targets(snapshot: pd.DataFrame, available_pairs: List[str], min_lot: float = 0.01) -> List[Target]:
    ps = pair_scores(snapshot, available_pairs)
    if ps.empty:
        return []
    selected: List[Target] = []
    used_currencies = set()
    for _, r in ps.iterrows():
        if not bool(r["eligible"]) or float(r["abs_score"]) < MIN_ABS_PAIR_SCORE:
            continue
        base, quote = str(r["base"]), str(r["quote"])
        if selected and (base in used_currencies or quote in used_currencies):
            continue
        direction = str(r["direction"])
        reason = (
            f"{base} score {float(r['base_score']):+.3f} vs "
            f"{quote} score {float(r['quote_score']):+.3f}; "
            f"pair score {float(r['pair_score']):+.3f}; "
            f"multi-horizon agreement {float(r['agreement']):.2f}"
        )
        selected.append(Target(
            symbol=str(r["symbol"]),
            direction=direction,
            lots=float(min_lot),
            score=float(r["pair_score"]),
            reason=reason,
        ))
        used_currencies.update([base, quote])
        if len(selected) >= MAX_POSITIONS:
            break
    return selected

def performance_metrics(equity_rows: pd.DataFrame) -> Dict[str,float]:
    if equity_rows.empty or "equity" not in equity_rows:
        return {}
    e = equity_rows.dropna(subset=["equity"]).copy()
    if len(e) < 2:
        return {"ending_equity": float(e["equity"].iloc[-1]) if len(e) else float("nan")}
    e = e.sort_values("captured_at")
    eq = e["equity"].astype(float)
    ret = eq.pct_change().dropna()
    peak = eq.cummax()
    dd = eq / peak - 1.0
    sharpe = float(ret.mean()/ret.std(ddof=1)*math.sqrt(252)) if len(ret)>2 and ret.std(ddof=1)>0 else float("nan")
    return {
        "ending_equity": float(eq.iloc[-1]),
        "total_return": float(eq.iloc[-1]/eq.iloc[0]-1.0),
        "max_drawdown": float(dd.min()),
        "sharpe": sharpe,
    }

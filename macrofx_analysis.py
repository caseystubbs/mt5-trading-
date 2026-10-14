"""MacroFX system analysis: turns the recorded feedback into findings.

Pure functions over data the system already stores (fills, trades from the
feedback layer, weekly runs, latest prices). Read-only; no strategy changes.
Every finding states its sample size, because a handful of trades is noise.
"""
from __future__ import annotations

from datetime import datetime
from statistics import mean
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
MIN_TRADES_TO_JUDGE = 30          # closed model trades before signal conclusions mean anything
MODEL_OPEN_NOTES = {"target_open", "target_reconciliation"}
MODEL_CLOSE_REASONS = {"target_removed", "signal_reversed", "drawdown_kill"}


def _f(v, d=0.0):
    try:
        return float(v) if v is not None else d
    except Exception:
        return d


def _when(v) -> Optional[datetime]:
    if v is None:
        return None
    if isinstance(v, datetime):
        return v
    try:
        return datetime.fromisoformat(str(v).replace("Z", "+00:00"))
    except Exception:
        return None


def execution_window(ts) -> str:
    """Weekend reopen = Sunday ET (the FX market reopens 5 PM ET Sunday)."""
    t = _when(ts)
    if t is None:
        return "unknown"
    t = t.astimezone(ET)
    return "Sunday reopen" if t.weekday() == 6 else "Weekday"


def usd_per_quote_unit(symbol: str, prices: Dict[str, float]) -> Optional[float]:
    """Value in USD of 1 unit of the pair's quote currency, from latest closes."""
    q = symbol[3:6]
    if q == "USD":
        return 1.0
    if f"USD{q}" in prices and prices[f"USD{q}"] > 0:
        return 1.0 / prices[f"USD{q}"]
    if f"{q}USD" in prices:
        return prices[f"{q}USD"]
    return None


def spread_cost_usd(symbol: str, spread_points: float, lots: float, prices: Dict[str, float]) -> Optional[float]:
    """Approximate cost of crossing the spread once. Points are 0.00001 (0.001 for JPY quotes)."""
    if not spread_points:
        return 0.0
    point = 0.001 if symbol[3:6] == "JPY" else 0.00001
    conv = usd_per_quote_unit(symbol, prices)
    if conv is None:
        return None
    cost = spread_points * point * lots * 100000 * conv
    # Sanity guard: a single spread crossing at <=0.01 lots never costs more than a few dollars.
    # Anything wildly larger means the conversion price is bad, so treat it as unpriced.
    if cost > 50 * max(lots / 0.01, 1):
        return None
    return cost


def _origin(t: Dict[str, Any], fills_by_ticket: Dict[int, List[Dict[str, Any]]]) -> str:
    opens = [f for f in fills_by_ticket.get(int(t["ticket"]), []) if str(f.get("action", "")).startswith("OPEN")]
    note = (opens[0].get("notes") if opens else "") or ""
    reason = t.get("exit_reason") or ""
    if t.get("status") == "CLOSED" and reason and reason not in MODEL_CLOSE_REASONS:
        return "test/manual"
    if note in MODEL_OPEN_NOTES:
        return "model"
    return "test/manual" if note else "model"


def analyze(fills: List[Dict[str, Any]], trades: List[Dict[str, Any]], summary: Dict[str, Any],
            runs: List[Dict[str, Any]], prices: Dict[str, float], equity_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    fills_by_ticket: Dict[int, List[Dict[str, Any]]] = {}
    for f in fills:
        fills_by_ticket.setdefault(int(f.get("ticket") or 0), []).append(f)

    # ---------- execution costs by window ----------
    windows: Dict[str, Dict[str, Any]] = {}
    unknown_cost = 0
    for f in fills:
        sp = _f(f.get("spread_points"))
        if sp <= 0:
            continue  # early fills did not record spread
        w = execution_window(f.get("captured_at"))
        c = spread_cost_usd(str(f.get("symbol", "")), sp, _f(f.get("lots"), 0.01), prices)
        b = windows.setdefault(w, {"window": w, "fills": 0, "spreads": [], "cost": 0.0})
        b["fills"] += 1
        b["spreads"].append(sp)
        if c is None:
            unknown_cost += 1
        else:
            b["cost"] += c
    exec_rows = []
    for w in ("Sunday reopen", "Weekday", "unknown"):
        if w in windows:
            b = windows[w]
            exec_rows.append({"window": w, "fills": b["fills"], "avg_spread_points": mean(b["spreads"]),
                              "max_spread_points": max(b["spreads"]), "est_spread_cost": b["cost"],
                              "avg_cost_per_fill": b["cost"] / b["fills"] if b["fills"] else 0.0})
    sun = next((r for r in exec_rows if r["window"] == "Sunday reopen"), None)
    wk = next((r for r in exec_rows if r["window"] == "Weekday"), None)
    spread_ratio = (sun["avg_spread_points"] / wk["avg_spread_points"]) if sun and wk and wk["avg_spread_points"] else None

    # ---------- trades: model vs test/manual ----------
    rows = []
    for t in trades:
        origin = _origin(t, fills_by_ticket)
        mfe, net = _f(t.get("mfe_net")), _f(t.get("net_pnl"))
        has_path = int(t.get("position_samples") or 0) > 1
        rows.append({**t, "origin": origin,
                     "giveback": (mfe - net) if (t.get("status") == "CLOSED" and has_path and mfe > net) else None,
                     "has_path": has_path})
    model_closed = [r for r in rows if r["origin"] == "model" and r["status"] == "CLOSED"]
    all_closed = [r for r in rows if r["status"] == "CLOSED"]

    def perf(ts):
        if not ts:
            return {"n": 0}
        nets = [_f(t["net_pnl"]) for t in ts]
        wins = [x for x in nets if x > 0]
        losses = [x for x in nets if x < 0]
        gl = abs(sum(losses))
        return {"n": len(ts), "net": sum(nets), "win_rate": len(wins) / len(ts),
                "avg_win": mean(wins) if wins else None, "avg_loss": mean(losses) if losses else None,
                "profit_factor": (sum(wins) / gl) if gl > 0 else None,
                "best": max(nets), "worst": min(nets),
                "avg_days": mean(_f(t["holding_hours"]) / 24 for t in ts)}

    # ---------- costs ----------
    swap_closed = sum(_f(t.get("swap")) for t in all_closed)
    comm_closed = sum(_f(t.get("commission")) for t in all_closed)
    gross_closed = sum(_f(t.get("pnl")) for t in all_closed)
    est_spread_total = sum(r["est_spread_cost"] for r in exec_rows)

    # ---------- signal quality (needs entry scores) ----------
    scored = [r for r in model_closed if r.get("entry_signal_score") not in (None, 0, 0.0)]
    with_path = [r for r in all_closed if r["has_path"]]

    # ---------- model stability ----------
    runs_sorted = sorted(runs, key=lambda r: str(r.get("week_ending")))
    turnover = []
    for prev, cur in zip(runs_sorted, runs_sorted[1:]):
        p = {(t["symbol"], t["direction"]) for t in (prev.get("targets_json") or [])}
        c = {(t["symbol"], t["direction"]) for t in (cur.get("targets_json") or [])}
        turnover.append({"week_ending": str(cur.get("week_ending")), "kept": len(p & c),
                         "changed": len(c - p), "targets": len(c)})
    avg_changes = mean(x["changed"] for x in turnover) if turnover else None

    # ---------- equity ----------
    closes = [_f(e.get("close_equity")) for e in equity_rows if _f(e.get("close_equity")) > 0]
    peak, dd = 0.0, 0.0
    for c in closes:
        peak = max(peak, c)
        dd = min(dd, c / peak - 1)

    # ---------- findings ----------
    n_model = len(model_closed)
    findings: List[Dict[str, Any]] = []

    def add(level, title, detail, evidence):
        findings.append({"level": level, "title": title, "detail": detail, "evidence": evidence})

    add("info" if n_model >= MIN_TRADES_TO_JUDGE else "warn",
        "Sample size" + (" is enough to start judging the signal" if n_model >= MIN_TRADES_TO_JUDGE
                         else " is far too small to judge the signal"),
        f"{n_model} closed trades came from the model (target needed: about {MIN_TRADES_TO_JUDGE}). "
        "Until then, results reflect luck and costs more than skill. A backtest (Upgrades #6) is the fast way to get a real sample.",
        f"{n_model} model trades, {len(all_closed) - n_model} closed by tests or by hand")
    if spread_ratio and spread_ratio >= 3:
        add("bad", "Trading at the Sunday reopen is the biggest cost",
            f"Spreads at the Sunday reopen average {sun['avg_spread_points']:.0f} points versus {wk['avg_spread_points']:.0f} on weekdays "
            f"({spread_ratio:.0f}× wider). Estimated spread paid at the reopen: ${sun['est_spread_cost']:.2f} over {sun['fills']} fills.",
            "Moving execution to Monday morning (Upgrades #2) removes most of this without touching the signal.")
    net_closed_all = sum(_f(t["net_pnl"]) for t in all_closed)
    if est_spread_total and abs(net_closed_all) < est_spread_total:
        add("warn", "Costs are larger than the results so far",
            f"Estimated spread paid (${est_spread_total:.2f}) is bigger than total realized profit (${net_closed_all:+.2f}).",
            "At 0.01 lots, small fixed costs dominate; that's normal early, but it hides whether the signal works.")
    if avg_changes is not None:
        lvl = "warn" if avg_changes >= 1 else "info"
        add(lvl, "Positions rotate most weeks" if avg_changes >= 1 else "Positions are fairly stable week to week",
            f"On average {avg_changes:.1f} of 2 targets change per weekly run ({len(turnover)} run-to-run comparisons). "
            "Each change pays two spreads.",
            "A rotation buffer (Upgrades #7) would keep a held pair unless a replacement is clearly better.")
    if not scored:
        add("warn", "Can't yet test whether higher scores win more",
            "Entry signal scores are missing on most fills (remote-command fills record 0).",
            "Fix the records first (Upgrades #3).")
    gb = [r["giveback"] for r in with_path if r["giveback"] is not None]
    if not with_path:
        add("info", "Best-point and worst-point tracking has no closed history yet",
            "Closed trades have too few position snapshots to measure how much open profit was given back.",
            "This fills in automatically as the EA keeps uploading positions every minute.")
    elif gb:
        add("info", "Open profit given back before exit",
            f"Closed trades gave back ${mean(gb):.2f} on average from their best point.",
            f"{len(gb)} trades with full price history")
    if swap_closed:
        add("info", "Swap has been " + ("a small tailwind" if swap_closed > 0 else "a cost"),
            f"Swap on closed trades: ${swap_closed:+.2f}. The model does not consider swap when picking (Upgrades #9).",
            f"{len(all_closed)} closed trades")

    # ---------- research questions from the weekly review ----------
    def status(ok_n, need):
        return "Enough data" if ok_n >= need else f"Waiting for data ({ok_n}/{need})"
    research = [
        {"question": "Do higher absolute entry scores produce better results?", "status": status(len(scored), 20),
         "note": "Needs entry scores on every fill (Upgrades #3)."},
        {"question": "Is open profit (MFE) repeatedly given back before the weekly exit?", "status": status(len(gb), 15),
         "note": "Measured from per-minute position snapshots."},
        {"question": "Do losses cluster tightly enough to justify a volatility stop?", "status": status(len(with_path), 20),
         "note": "Upgrades #10."},
        {"question": "How much do spread, slippage, swap and commission cost versus the signal?",
         "status": "Measured" if exec_rows else "Waiting for data", "note": "See Costs below."},
    ]

    return {
        "min_trades_to_judge": MIN_TRADES_TO_JUDGE,
        "model_closed": n_model,
        "performance": {"model": perf(model_closed), "all": perf(all_closed)},
        "execution": exec_rows,
        "spread_ratio": spread_ratio,
        "costs": {"gross_closed": gross_closed, "swap_closed": swap_closed, "commission_closed": comm_closed,
                  "est_spread_total": est_spread_total, "net_closed": net_closed_all,
                  "unpriced_fills": unknown_cost},
        "turnover": turnover,
        "avg_target_changes": avg_changes,
        "max_daily_drawdown": dd,
        "trades": [{k: r.get(k) for k in ("ticket", "symbol", "direction", "status", "origin", "net_pnl", "mae_net",
                                           "mfe_net", "giveback", "entry_signal_score", "holding_hours",
                                           "entry_spread_points", "exit_reason")} for r in rows],
        "findings": findings,
        "research": research,
    }

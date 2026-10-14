"""MacroFX dashboard: read-only page + data API.

GET /macrofx                      HTML dashboard (tabs: Overview, This Week,
                                  History, How It Works, Changelog, Upgrades)
GET /api/macrofx/dashboard-data   JSON used by the page (read-only)
GET /api/macrofx/doc/{name}       Markdown docs: rules, upgrades, changelog, devlog

Nothing here writes to the database or sends commands. Secrets and claim
tokens are never returned.
"""
from __future__ import annotations

import json
import math
import os
import re
import time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import markdown as md
import pandas as pd
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse

from macrofx import get_pool
from macrofx_engine import HORIZONS, MAX_POSITIONS, MIN_ABS_PAIR_SCORE, MIN_AGREEMENT, build_snapshot, choose_targets, pair_scores
from macrofx_feedback import build_feedback_snapshot
from macrofx_analysis import analyze

router = APIRouter(tags=["macrofx-dashboard"])

ROOT = os.path.dirname(os.path.abspath(__file__))
ACCOUNT = os.environ.get("MACROFX_DASHBOARD_ACCOUNT", "1041307")
MAGIC = 26092601
ET = ZoneInfo("America/New_York")
WEEKLY_CRON_UTC = (5, 1, 0)  # Saturday 01:00 UTC (service cron "0 1 * * 6")
_preview_cache: dict = {"at": 0.0, "data": None}


def _clean(v):
    if isinstance(v, datetime):
        return v.isoformat()
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return None
    if hasattr(v, "isoformat"):
        return v.isoformat()
    if isinstance(v, (list, tuple)):
        return [_clean(x) for x in v]
    if isinstance(v, dict):
        return {k: _clean(x) for k, x in v.items()}
    return v


def _row(r):
    return {k: _clean(v) for k, v in dict(r).items() if k != "claim_token"}


def _json(v):
    if isinstance(v, str):
        try:
            return json.loads(v)
        except Exception:
            return v
    return v


def next_weekly_run(now: datetime) -> datetime:
    wd, hour, minute = WEEKLY_CRON_UTC
    cand = now.replace(hour=hour, minute=minute, second=0, microsecond=0) + timedelta(days=(wd - now.weekday()) % 7)
    if cand <= now:
        cand += timedelta(days=7)
    return cand


async def _table_exists(conn, name: str) -> bool:
    return bool(await conn.fetchval("SELECT to_regclass($1)", "public." + name))


async def _preview(pool):
    """What the model would pick if it ran right now (read-only, cached 10 min)."""
    if _preview_cache["data"] is not None and time.time() - _preview_cache["at"] < 600:
        return _preview_cache["data"]
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT symbol,bar_date,close FROM macrofx_daily_bars WHERE bar_date >= $1 ORDER BY bar_date,symbol",
            datetime.now(ET).date() - timedelta(days=520))
    if not rows:
        return {"available": False, "reason": "No daily bars uploaded yet"}
    df = pd.DataFrame([dict(r) for r in rows])
    close_df = df.pivot_table(index="bar_date", columns="symbol", values="close", aggfunc="last").sort_index()
    close_df.index = pd.to_datetime(close_df.index)
    available = [c for c in close_df.columns if close_df[c].notna().sum() >= 260]
    close_df = close_df[available]
    if len(available) < 6:
        return {"available": False, "reason": f"Only {len(available)} pairs have 260+ daily bars"}
    snap = build_snapshot(close_df)
    ps = pair_scores(snap, available)
    targets = choose_targets(snap, available, min_lot=0.01)
    picked = {t.symbol for t in targets}
    data = {
        "available": True,
        "as_of_bar": str(close_df.index.max().date()),
        "currencies": [_clean(r) for r in json.loads(snap.to_json(orient="records"))],
        "pairs": [{**_clean(r), "picked": r["symbol"] in picked}
                  for r in json.loads(ps.to_json(orient="records"))] if not ps.empty else [],
        "targets": [_clean(t.__dict__) for t in targets],
    }
    _preview_cache.update(at=time.time(), data=data)
    return data


async def dashboard_data():
    pool = await get_pool()
    now = datetime.now(timezone.utc)
    out: dict = {"generated_at": now.isoformat(), "account_id": ACCOUNT}
    async with pool.acquire() as conn:
        hb = await conn.fetchrow("""SELECT captured_at,balance,equity,free_margin,is_demo,ea_version,broker
            FROM macrofx_heartbeats WHERE account_id=$1 ORDER BY captured_at DESC LIMIT 1""", ACCOUNT)
        first = await conn.fetchrow("""SELECT captured_at,balance FROM macrofx_heartbeats
            WHERE account_id=$1 AND balance>0 ORDER BY captured_at LIMIT 1""", ACCOUNT)
        out["account"] = None
        if hb:
            age = (now - hb["captured_at"]).total_seconds()
            out["account"] = {**_row(hb), "age_seconds": age, "online": age < 180,
                              "start_balance": float(first["balance"]) if first else None,
                              "start_at": _clean(first["captured_at"]) if first else None}

        # Remote control state
        settings = None
        if await _table_exists(conn, "macrofx_v2_settings"):
            settings = await conn.fetchrow("""SELECT enabled,pause_entries,max_positions,max_lot_per_pair,
                max_spread_points,slippage_points,revision,updated_at FROM macrofx_v2_settings WHERE account_id=$1""", ACCOUNT)
        commands = []
        if await _table_exists(conn, "macrofx_v2_commands"):
            commands = await conn.fetch("""SELECT command_id,action,symbol,ticket,lots,status,reason,created_at,
                claimed_at,acknowledged_at,expires_at,result FROM macrofx_v2_commands
                WHERE account_id=$1 ORDER BY created_at DESC LIMIT 40""", ACCOUNT)
        out["remote"] = {
            "settings": _row(settings) if settings else None,
            "enabled": bool(settings and settings["enabled"]),
            "unresolved": sum(1 for c in commands if c["status"] in ("PENDING", "CLAIMED")
                              and (c["status"] == "CLAIMED" or c["expires_at"] > now)),
        }
        out["commands"] = [_row(c) for c in commands]

        # Open positions = latest complete snapshot, enriched with latest P&L/swap rows
        positions = []
        snap_at = None
        if await _table_exists(conn, "macrofx_v2_position_snapshots"):
            snap = await conn.fetchrow("SELECT captured_at,positions_json FROM macrofx_v2_position_snapshots WHERE account_id=$1", ACCOUNT)
            if snap:
                snap_at = snap["captured_at"]
                tickets = [int(p["ticket"]) for p in _json(snap["positions_json"]) if int(p.get("magic", 0)) == MAGIC]
                if tickets:
                    rows = await conn.fetch("""SELECT DISTINCT ON (ticket) ticket,symbol,side,lots,open_price,current_price,
                        pnl,swap,commission,captured_at FROM macrofx_positions
                        WHERE account_id=$1 AND ticket = ANY($2::bigint[]) ORDER BY ticket,captured_at DESC""", ACCOUNT, tickets)
                    opened = {r["ticket"]: r for r in await conn.fetch("""SELECT DISTINCT ON (ticket) ticket,captured_at,
                        signal_score,notes FROM macrofx_fills WHERE account_id=$1 AND ticket = ANY($2::bigint[])
                        AND action LIKE 'OPEN%' ORDER BY ticket,captured_at""", ACCOUNT, tickets)}
                    for r in rows:
                        o = opened.get(r["ticket"])
                        held = (now - o["captured_at"]).total_seconds() / 86400 if o else None
                        swap = float(r["swap"] or 0)
                        positions.append({**_row(r),
                                          "opened_at": _clean(o["captured_at"]) if o else None,
                                          "days_held": held,
                                          "swap_per_day": (swap / held) if held and held >= 1 else None,
                                          "net": float(r["pnl"] or 0) + swap + float(r["commission"] or 0)})
        out["positions"] = positions
        out["positions_snapshot_at"] = _clean(snap_at)

        # Weekly runs + targets
        runs = await conn.fetch("""SELECT id,week_ending,created_at,strategy_version,strongest_currency,weakest_currency,
            targets_json FROM macrofx_weekly_runs ORDER BY week_ending DESC LIMIT 30""")
        out["runs"] = [{**_row(r), "targets_json": _json(r["targets_json"])} for r in runs]
        latest = await conn.fetchrow("""SELECT id,week_ending,created_at,strategy_version,strongest_currency,
            weakest_currency,snapshot_json,targets_json FROM macrofx_weekly_runs ORDER BY week_ending DESC LIMIT 1""")
        out["latest_run"] = ({**_row(latest), "snapshot_json": _json(latest["snapshot_json"]),
                              "targets_json": _json(latest["targets_json"])} if latest else None)
        active = await conn.fetch("""SELECT symbol,direction,lots,score,reason,expires_at FROM macrofx_targets
            WHERE active=TRUE AND expires_at>NOW() ORDER BY ABS(score) DESC""")
        out["active_targets"] = [_row(t) for t in active]

        # Fills and swap/commission totals
        fills = await conn.fetch("""SELECT captured_at,symbol,ticket,action,lots,requested_price,fill_price,spread_points,
            slippage_points,pnl,swap,commission,signal_score,exit_reason,notes FROM macrofx_fills
            WHERE account_id=$1 ORDER BY captured_at DESC LIMIT 100""", ACCOUNT)
        out["fills"] = [_row(f) for f in fills]
        totals = await conn.fetchrow("""SELECT COALESCE(SUM(pnl) FILTER (WHERE action='CLOSE'),0) pnl,
            COALESCE(SUM(swap) FILTER (WHERE action='CLOSE'),0) swap,
            COALESCE(SUM(commission) FILTER (WHERE action='CLOSE'),0) commission, COUNT(*) FILTER (WHERE action='CLOSE') closes
            FROM macrofx_fills WHERE account_id=$1""", ACCOUNT)
        out["totals"] = _row(totals)

        equity = []
        if await _table_exists(conn, "macrofx_daily_equity"):
            equity = await conn.fetch("""SELECT equity_date,open_equity,high_equity,low_equity,close_equity,close_balance
                FROM macrofx_daily_equity WHERE account_id=$1 ORDER BY equity_date""", ACCOUNT)
        out["equity"] = [_row(e) for e in equity]

        price_rows = await conn.fetch("""SELECT DISTINCT ON (symbol) symbol,close FROM macrofx_daily_bars
            ORDER BY symbol,bar_date DESC""")
        prices = {r["symbol"]: float(r["close"]) for r in price_rows}
        review = await conn.fetchval("SELECT report_markdown FROM macrofx_weekly_runs ORDER BY week_ending DESC LIMIT 1")
        all_fills = await conn.fetch("""SELECT captured_at,symbol,ticket,action,lots,spread_points,notes,exit_reason
            FROM macrofx_fills WHERE account_id=$1 ORDER BY captured_at""", ACCOUNT)

    # Trade-by-trade review (MAE/MFE, holding time, exit reason)
    try:
        fb = await build_feedback_snapshot(pool, ACCOUNT, days=365)
        out["trades"] = _clean(fb.get("trades", []))
        out["trade_summary"] = _clean(fb.get("summary", {}))
    except Exception as e:  # never break the page over the review layer
        out["trades"], out["trade_summary"] = [], {"error": str(e)[:200]}

    try:
        out["analysis"] = _clean(analyze([_row(f) for f in all_fills], out["trades"], out["trade_summary"],
                                         out["runs"], prices, out["equity"]))
    except Exception as e:
        out["analysis"] = {"error": str(e)[:200]}
    out["review_html"] = _md_html(review) if review else None

    nxt = next_weekly_run(now)
    out["schedule"] = {"next_run_utc": nxt.isoformat(), "next_run_et": nxt.astimezone(ET).isoformat()}

    # Difference between what the model wants and what is held
    held = {(p["symbol"][:6], "LONG" if str(p["side"]).upper() in ("BUY", "LONG") else "SHORT") for p in positions}
    want = {(t["symbol"], t["direction"]) for t in out["active_targets"]}
    out["target_diff"] = {
        "to_open": [{"symbol": s, "direction": d} for s, d in sorted(want - held)],
        "to_close": [{"symbol": s, "direction": d} for s, d in sorted(held - want)],
        "matching": [{"symbol": s, "direction": d} for s, d in sorted(want & held)],
    }
    try:
        out["preview"] = await _preview(pool)
    except Exception as e:
        out["preview"] = {"available": False, "reason": str(e)[:200]}
    out["model"] = {"horizons": {str(k): v for k, v in HORIZONS.items()}, "min_agreement": MIN_AGREEMENT,
                    "min_pair_score": MIN_ABS_PAIR_SCORE, "max_positions": MAX_POSITIONS}
    return out


@router.get("/api/macrofx/dashboard-data")
async def dashboard_data_endpoint():
    return await dashboard_data()


_MACRO = re.compile(r"macro\s?fx", re.I)


def _macro_sections(path: str) -> str:
    """Keep only MacroFX-related sections of a shared log file."""
    try:
        text = open(path, encoding="utf-8").read()
    except FileNotFoundError:
        return ""
    blocks, cur = [], []
    for line in text.splitlines():
        if re.match(r"^#{2,3} ", line) and cur:
            blocks.append(cur)
            cur = []
        cur.append(line)
    if cur:
        blocks.append(cur)
    keep = ["\n".join(b) for b in blocks if b and re.match(r"^#{2,3} ", b[0]) and _MACRO.search("\n".join(b))]
    return "\n\n".join(keep)


DOCS = {
    "rules": lambda: open(os.path.join(ROOT, "docs", "MACROFX_RULES.md"), encoding="utf-8").read(),
    "upgrades": lambda: open(os.path.join(ROOT, "docs", "MACROFX_UPGRADES.md"), encoding="utf-8").read(),
    "changelog": lambda: _macro_sections(os.path.join(ROOT, "changelog.md")),
    "devlog": lambda: _macro_sections(os.path.join(ROOT, "DEV_LOG.md")),
}


def _md_html(text: str) -> str:
    # Logs often start a list straight after a paragraph line; markdown needs a blank line there.
    text = re.sub(r"(?m)^(?![-*] |\d+\. |\s|$|#|\|)(.+)\n(?=[-*] |\d+\. )", r"\1\n\n", text)
    return md.markdown(text.replace("<", "&lt;"), extensions=["tables", "fenced_code", "sane_lists"])


@router.get("/api/macrofx/doc/{name}", response_class=PlainTextResponse)
async def doc(name: str, format: str = "md"):
    if name not in DOCS:
        raise HTTPException(404, "Unknown document")
    try:
        text = DOCS[name]() or "_Nothing recorded yet._"
    except FileNotFoundError:
        raise HTTPException(404, "Document not found")
    if format == "html":
        # Repo docs are trusted, but raw HTML in them is escaped anyway.
        return HTMLResponse(_md_html(text))
    return text


@router.get("/macrofx", response_class=HTMLResponse)
async def macrofx_page():
    with open(os.path.join(ROOT, "static", "macrofx_dashboard.html"), encoding="utf-8") as f:
        return f.read()

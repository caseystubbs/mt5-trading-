from __future__ import annotations

import json
import os
from datetime import datetime, timezone, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

import asyncpg
import pandas as pd
from fastapi import APIRouter, HTTPException, Body, Header
from fastapi.responses import PlainTextResponse

from macrofx_engine import build_snapshot, choose_targets, performance_metrics

router = APIRouter(prefix="/api/macrofx", tags=["macrofx"])

DATABASE_URL = os.environ.get("DATABASE_URL", "")
API_KEY = os.environ.get("MACROFX_API_KEY", os.environ.get("EA_API_KEY", ""))
_macro_pool: Optional[asyncpg.Pool] = None

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS macrofx_heartbeats (
    id BIGSERIAL PRIMARY KEY,
    captured_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    account_id TEXT NOT NULL,
    balance DOUBLE PRECISION,
    equity DOUBLE PRECISION,
    free_margin DOUBLE PRECISION,
    is_demo BOOLEAN NOT NULL DEFAULT TRUE,
    ea_version TEXT,
    broker TEXT DEFAULT 'MidasFX'
);
CREATE INDEX IF NOT EXISTS idx_macrofx_heartbeats_time ON macrofx_heartbeats(captured_at);

CREATE TABLE IF NOT EXISTS macrofx_positions (
    id BIGSERIAL PRIMARY KEY,
    captured_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    account_id TEXT NOT NULL,
    symbol TEXT NOT NULL,
    ticket BIGINT,
    side TEXT,
    lots DOUBLE PRECISION,
    open_price DOUBLE PRECISION,
    current_price DOUBLE PRECISION,
    pnl DOUBLE PRECISION,
    swap DOUBLE PRECISION,
    commission DOUBLE PRECISION,
    magic BIGINT
);
CREATE INDEX IF NOT EXISTS idx_macrofx_positions_time ON macrofx_positions(captured_at);

CREATE TABLE IF NOT EXISTS macrofx_fills (
    id BIGSERIAL PRIMARY KEY,
    captured_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    account_id TEXT NOT NULL,
    symbol TEXT NOT NULL,
    ticket BIGINT,
    action TEXT,
    lots DOUBLE PRECISION,
    requested_price DOUBLE PRECISION,
    fill_price DOUBLE PRECISION,
    spread_points DOUBLE PRECISION,
    slippage_points DOUBLE PRECISION,
    pnl DOUBLE PRECISION,
    swap DOUBLE PRECISION,
    commission DOUBLE PRECISION,
    strategy_version TEXT,
    notes TEXT
);
CREATE INDEX IF NOT EXISTS idx_macrofx_fills_time ON macrofx_fills(captured_at);

CREATE TABLE IF NOT EXISTS macrofx_daily_bars (
    symbol TEXT NOT NULL,
    bar_date DATE NOT NULL,
    close DOUBLE PRECISION NOT NULL,
    source TEXT NOT NULL DEFAULT 'midasfx_mt4',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY(symbol, bar_date)
);

CREATE TABLE IF NOT EXISTS macrofx_weekly_runs (
    id BIGSERIAL PRIMARY KEY,
    week_ending DATE NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    strategy_version TEXT NOT NULL,
    strongest_currency TEXT,
    weakest_currency TEXT,
    snapshot_json JSONB NOT NULL,
    targets_json JSONB NOT NULL,
    report_markdown TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS macrofx_targets (
    id BIGSERIAL PRIMARY KEY,
    weekly_run_id BIGINT REFERENCES macrofx_weekly_runs(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    symbol TEXT NOT NULL,
    direction TEXT NOT NULL,
    lots DOUBLE PRECISION NOT NULL,
    score DOUBLE PRECISION,
    reason TEXT,
    active BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE INDEX IF NOT EXISTS idx_macrofx_targets_active ON macrofx_targets(active, expires_at);

CREATE TABLE IF NOT EXISTS macrofx_reconciliation (
    id BIGSERIAL PRIMARY KEY,
    captured_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    account_id TEXT NOT NULL,
    status TEXT NOT NULL,
    details TEXT
);
"""

def _verify(key: str):
    if not API_KEY or key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

async def get_pool() -> asyncpg.Pool:
    global _macro_pool
    if _macro_pool is None:
        if not DATABASE_URL:
            raise RuntimeError("DATABASE_URL is not configured")
        _macro_pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=4)
        async with _macro_pool.acquire() as conn:
            await conn.execute(SCHEMA_SQL)
    return _macro_pool

def _num(v, default=0.0):
    try:
        return float(v)
    except Exception:
        return default

@router.get("/health")
async def macrofx_health():
    pool = await get_pool()
    async with pool.acquire() as conn:
        latest = await conn.fetchrow("SELECT * FROM macrofx_heartbeats ORDER BY captured_at DESC LIMIT 1")
        latest_run = await conn.fetchrow(
            "SELECT week_ending, created_at, strongest_currency, weakest_currency "
            "FROM macrofx_weekly_runs ORDER BY week_ending DESC LIMIT 1"
        )
    return {
        "status": "ok",
        "latest_heartbeat": dict(latest) if latest else None,
        "latest_weekly_run": dict(latest_run) if latest_run else None,
    }

@router.post("/heartbeat")
async def heartbeat(
    account_id: str,
    balance: float = 0,
    equity: float = 0,
    free_margin: float = 0,
    is_demo: bool = True,
    ea_version: str = "",
    broker: str = "MidasFX",
    x_ea_api_key: str = Header(default="", alias="X-EA-API-Key"),
):
    _verify(x_ea_api_key)
    if not is_demo:
        raise HTTPException(status_code=409, detail="MacroFX bridge is demo-only in v1")
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO macrofx_heartbeats(account_id,balance,equity,free_margin,is_demo,ea_version,broker) "
            "VALUES($1,$2,$3,$4,$5,$6,$7)",
            account_id, balance, equity, free_margin, is_demo, ea_version, broker
        )
    return {"status":"ok"}

@router.post("/positions-csv")
async def positions_csv(account_id: str, body: str = Body(default="", media_type="text/plain"), x_ea_api_key: str = Header(default="", alias="X-EA-API-Key")):
    _verify(x_ea_api_key)
    pool = await get_pool()
    rows = []
    for line in body.splitlines():
        line = line.strip()
        if not line or line.lower().startswith("symbol,"):
            continue
        p = [x.strip() for x in line.split(",")]
        if len(p) >= 10:
            rows.append(p[:10])
    async with pool.acquire() as conn:
        for p in rows:
            await conn.execute(
                "INSERT INTO macrofx_positions(account_id,symbol,ticket,side,lots,open_price,current_price,pnl,swap,commission,magic) "
                "VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)",
                account_id, p[0], int(_num(p[1],0)), p[2], _num(p[3]), _num(p[4]), _num(p[5]),
                _num(p[6]), _num(p[7]), _num(p[8]), int(_num(p[9],0))
            )
    return {"status":"ok","rows":len(rows)}

@router.post("/bars-csv")
async def bars_csv(symbol: str, body: str = Body(default="", media_type="text/plain"), x_ea_api_key: str = Header(default="", alias="X-EA-API-Key")):
    _verify(x_ea_api_key)
    symbol = symbol.upper()
    pool = await get_pool()
    inserted = 0
    async with pool.acquire() as conn:
        for line in body.splitlines():
            line = line.strip()
            if not line or line.lower().startswith("date,"):
                continue
            p = [x.strip() for x in line.split(",")]
            if len(p) < 2:
                continue
            try:
                d = datetime.strptime(p[0], "%Y-%m-%d").date()
                close = float(p[1])
            except Exception:
                continue
            if close <= 0:
                continue
            await conn.execute(
                "INSERT INTO macrofx_daily_bars(symbol,bar_date,close) VALUES($1,$2,$3) "
                "ON CONFLICT(symbol,bar_date) DO UPDATE SET close=EXCLUDED.close, updated_at=NOW()",
                symbol, d, close
            )
            inserted += 1
    return {"status":"ok","symbol":symbol,"bars":inserted}

@router.post("/fill")
async def fill(
    account_id: str,
    symbol: str,
    action: str,
    lots: float,
    ticket: int = 0,
    requested_price: float = 0,
    fill_price: float = 0,
    spread_points: float = 0,
    slippage_points: float = 0,
    pnl: float = 0,
    swap: float = 0,
    commission: float = 0,
    strategy_version: str = "macrofx-v1",
    notes: str = "",
    x_ea_api_key: str = Header(default="", alias="X-EA-API-Key"),
):
    _verify(x_ea_api_key)
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO macrofx_fills(account_id,symbol,ticket,action,lots,requested_price,fill_price,"
            "spread_points,slippage_points,pnl,swap,commission,strategy_version,notes) "
            "VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14)",
            account_id, symbol, ticket, action, lots, requested_price, fill_price,
            spread_points, slippage_points, pnl, swap, commission, strategy_version, notes
        )
    return {"status":"ok"}

async def run_weekly_analysis(force: bool = False):
    pool = await get_pool()
    today_et = datetime.now(ZoneInfo("America/New_York")).date()
    week_ending = today_et - timedelta(days=(today_et.weekday() - 4) % 7)

    async with pool.acquire() as conn:
        if not force:
            existing = await conn.fetchrow(
                "SELECT id FROM macrofx_weekly_runs WHERE week_ending=$1", week_ending
            )
            if existing:
                return {"status":"already_ran","week_ending":str(week_ending),"run_id":existing["id"]}
        rows = await conn.fetch(
            "SELECT symbol, bar_date, close FROM macrofx_daily_bars "
            "WHERE bar_date >= $1 ORDER BY bar_date, symbol",
            week_ending - timedelta(days=520)
        )

    if not rows:
        raise HTTPException(status_code=409, detail="No MacroFX daily bars have been uploaded")

    df = pd.DataFrame([dict(r) for r in rows])
    close_df = df.pivot_table(index="bar_date", columns="symbol", values="close", aggfunc="last").sort_index()
    close_df.index = pd.to_datetime(close_df.index)
    available = [c for c in close_df.columns if close_df[c].notna().sum() >= 260]
    close_df = close_df[available]

    if len(available) < 6:
        raise HTTPException(
            status_code=409,
            detail=f"Need more history: only {len(available)} pairs have at least 260 daily bars"
        )

    snapshot = build_snapshot(close_df)
    targets = choose_targets(snapshot, available, min_lot=0.01)
    strongest = str(snapshot.iloc[0]["currency"]) if not snapshot.empty else None
    weakest = str(snapshot.iloc[-1]["currency"]) if not snapshot.empty else None
    snapshot_records = json.loads(snapshot.to_json(orient="records"))
    target_records = [t.__dict__ for t in targets]

    lines = [
        f"# Macro FX Weekly — {week_ending}",
        "",
        f"Strongest currency: {strongest or 'N/A'}",
        f"Weakest currency: {weakest or 'N/A'}",
        f"Target positions: {len(target_records)}",
        "",
        "## Currency ranking",
        "",
        "| Currency | Score | Agreement | 1M | 3M | 6M | 12M |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, r in snapshot.iterrows():
        lines.append(
            f"| {r['currency']} | {r['score']:+.3f} | {int(r['agreement'])}/4 | "
            f"{r.get('m21',float('nan')):+.3f} | {r.get('m63',float('nan')):+.3f} | "
            f"{r.get('m126',float('nan')):+.3f} | {r.get('m252',float('nan')):+.3f} |"
        )

    lines += ["", "## Demo targets", ""]
    if target_records:
        for t in target_records:
            lines.append(f"- {t['direction']} {t['symbol']} {t['lots']:.2f} lots — {t['reason']}")
    else:
        lines.append("- No pair passed the current macro-divergence gate.")

    async with pool.acquire() as conn:
        eqrows = await conn.fetch(
            "SELECT captured_at, equity FROM macrofx_heartbeats WHERE equity > 0 ORDER BY captured_at"
        )

    perf = performance_metrics(pd.DataFrame([dict(r) for r in eqrows])) if eqrows else {}
    lines += ["", "## Broker-demo feedback", ""]
    if perf:
        lines.append(f"- Ending equity: USD {perf.get('ending_equity',0):,.2f}")
        if "total_return" in perf:
            lines.append(f"- Demo return: {perf['total_return']:.2%}")
        if "max_drawdown" in perf:
            lines.append(f"- Max drawdown: {perf['max_drawdown']:.2%}")
        if "sharpe" in perf and pd.notna(perf["sharpe"]):
            lines.append(f"- Snapshot Sharpe: {perf['sharpe']:.2f}")
    else:
        lines.append("- Not enough demo-equity history yet.")

    lines += [
        "",
        "## Feedback rules",
        "",
        "- Compare model targets with actual MT4 positions and fills.",
        "- Track spread, slippage, swap and commission drag separately.",
        "- Do not alter momentum horizons because of one weak week.",
        "- Any strategy change gets a new version and must be retested out-of-sample.",
    ]
    report = "\n".join(lines)
    expires = datetime.now(timezone.utc) + timedelta(days=10)

    async with pool.acquire() as conn:
        async with conn.transaction():
            if force:
                old = await conn.fetchrow(
                    "SELECT id FROM macrofx_weekly_runs WHERE week_ending=$1", week_ending
                )
                if old:
                    await conn.execute("DELETE FROM macrofx_weekly_runs WHERE id=$1", old["id"])

            run_id = await conn.fetchval(
                "INSERT INTO macrofx_weekly_runs("
                "week_ending,strategy_version,strongest_currency,weakest_currency,"
                "snapshot_json,targets_json,report_markdown) "
                "VALUES($1,'macrofx-v1',$2,$3,$4::jsonb,$5::jsonb,$6) RETURNING id",
                week_ending, strongest, weakest,
                json.dumps(snapshot_records), json.dumps(target_records), report
            )
            await conn.execute("UPDATE macrofx_targets SET active=FALSE WHERE active=TRUE")
            for t in target_records:
                await conn.execute(
                    "INSERT INTO macrofx_targets(weekly_run_id,expires_at,symbol,direction,lots,score,reason) "
                    "VALUES($1,$2,$3,$4,$5,$6,$7)",
                    run_id, expires, t["symbol"], t["direction"], t["lots"], t["score"], t["reason"]
                )

    return {
        "status":"ok",
        "week_ending":str(week_ending),
        "run_id":run_id,
        "strongest":strongest,
        "weakest":weakest,
        "targets":target_records,
        "report_markdown":report,
    }

@router.post("/run-weekly")
async def run_weekly(x_ea_api_key: str = Header(default="", alias="X-EA-API-Key"), force: bool = False):
    _verify(x_ea_api_key)
    return await run_weekly_analysis(force=force)

@router.get("/targets-text", response_class=PlainTextResponse)
async def targets_text(x_ea_api_key: str = Header(default="", alias="X-EA-API-Key"), account_id: str = ""):
    _verify(x_ea_api_key)
    pool = await get_pool()
    async with pool.acquire() as conn:
        hb = (
            await conn.fetchrow(
                "SELECT is_demo FROM macrofx_heartbeats WHERE account_id=$1 ORDER BY captured_at DESC LIMIT 1",
                account_id
            )
            if account_id else None
        )
        if hb and not hb["is_demo"]:
            return PlainTextResponse("ERROR,LIVE_ACCOUNT_BLOCKED\n", status_code=409)
        rows = await conn.fetch(
            "SELECT symbol,direction,lots,score,expires_at FROM macrofx_targets "
            "WHERE active=TRUE AND expires_at > NOW() ORDER BY ABS(score) DESC"
        )

    lines = [
        "MODE,DEMO_ONLY",
        "STRATEGY,macrofx-v1",
        "FLATTEN_UNLISTED,1",
        "MAX_POSITIONS,2",
        "MAX_LOT_PER_PAIR,0.01",
    ]
    for r in rows:
        signed = r["lots"] if r["direction"] == "LONG" else -r["lots"]
        lines.append(f"TARGET,{r['symbol']},{signed:.2f},{r['score']:.6f}")
    return "\n".join(lines) + "\n"

@router.get("/weekly-report")
async def weekly_report():
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT week_ending,created_at,strongest_currency,weakest_currency,report_markdown "
            "FROM macrofx_weekly_runs ORDER BY week_ending DESC LIMIT 1"
        )
    if not row:
        raise HTTPException(status_code=404, detail="No weekly MacroFX report yet")
    return dict(row)

@router.get("/status")
async def status():
    pool = await get_pool()
    async with pool.acquire() as conn:
        hb = await conn.fetchrow("SELECT * FROM macrofx_heartbeats ORDER BY captured_at DESC LIMIT 1")
        targets = await conn.fetch(
            "SELECT symbol,direction,lots,score,reason FROM macrofx_targets "
            "WHERE active=TRUE AND expires_at>NOW() ORDER BY ABS(score) DESC"
        )
        fills = await conn.fetch("SELECT * FROM macrofx_fills ORDER BY captured_at DESC LIMIT 20")
    return {
        "heartbeat": dict(hb) if hb else None,
        "targets": [dict(r) for r in targets],
        "recent_fills": [dict(r) for r in fills],
    }

"""
EST Liquidity Breakout EA — Trade Journal API
Receives real-time trade events from the EA via WebRequest,
stores in PostgreSQL, serves dashboard, and tracks patterns for system improvement.
"""

import os
import json
from datetime import datetime, date, timedelta
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncpg

DATABASE_URL = os.environ.get("DATABASE_URL", "")
API_KEY = os.environ.get("EA_API_KEY", "estlb-secret-key-change-me")

# ======================== DATABASE ========================

pool: Optional[asyncpg.Pool] = None

async def init_db():
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL, min_size=2, max_size=10)
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS trade_events (
                id SERIAL PRIMARY KEY,
                timestamp_est TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                event_type VARCHAR(50) NOT NULL,
                symbol VARCHAR(20),
                direction VARCHAR(10),
                level_name VARCHAR(30),
                level_price DOUBLE PRECISION,
                entry_price DOUBLE PRECISION,
                stop_price DOUBLE PRECISION,
                target_1r DOUBLE PRECISION,
                target_2r DOUBLE PRECISION,
                risk_price DOUBLE PRECISION,
                rr_ratio DOUBLE PRECISION,
                candle_open DOUBLE PRECISION,
                candle_high DOUBLE PRECISION,
                candle_low DOUBLE PRECISION,
                candle_close DOUBLE PRECISION,
                close_pct DOUBLE PRECISION,
                daily_trend VARCHAR(30),
                bid_at_signal DOUBLE PRECISION,
                spread DOUBLE PRECISION,
                result VARCHAR(30),
                pnl_price DOUBLE PRECISION,
                pnl_points DOUBLE PRECISION,
                duration_minutes INTEGER,
                lots DOUBLE PRECISION,
                notes TEXT,
                ea_version VARCHAR(10)
            );

            CREATE TABLE IF NOT EXISTS daily_summaries (
                id SERIAL PRIMARY KEY,
                trade_date DATE NOT NULL UNIQUE,
                symbol VARCHAR(20),
                daily_trend VARCHAR(30),
                pdh DOUBLE PRECISION,
                pdl DOUBLE PRECISION,
                pm_high DOUBLE PRECISION,
                pm_low DOUBLE PRECISION,
                or_high DOUBLE PRECISION,
                or_low DOUBLE PRECISION,
                setups_found INTEGER DEFAULT 0,
                setups_rejected INTEGER DEFAULT 0,
                trades_taken INTEGER DEFAULT 0,
                trades_won INTEGER DEFAULT 0,
                trades_lost INTEGER DEFAULT 0,
                total_pnl DOUBLE PRECISION DEFAULT 0,
                max_win DOUBLE PRECISION DEFAULT 0,
                max_loss DOUBLE PRECISION DEFAULT 0,
                rejection_reasons TEXT,
                user_notes TEXT,
                lessons_learned TEXT,
                ea_version VARCHAR(10)
            );

            CREATE TABLE IF NOT EXISTS system_changelog (
                id SERIAL PRIMARY KEY,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                version VARCHAR(10) NOT NULL,
                change_type VARCHAR(20) NOT NULL,
                description TEXT NOT NULL,
                reason TEXT,
                metrics_before TEXT,
                metrics_after TEXT
            );

            CREATE TABLE IF NOT EXISTS pattern_observations (
                id SERIAL PRIMARY KEY,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                trade_date DATE,
                pattern_type VARCHAR(50) NOT NULL,
                description TEXT NOT NULL,
                frequency INTEGER DEFAULT 1,
                outcome VARCHAR(20),
                confidence DOUBLE PRECISION,
                actionable BOOLEAN DEFAULT FALSE,
                action_taken TEXT
            );

            CREATE TABLE IF NOT EXISTS daily_plans (
                id SERIAL PRIMARY KEY,
                trade_date DATE NOT NULL UNIQUE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                bias VARCHAR(20) DEFAULT 'Neutral',
                bias_reason TEXT DEFAULT '',
                yesterday_summary TEXT DEFAULT '',
                premarket_notes TEXT DEFAULT '',
                key_levels TEXT DEFAULT '',
                long_setups TEXT DEFAULT '',
                short_setups TEXT DEFAULT '',
                invalidation TEXT DEFAULT '',
                stop_plan TEXT DEFAULT '',
                notes TEXT DEFAULT ''
            );

            CREATE INDEX IF NOT EXISTS idx_events_date ON trade_events(timestamp_est);
            CREATE INDEX IF NOT EXISTS idx_events_type ON trade_events(event_type);
            CREATE INDEX IF NOT EXISTS idx_summaries_date ON daily_summaries(trade_date);
        """)

async def close_db():
    global pool
    if pool:
        await pool.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()

app = FastAPI(
    title="EST Liquidity Breakout EA — Trade Journal",
    version="1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================== MODELS ========================

class TradeEvent(BaseModel):
    event_type: str
    symbol: str = ""
    direction: str = ""
    level_name: str = ""
    level_price: float = 0
    entry_price: float = 0
    stop_price: float = 0
    target_1r: float = 0
    target_2r: float = 0
    risk_price: float = 0
    rr_ratio: float = 0
    candle_open: float = 0
    candle_high: float = 0
    candle_low: float = 0
    candle_close: float = 0
    close_pct: float = 0
    daily_trend: str = ""
    bid_at_signal: float = 0
    spread: float = 0
    result: str = ""
    pnl_price: float = 0
    pnl_points: float = 0
    duration_minutes: int = 0
    lots: float = 0
    notes: str = ""
    ea_version: str = ""
    api_key: str = ""

class DailyNote(BaseModel):
    trade_date: str
    user_notes: str = ""
    lessons_learned: str = ""
    api_key: str = ""

class ChangelogEntry(BaseModel):
    version: str
    change_type: str
    description: str
    reason: str = ""
    api_key: str = ""

class DailyPlan(BaseModel):
    trade_date: str = ""
    bias: str = "Neutral"
    bias_reason: str = ""
    yesterday_summary: str = ""
    premarket_notes: str = ""
    key_levels: str = ""
    long_setups: str = ""
    short_setups: str = ""
    invalidation: str = ""
    stop_plan: str = ""
    notes: str = ""
    api_key: str = ""

# ======================== AUTH ========================

def verify_key(key: str):
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

# ======================== PLAN ENDPOINTS ========================

@app.post("/api/plan")
async def save_plan(plan: DailyPlan):
    verify_key(plan.api_key)
    trade_date = datetime.strptime(plan.trade_date, "%Y-%m-%d").date() if plan.trade_date else date.today()

    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO daily_plans (trade_date, bias, bias_reason, yesterday_summary, premarket_notes,
                key_levels, long_setups, short_setups, invalidation, stop_plan, notes, updated_at)
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,NOW())
            ON CONFLICT (trade_date) DO UPDATE SET
                bias=$2, bias_reason=$3, yesterday_summary=$4, premarket_notes=$5,
                key_levels=$6, long_setups=$7, short_setups=$8, invalidation=$9,
                stop_plan=$10, notes=$11, updated_at=NOW()
        """, trade_date, plan.bias, plan.bias_reason, plan.yesterday_summary,
            plan.premarket_notes, plan.key_levels, plan.long_setups,
            plan.short_setups, plan.invalidation, plan.stop_plan, plan.notes)

    return {"status": "ok", "date": str(trade_date)}

@app.get("/api/plan/{plan_date}")
async def get_plan(plan_date: str):
    trade_date = datetime.strptime(plan_date, "%Y-%m-%d").date()
    async with pool.acquire() as conn:
        plan = await conn.fetchrow("SELECT * FROM daily_plans WHERE trade_date = $1", trade_date)
    if not plan:
        raise HTTPException(status_code=404, detail="No plan for " + plan_date)
    return dict(plan)

# ======================== EVENT ENDPOINTS ========================

@app.post("/api/event")
async def log_event(event: TradeEvent):
    verify_key(event.api_key)

    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO trade_events (
                event_type, symbol, direction, level_name, level_price,
                entry_price, stop_price, target_1r, target_2r,
                risk_price, rr_ratio, candle_open, candle_high, candle_low, candle_close,
                close_pct, daily_trend, bid_at_signal, spread,
                result, pnl_price, pnl_points, duration_minutes, lots, notes, ea_version
            ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17,$18,$19,$20,$21,$22,$23,$24,$25,$26)
        """,
            event.event_type, event.symbol, event.direction, event.level_name, event.level_price,
            event.entry_price, event.stop_price, event.target_1r, event.target_2r,
            event.risk_price, event.rr_ratio, event.candle_open, event.candle_high,
            event.candle_low, event.candle_close, event.close_pct, event.daily_trend,
            event.bid_at_signal, event.spread, event.result, event.pnl_price,
            event.pnl_points, event.duration_minutes, event.lots, event.notes, event.ea_version
        )

        # Auto-update daily summary on trade close events
        if event.event_type == "TRADE_CLOSED":
            today = date.today()
            is_win = event.pnl_price > 0

            await conn.execute("""
                INSERT INTO daily_summaries (trade_date, symbol, trades_taken, trades_won, trades_lost, total_pnl, max_win, max_loss, ea_version)
                VALUES ($1, $2, 1, $3, $4, $5, $6, $7, $8)
                ON CONFLICT (trade_date) DO UPDATE SET
                    trades_taken = daily_summaries.trades_taken + 1,
                    trades_won = daily_summaries.trades_won + $3,
                    trades_lost = daily_summaries.trades_lost + $4,
                    total_pnl = daily_summaries.total_pnl + $5,
                    max_win = GREATEST(daily_summaries.max_win, $6),
                    max_loss = LEAST(daily_summaries.max_loss, $7)
            """,
                today, event.symbol,
                1 if is_win else 0,
                0 if is_win else 1,
                event.pnl_price,
                event.pnl_price if is_win else 0,
                event.pnl_price if not is_win else 0,
                event.ea_version
            )

        # Auto-update daily summary on daily open
        if event.event_type == "DAILY_OPEN":
            today = date.today()
            await conn.execute("""
                INSERT INTO daily_summaries (trade_date, symbol, daily_trend, ea_version)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (trade_date) DO UPDATE SET
                    daily_trend = $3,
                    ea_version = $4
            """, today, event.symbol, event.daily_trend, event.ea_version)

    return {"status": "ok", "event": event.event_type}


@app.post("/api/daily-note")
async def add_daily_note(note: DailyNote):
    verify_key(note.api_key)
    trade_date = datetime.strptime(note.trade_date, "%Y-%m-%d").date()

    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO daily_summaries (trade_date, user_notes, lessons_learned)
            VALUES ($1, $2, $3)
            ON CONFLICT (trade_date) DO UPDATE SET
                user_notes = $2,
                lessons_learned = $3
        """, trade_date, note.user_notes, note.lessons_learned)

    return {"status": "ok"}


@app.post("/api/changelog")
async def add_changelog(entry: ChangelogEntry):
    verify_key(entry.api_key)

    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO system_changelog (version, change_type, description, reason)
            VALUES ($1, $2, $3, $4)
        """, entry.version, entry.change_type, entry.description, entry.reason)

    return {"status": "ok"}


# ======================== QUERY ENDPOINTS ========================

@app.get("/api/today")
async def get_today():
    today = date.today()
    async with pool.acquire() as conn:
        events = await conn.fetch(
            "SELECT * FROM trade_events WHERE timestamp_est::date = $1 ORDER BY timestamp_est",
            today
        )
        summary = await conn.fetchrow(
            "SELECT * FROM daily_summaries WHERE trade_date = $1", today
        )

    return {
        "date": str(today),
        "events": [dict(r) for r in events],
        "summary": dict(summary) if summary else None
    }


@app.get("/api/stats")
async def get_stats(days: int = Query(default=30)):
    since = date.today() - timedelta(days=days)
    async with pool.acquire() as conn:
        stats = await conn.fetchrow("""
            SELECT
                COUNT(*) as total_trades,
                SUM(CASE WHEN pnl_price > 0 THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN pnl_price <= 0 THEN 1 ELSE 0 END) as losses,
                COALESCE(SUM(pnl_price), 0) as total_pnl,
                COALESCE(AVG(pnl_price), 0) as avg_pnl,
                COALESCE(MAX(pnl_price), 0) as best_trade,
                COALESCE(MIN(pnl_price), 0) as worst_trade,
                COALESCE(AVG(duration_minutes), 0) as avg_duration,
                COALESCE(AVG(risk_price), 0) as avg_risk
            FROM trade_events
            WHERE event_type = 'TRADE_CLOSED'
            AND timestamp_est::date >= $1
        """, since)

        # Pattern: win rate by level
        by_level = await conn.fetch("""
            SELECT
                e_open.level_name,
                COUNT(*) as trades,
                SUM(CASE WHEN e_close.pnl_price > 0 THEN 1 ELSE 0 END) as wins,
                COALESCE(AVG(e_close.pnl_price), 0) as avg_pnl
            FROM trade_events e_close
            JOIN trade_events e_open ON e_open.event_type = 'TRADE_OPENED'
                AND e_open.timestamp_est::date = e_close.timestamp_est::date
                AND e_open.symbol = e_close.symbol
            WHERE e_close.event_type = 'TRADE_CLOSED'
            AND e_close.timestamp_est::date >= $1
            AND e_open.level_name != ''
            GROUP BY e_open.level_name
            ORDER BY trades DESC
        """, since)

        # Pattern: win rate by direction
        by_direction = await conn.fetch("""
            SELECT
                e_open.direction,
                COUNT(*) as trades,
                SUM(CASE WHEN e_close.pnl_price > 0 THEN 1 ELSE 0 END) as wins,
                COALESCE(AVG(e_close.pnl_price), 0) as avg_pnl
            FROM trade_events e_close
            JOIN trade_events e_open ON e_open.event_type = 'TRADE_OPENED'
                AND e_open.timestamp_est::date = e_close.timestamp_est::date
                AND e_open.symbol = e_close.symbol
            WHERE e_close.event_type = 'TRADE_CLOSED'
            AND e_close.timestamp_est::date >= $1
            AND e_open.direction != ''
            GROUP BY e_open.direction
        """, since)

        # Pattern: win rate by trend alignment
        by_trend = await conn.fetch("""
            SELECT
                e_open.daily_trend,
                e_open.direction,
                COUNT(*) as trades,
                SUM(CASE WHEN e_close.pnl_price > 0 THEN 1 ELSE 0 END) as wins,
                COALESCE(AVG(e_close.pnl_price), 0) as avg_pnl
            FROM trade_events e_close
            JOIN trade_events e_open ON e_open.event_type = 'TRADE_OPENED'
                AND e_open.timestamp_est::date = e_close.timestamp_est::date
                AND e_open.symbol = e_close.symbol
            WHERE e_close.event_type = 'TRADE_CLOSED'
            AND e_close.timestamp_est::date >= $1
            AND e_open.daily_trend != ''
            GROUP BY e_open.daily_trend, e_open.direction
        """, since)

        # Recent daily P&L
        daily_pnl = await conn.fetch("""
            SELECT trade_date, total_pnl, trades_taken, trades_won, trades_lost
            FROM daily_summaries
            WHERE trade_date >= $1
            ORDER BY trade_date
        """, since)

    total = dict(stats) if stats else {}
    win_rate = 0
    if total.get("total_trades", 0) > 0:
        win_rate = round(total["wins"] / total["total_trades"] * 100, 1)

    return {
        "period_days": days,
        "total": {**total, "win_rate": win_rate},
        "by_level": [dict(r) for r in by_level],
        "by_direction": [dict(r) for r in by_direction],
        "by_trend_alignment": [dict(r) for r in by_trend],
        "daily_pnl": [dict(r) for r in daily_pnl]
    }


@app.get("/api/patterns")
async def get_patterns():
    async with pool.acquire() as conn:
        patterns = await conn.fetch(
            "SELECT * FROM pattern_observations ORDER BY created_at DESC LIMIT 50"
        )
    return [dict(r) for r in patterns]


@app.get("/api/changelog")
async def get_changelog_entries():
    async with pool.acquire() as conn:
        entries = await conn.fetch(
            "SELECT * FROM system_changelog ORDER BY created_at DESC LIMIT 50"
        )
    return [dict(r) for r in entries]


@app.get("/api/daily-log/{log_date}")
async def get_daily_log(log_date: str):
    """Generate a detailed daily log for a specific date"""
    trade_date = datetime.strptime(log_date, "%Y-%m-%d").date()

    async with pool.acquire() as conn:
        summary = await conn.fetchrow(
            "SELECT * FROM daily_summaries WHERE trade_date = $1", trade_date
        )
        # Query events by both the target date AND the next day (UTC offset issue)
        # Events at 9:45 EST on Apr 7 = 13:45 UTC on Apr 7, but events at 20:00 EST = 00:00 UTC next day
        events = await conn.fetch("""
            SELECT * FROM trade_events
            WHERE timestamp_est::date = $1
               OR timestamp_est::date = $2
            ORDER BY timestamp_est
        """, trade_date, trade_date - timedelta(days=1))
        changelog = await conn.fetch("""
            SELECT * FROM system_changelog
            WHERE created_at::date = $1 OR created_at::date = $2
            ORDER BY created_at
        """, trade_date, trade_date - timedelta(days=1))

    s = dict(summary) if summary else {}
    evts = [dict(e) for e in events]
    changes = [dict(c) for c in changelog]

    if not evts and not s:
        raise HTTPException(status_code=404, detail=f"No data found for {log_date}")

    # Build the daily log
    setups = [e for e in evts if e["event_type"] == "SETUP_FOUND"]
    rejections = [e for e in evts if e["event_type"] == "SETUP_REJECTED"]
    opens = [e for e in evts if e["event_type"] == "TRADE_OPENED"]
    closes = [e for e in evts if e["event_type"] == "TRADE_CLOSED"]
    partials = [e for e in evts if e["event_type"] in ("PARTIAL_CLOSE", "PARTIAL_SKIPPED")]
    breakevens = [e for e in evts if e["event_type"] == "BREAKEVEN"]

    total_pnl = sum(c.get("pnl_price", 0) or 0 for c in closes)
    wins = [c for c in closes if (c.get("pnl_price", 0) or 0) > 0]
    losses = [c for c in closes if (c.get("pnl_price", 0) or 0) <= 0]

    return {
        "date": str(trade_date),
        "summary": {
            "trend": s.get("daily_trend", "Unknown"),
            "ea_version": s.get("ea_version", "Unknown"),
            "setups_found": len(setups),
            "setups_rejected": len(rejections),
            "trades_opened": len(opens),
            "trades_closed": len(closes),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": round(len(wins) / len(closes) * 100, 1) if closes else 0,
            "total_pnl": round(total_pnl, 2),
            "best_trade": round(max((c.get("pnl_price", 0) or 0 for c in closes), default=0), 2),
            "worst_trade": round(min((c.get("pnl_price", 0) or 0 for c in closes), default=0), 2),
            "user_notes": s.get("user_notes", ""),
            "lessons_learned": s.get("lessons_learned", ""),
        },
        "levels": {
            "pdh": s.get("pdh"),
            "pdl": s.get("pdl"),
            "pm_high": s.get("pm_high"),
            "pm_low": s.get("pm_low"),
            "or_high": s.get("or_high"),
            "or_low": s.get("or_low"),
        },
        "timeline": evts,
        "setups": setups,
        "rejections": rejections,
        "trades": [{
            "opened": o,
            "closed": next((c for c in closes if c["timestamp_est"] > o["timestamp_est"]), None),
            "partial": next((p for p in partials if p["timestamp_est"] > o["timestamp_est"]), None),
            "breakeven": next((b for b in breakevens if b["timestamp_est"] > o["timestamp_est"]), None),
        } for o in opens],
        "system_changes": changes,
    }


@app.get("/api/daily-log-markdown/{log_date}")
async def get_daily_log_markdown(log_date: str):
    """Generate markdown daily log for GitHub"""
    data = await get_daily_log(log_date)
    s = data["summary"]
    levels = data["levels"]

    md = f"""# Daily trading log — {data['date']}

## Session overview

| Metric | Value |
|--------|-------|
| EA version | {s['ea_version']} |
| Daily trend | {s['trend']} |
| Setups found | {s['setups_found']} |
| Setups rejected | {s['setups_rejected']} |
| Trades taken | {s['trades_opened']} |
| Wins / Losses | {s['wins']} / {s['losses']} |
| Win rate | {s['win_rate']}% |
| Total P&L | ${s['total_pnl']:.2f} |
| Best trade | ${s['best_trade']:.2f} |
| Worst trade | ${s['worst_trade']:.2f} |

## Levels

| Level | Price |
|-------|-------|
| PDH | {levels.get('pdh', 'N/A')} |
| PDL | {levels.get('pdl', 'N/A')} |
| PM High | {levels.get('pm_high', 'N/A')} |
| PM Low | {levels.get('pm_low', 'N/A')} |
| OR High | {levels.get('or_high', 'N/A')} |
| OR Low | {levels.get('or_low', 'N/A')} |

## Event timeline

| Time | Event | Direction | Level | P&L | Result | Notes |
|------|-------|-----------|-------|-----|--------|-------|
"""
    for e in data["timeline"]:
        ts = e["timestamp_est"].strftime("%H:%M") if e.get("timestamp_est") else ""
        pnl = f"${e['pnl_price']:.2f}" if e.get("pnl_price") else ""
        md += f"| {ts} | {e['event_type']} | {e.get('direction','')} | {e.get('level_name','')} | {pnl} | {e.get('result','')} | {e.get('notes','')} |\n"

    md += f"""
## Trade details

"""
    for i, t in enumerate(data["trades"], 1):
        o = t["opened"]
        c = t.get("closed", {}) or {}
        md += f"""### Trade {i}: {o.get('direction','')} on {o.get('level_name','')}
- Entry: {o.get('entry_price','')} | Stop: {o.get('stop_price','')}
- 1R target: {o.get('target_1r','')} | 2R target: {o.get('target_2r','')}
- Risk: ${o.get('risk_price', 0):.2f} | R:R: {o.get('rr_ratio', 0):.1f}
- Candle: O={o.get('candle_open','')} H={o.get('candle_high','')} L={o.get('candle_low','')} C={o.get('candle_close','')} (Close%={o.get('close_pct',0):.1f})
- Result: {c.get('result','')} | P&L: ${c.get('pnl_price',0):.2f} | Duration: {c.get('duration_minutes',0)} min
"""

    if data["rejections"]:
        md += "\n## Rejected setups\n\n"
        for r in data["rejections"]:
            md += f"- {r.get('direction','')} on {r.get('level_name','')}: {r.get('notes','')}\n"

    if data["system_changes"]:
        md += "\n## System changes today\n\n"
        for c in data["system_changes"]:
            md += f"- **v{c.get('version','')}** [{c.get('change_type','')}]: {c.get('description','')}\n"
            if c.get("reason"):
                md += f"  - Reason: {c['reason']}\n"

    md += f"""
## Casey's notes

{s.get('user_notes', '_No notes yet. Add via POST /api/daily-note_')}

## Lessons learned

{s.get('lessons_learned', '_No lessons yet. Add via POST /api/daily-note_')}

## Patterns to watch

_Review with Claude: upload this log or the CSV journal for analysis_

---
*Auto-generated by EST Liquidity Breakout EA Trade Journal API*
"""

    return {"date": data["date"], "markdown": md}


@app.get("/api/cumulative-log")
async def get_cumulative_log():
    """Generate a full cumulative performance report"""
    async with pool.acquire() as conn:
        days = await conn.fetch("""
            SELECT * FROM daily_summaries ORDER BY trade_date
        """)
        all_closes = await conn.fetch("""
            SELECT * FROM trade_events
            WHERE event_type = 'TRADE_CLOSED'
            ORDER BY timestamp_est
        """)
        changelog = await conn.fetch("""
            SELECT * FROM system_changelog ORDER BY created_at
        """)
        patterns = await conn.fetch("""
            SELECT * FROM pattern_observations ORDER BY created_at
        """)

        # Win rate by level
        by_level = await conn.fetch("""
            SELECT
                e_open.level_name,
                COUNT(*) as trades,
                SUM(CASE WHEN e_close.pnl_price > 0 THEN 1 ELSE 0 END) as wins,
                COALESCE(AVG(e_close.pnl_price), 0) as avg_pnl,
                COALESCE(SUM(e_close.pnl_price), 0) as total_pnl
            FROM trade_events e_close
            JOIN trade_events e_open ON e_open.event_type = 'TRADE_OPENED'
                AND e_open.timestamp_est::date = e_close.timestamp_est::date
            WHERE e_close.event_type = 'TRADE_CLOSED'
            AND e_open.level_name != ''
            GROUP BY e_open.level_name ORDER BY trades DESC
        """)

        # Win rate by direction + trend
        by_trend = await conn.fetch("""
            SELECT
                e_open.direction,
                e_open.daily_trend,
                COUNT(*) as trades,
                SUM(CASE WHEN e_close.pnl_price > 0 THEN 1 ELSE 0 END) as wins,
                COALESCE(AVG(e_close.pnl_price), 0) as avg_pnl
            FROM trade_events e_close
            JOIN trade_events e_open ON e_open.event_type = 'TRADE_OPENED'
                AND e_open.timestamp_est::date = e_close.timestamp_est::date
            WHERE e_close.event_type = 'TRADE_CLOSED'
            AND e_open.direction != ''
            GROUP BY e_open.direction, e_open.daily_trend
        """)

        # Win rate by close percentage bucket
        by_close_strength = await conn.fetch("""
            SELECT
                CASE
                    WHEN e_open.close_pct >= 90 THEN '90-100% (very strong)'
                    WHEN e_open.close_pct >= 80 THEN '80-90% (strong)'
                    WHEN e_open.close_pct >= 70 THEN '70-80% (moderate)'
                    ELSE 'Below 70% (weak)'
                END as strength,
                COUNT(*) as trades,
                SUM(CASE WHEN e_close.pnl_price > 0 THEN 1 ELSE 0 END) as wins,
                COALESCE(AVG(e_close.pnl_price), 0) as avg_pnl
            FROM trade_events e_close
            JOIN trade_events e_open ON e_open.event_type IN ('SETUP_FOUND')
                AND e_open.timestamp_est::date = e_close.timestamp_est::date
            WHERE e_close.event_type = 'TRADE_CLOSED'
            AND e_open.close_pct > 0
            GROUP BY strength ORDER BY strength DESC
        """)

        # Rejection analysis
        rejection_stats = await conn.fetch("""
            SELECT notes as reason, COUNT(*) as count
            FROM trade_events
            WHERE event_type = 'SETUP_REJECTED'
            GROUP BY notes ORDER BY count DESC
        """)

    closes = [dict(c) for c in all_closes]
    total_pnl = sum(c.get("pnl_price", 0) or 0 for c in closes)
    wins = len([c for c in closes if (c.get("pnl_price", 0) or 0) > 0])
    total = len(closes)

    # Calculate drawdown
    running_pnl = 0
    peak = 0
    max_dd = 0
    for c in closes:
        running_pnl += c.get("pnl_price", 0) or 0
        if running_pnl > peak:
            peak = running_pnl
        dd = peak - running_pnl
        if dd > max_dd:
            max_dd = dd

    return {
        "overall": {
            "total_days": len(days),
            "total_trades": total,
            "wins": wins,
            "losses": total - wins,
            "win_rate": round(wins / total * 100, 1) if total > 0 else 0,
            "total_pnl": round(total_pnl, 2),
            "avg_pnl": round(total_pnl / total, 2) if total > 0 else 0,
            "max_drawdown": round(max_dd, 2),
            "profit_factor": round(
                sum(c.get("pnl_price", 0) for c in closes if (c.get("pnl_price", 0) or 0) > 0) /
                abs(sum(c.get("pnl_price", 0) for c in closes if (c.get("pnl_price", 0) or 0) < 0) or 1),
                2
            ),
        },
        "by_level": [dict(r) for r in by_level],
        "by_trend_alignment": [dict(r) for r in by_trend],
        "by_close_strength": [dict(r) for r in by_close_strength],
        "rejection_analysis": [dict(r) for r in rejection_stats],
        "daily_history": [dict(d) for d in days],
        "changelog": [dict(c) for c in changelog],
        "patterns": [dict(p) for p in patterns],
    }


# ======================== DAILY PLAN PAGE ========================

@app.get("/plan", response_class=HTMLResponse)
@app.get("/plan/{plan_date}", response_class=HTMLResponse)
async def plan_page(plan_date: str = None):
    target_date = datetime.strptime(plan_date, "%Y-%m-%d").date() if plan_date else date.today()

    async with pool.acquire() as conn:
        plan = await conn.fetchrow("SELECT * FROM daily_plans WHERE trade_date = $1", target_date)
        # Get yesterday's summary for reference
        yesterday = target_date - timedelta(days=1)
        prev_summary = await conn.fetchrow("SELECT * FROM daily_summaries WHERE trade_date = $1", yesterday)
        prev_events = await conn.fetch("""
            SELECT * FROM trade_events WHERE timestamp_est::date = $1 OR timestamp_est::date = $2
            ORDER BY timestamp_est DESC LIMIT 5
        """, yesterday, yesterday - timedelta(days=1))
        # Available plan dates
        available = await conn.fetch("SELECT DISTINCT trade_date FROM daily_plans ORDER BY trade_date DESC LIMIT 14")

        # Get today's levels from DAILY_OPEN event (most recent one)
        daily_open = await conn.fetchrow("""
            SELECT notes FROM trade_events
            WHERE event_type = 'DAILY_OPEN'
            AND (timestamp_est::date = $1 OR timestamp_est::date = $2)
            ORDER BY timestamp_est DESC LIMIT 1
        """, target_date, target_date - timedelta(days=1))

    p = dict(plan) if plan else {}
    ps = dict(prev_summary) if prev_summary else {}
    avail = [str(r["trade_date"]) for r in available]

    # Parse levels from DAILY_OPEN notes
    auto_levels = ""
    if daily_open and daily_open.get("notes"):
        notes = daily_open["notes"]
        level_lines = []
        for part in notes.split(" "):
            if "=" in part:
                k, v = part.split("=", 1)
                if v != "N/A":
                    label = k
                    if k == "PDH": label = "PDH"
                    elif k == "PDL": label = "PDL"
                    elif k == "PMH": label = "PM High"
                    elif k == "PML": label = "PM Low"
                    elif k == "ORH": label = "OR High"
                    elif k == "ORL": label = "OR Low"
                    level_lines.append(f"{label}: {v}")
                else:
                    label = k
                    if k == "PMH": label = "PM High"
                    elif k == "PML": label = "PM Low"
                    elif k == "ORH": label = "OR High"
                    elif k == "ORL": label = "OR Low"
                    level_lines.append(f"{label}: (not yet available)")
        auto_levels = "\n".join(level_lines)

    # Use auto levels if plan doesn't already have levels saved
    key_levels_value = p.get('key_levels', '') or auto_levels

    # Nav
    nav_html = '<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:20px">'
    for d in avail:
        active = "background:#333;color:#fff" if d == str(target_date) else ""
        nav_html += f'<a href="/plan/{d}" style="padding:4px 12px;border-radius:4px;border:1px solid #333;color:#aaa;text-decoration:none;font-size:12px;{active}">{d}</a>'
    nav_html += '</div>'

    # Previous day info
    prev_html = ""
    if ps:
        prev_pnl = ps.get("total_pnl", 0) or 0
        prev_color = "#22c55e" if prev_pnl > 0 else "#ef4444" if prev_pnl < 0 else "#888"
        prev_html = f"""<div style="background:#111;border-radius:8px;padding:16px;margin-bottom:20px">
            <div style="font-size:13px;color:#888;margin-bottom:8px">Yesterday ({yesterday})</div>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:12px;font-size:13px">
                <div>Trend: {ps.get('daily_trend','?')}</div>
                <div>Trades: {ps.get('trades_taken',0)}</div>
                <div>Win: {ps.get('trades_won',0)} / Loss: {ps.get('trades_lost',0)}</div>
                <div style="color:{prev_color}">P&L: ${prev_pnl:.2f}</div>
            </div>
        </div>"""

    bias_val = p.get("bias", "Neutral")
    bias_options = ""
    for b in ["Bullish", "Bearish", "Neutral", "Range"]:
        sel = "selected" if b == bias_val else ""
        bias_options += f'<option value="{b}" {sel}>{b}</option>'

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Daily plan — {target_date}</title>
<style>
body{{font-family:-apple-system,system-ui,sans-serif;margin:0;padding:20px;background:#0a0a0a;color:#e0e0e0;max-width:900px;margin:0 auto}}
h1{{font-size:22px;font-weight:500;margin:0 0 4px}}
h2{{font-size:16px;font-weight:500;margin:24px 0 8px;color:#aaa;border-bottom:1px solid #222;padding-bottom:6px}}
.subtitle{{font-size:14px;color:#888;margin-bottom:16px}}
label{{display:block;font-size:13px;color:#888;margin-bottom:4px}}
input[type=text],textarea,select{{width:100%;padding:10px 12px;border:1px solid #333;border-radius:6px;background:#111;color:#e0e0e0;font-size:14px;font-family:inherit;box-sizing:border-box;margin-bottom:16px;resize:vertical}}
textarea{{min-height:80px}}
select{{height:42px}}
.row2{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
.nav-tabs{{display:flex;gap:0;margin-bottom:20px;border-bottom:1px solid #333}}
.nav-tabs a{{padding:10px 20px;color:#888;text-decoration:none;font-size:14px;border-bottom:2px solid transparent}}
.nav-tabs a:hover{{color:#fff;background:#111}}
.nav-tabs a.active{{color:#fff;border-bottom:2px solid #60a5fa}}
button{{padding:10px 24px;background:#1d4ed8;color:white;border:none;border-radius:6px;cursor:pointer;font-size:14px;font-weight:500}}
button:hover{{background:#2563eb}}
.saved{{color:#22c55e;font-size:13px;margin-left:12px;display:none}}
a{{color:#60a5fa}}
</style></head><body>

<div class="nav-tabs">
    <a href="/">Dashboard</a>
    <a href="/summary">Daily summary</a>
    <a href="/plan" class="active">Daily plan</a>
</div>

<h1>Daily trading plan</h1>
<div class="subtitle">{target_date} | Fill out before market open (9:30 EST)</div>

{nav_html}
{prev_html}

<h2>Market bias</h2>
<div class="row2">
    <div>
        <label>Bias for today</label>
        <select id="bias">{bias_options}</select>
    </div>
    <div>
        <label>Why? (e.g. "Above PDH, gap up, strong premarket")</label>
        <input type="text" id="bias_reason" value="{p.get('bias_reason','')}" placeholder="Price above PDH at 6628, bullish bias...">
    </div>
</div>

<h2>Yesterday's price action</h2>
<textarea id="yesterday_summary" placeholder="What happened yesterday? Key moves, levels that held/broke, end of day behavior...">{p.get('yesterday_summary','')}</textarea>

<h2>Premarket &amp; overnight</h2>
<textarea id="premarket_notes" placeholder="Gap up/down? Where is PM High/Low forming? Any news catalysts?">{p.get('premarket_notes','')}</textarea>

<h2>Key levels for today <span style="font-size:12px;color:#888;font-weight:400">(auto-loaded from EA)</span></h2>
<textarea id="key_levels" placeholder="Levels will auto-populate when EA sends DAILY_OPEN event..." style="min-height:120px">{key_levels_value}</textarea>
<button onclick="refreshLevels()" style="background:#333;padding:6px 16px;font-size:12px;margin-bottom:16px">Refresh levels from EA</button>

<h2>Setups I'm watching</h2>
<div class="row2">
    <div>
        <label>Long setups</label>
        <textarea id="long_setups" placeholder="e.g. PMH Breakout Long if price holds above ORL&#10;ORL Bounce Long if price pulls back to OR Low">{p.get('long_setups','')}</textarea>
    </div>
    <div>
        <label>Short setups</label>
        <textarea id="short_setups" placeholder="e.g. PML Breakdown Short if PM Low breaks&#10;PDL Breakdown Short if bearish — switch bias">{p.get('short_setups','')}</textarea>
    </div>
</div>

<h2>Plan invalidation</h2>
<textarea id="invalidation" placeholder="What would change the plan? e.g. 'If PDL breaks, switch from bullish to bearish. Look for PDL bounce short setups.'">{p.get('invalidation','')}</textarea>

<h2>Stop loss plan</h2>
<textarea id="stop_plan" placeholder="Where are stops going today? e.g. 'Longs: stop below PML (6757.6 - $3 = 6754.6). Shorts: stop above PMH (6777.7 + $3 = 6780.7)'">{p.get('stop_plan','')}</textarea>

<h2>Additional notes</h2>
<textarea id="notes" placeholder="Anything else — news events, personal reminders, risk management notes...">{p.get('notes','')}</textarea>

<div style="margin-top:20px;display:flex;align-items:center">
    <button onclick="savePlan()">Save plan</button>
    <span class="saved" id="saved-msg">Plan saved!</span>
</div>

<script>
async function savePlan() {{
    const body = {{
        trade_date: "{target_date}",
        bias: document.getElementById("bias").value,
        bias_reason: document.getElementById("bias_reason").value,
        yesterday_summary: document.getElementById("yesterday_summary").value,
        premarket_notes: document.getElementById("premarket_notes").value,
        key_levels: document.getElementById("key_levels").value,
        long_setups: document.getElementById("long_setups").value,
        short_setups: document.getElementById("short_setups").value,
        invalidation: document.getElementById("invalidation").value,
        stop_plan: document.getElementById("stop_plan").value,
        notes: document.getElementById("notes").value,
        api_key: prompt("Enter API key:")
    }};
    try {{
        const res = await fetch("/api/plan", {{
            method: "POST",
            headers: {{"Content-Type": "application/json"}},
            body: JSON.stringify(body)
        }});
        const data = await res.json();
        if(data.status === "ok") {{
            const msg = document.getElementById("saved-msg");
            msg.style.display = "inline";
            setTimeout(() => msg.style.display = "none", 3000);
        }} else {{
            alert("Error: " + JSON.stringify(data));
        }}
    }} catch(e) {{
        alert("Save failed: " + e.message);
    }}
}}

async function refreshLevels() {{
    try {{
        const res = await fetch("/api/today");
        const data = await res.json();
        if(!data.events) return;

        let levels = [];
        for(const evt of data.events) {{
            if(evt.event_type === "DAILY_OPEN" && evt.notes) {{
                const parts = evt.notes.split(" ");
                for(const part of parts) {{
                    if(part.includes("=")) {{
                        const [k, v] = part.split("=");
                        const labels = {{PDH:"PDH",PDL:"PDL",PMH:"PM High",PML:"PM Low",ORH:"OR High",ORL:"OR Low"}};
                        const label = labels[k] || k;
                        if(v === "N/A") levels.push(label + ": (not yet available)");
                        else levels.push(label + ": " + v);
                    }}
                }}
            }}
        }}

        if(levels.length > 0) {{
            const el = document.getElementById("key_levels");
            el.value = levels.join("\\n");
        }} else {{
            alert("No levels found yet. Make sure the EA is running and has sent a DAILY_OPEN event.");
        }}
    }} catch(e) {{
        alert("Failed to fetch levels: " + e.message);
    }}
}}
</script>

<div style="margin-top:40px;padding-top:20px;border-top:1px solid #222;font-size:12px;color:#555">
    <a href="/">Dashboard</a> | <a href="/summary">Today's summary</a> | <a href="/api/plan/{target_date}">Raw JSON</a>
</div>

</body></html>"""


# ======================== DAILY SUMMARY PAGE ========================

@app.get("/summary", response_class=HTMLResponse)
@app.get("/summary/{report_date}", response_class=HTMLResponse)
async def daily_summary_page(report_date: str = None):
    """Auto-generated daily trading summary with analysis, lessons, and evaluation"""
    if report_date:
        target_date = datetime.strptime(report_date, "%Y-%m-%d").date()
    else:
        target_date = date.today()

    async with pool.acquire() as conn:
        events = await conn.fetch(
            "SELECT * FROM trade_events WHERE timestamp_est::date = $1 ORDER BY timestamp_est",
            target_date
        )
        summary = await conn.fetchrow(
            "SELECT * FROM daily_summaries WHERE trade_date = $1", target_date
        )

        # Get previous days for comparison
        prev_days = await conn.fetch("""
            SELECT trade_date, total_pnl, trades_taken, trades_won, trades_lost
            FROM daily_summaries WHERE trade_date < $1
            ORDER BY trade_date DESC LIMIT 7
        """, target_date)

        # All-time stats
        all_time = await conn.fetchrow("""
            SELECT COUNT(*) as total_trades,
                SUM(CASE WHEN pnl_price > 0 THEN 1 ELSE 0 END) as wins,
                COALESCE(SUM(pnl_price), 0) as total_pnl
            FROM trade_events WHERE event_type = 'TRADE_CLOSED'
        """)

        # Available dates for navigation
        available = await conn.fetch(
            "SELECT DISTINCT timestamp_est::date as d FROM trade_events ORDER BY d DESC LIMIT 30"
        )

    evts = [dict(e) for e in events]
    s = dict(summary) if summary else {}
    at = dict(all_time) if all_time else {}
    avail_dates = [str(r["d"]) for r in available]

    # Categorize events
    setups = [e for e in evts if e["event_type"] == "SETUP_FOUND"]
    rejections = [e for e in evts if e["event_type"] == "SETUP_REJECTED"]
    opens = [e for e in evts if e["event_type"] == "TRADE_OPENED"]
    closes = [e for e in evts if e["event_type"] == "TRADE_CLOSED"]
    daily_open = next((e for e in evts if e["event_type"] == "DAILY_OPEN"), None)

    # Parse levels from DAILY_OPEN notes
    levels = {}
    if daily_open and daily_open.get("notes"):
        for part in daily_open["notes"].split(" "):
            if "=" in part:
                k, v = part.split("=", 1)
                levels[k] = v

    # Calculate stats
    total_pnl = sum(c.get("pnl_price", 0) or 0 for c in closes)
    wins = [c for c in closes if (c.get("pnl_price", 0) or 0) > 0]
    losses = [c for c in closes if (c.get("pnl_price", 0) or 0) <= 0]
    win_rate = round(len(wins) / len(closes) * 100) if closes else 0

    # Analyze setups
    directions = {}
    level_names = {}
    for setup in setups:
        d = setup.get("direction", "")
        ln = setup.get("level_name", "")
        directions[d] = directions.get(d, 0) + 1
        level_names[ln] = level_names.get(ln, 0) + 1

    # Rejection reasons
    rejection_reasons = {}
    for r in rejections:
        reason = r.get("notes", "Unknown")
        rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1

    # Price movement analysis
    first_bid = None
    last_bid = None
    low_bid = 999999
    high_bid = 0
    for e in evts:
        bid = e.get("bid_at_signal", 0) or 0
        if bid > 0:
            if first_bid is None:
                first_bid = bid
            last_bid = bid
            if bid < low_bid:
                low_bid = bid
            if bid > high_bid:
                high_bid = bid

    day_range = high_bid - low_bid if high_bid > 0 and low_bid < 999999 else 0
    day_move = (last_bid - first_bid) if first_bid and last_bid else 0

    # Generate analysis
    trend = s.get("daily_trend", daily_open.get("daily_trend", "Unknown") if daily_open else "Unknown")

    # Auto-generate lessons and evaluation
    analysis_points = []
    grade = "N/A"

    if len(closes) == 0 and len(setups) == 0:
        analysis_points.append("No setups found today. Market may not have reached key levels.")
        grade = "—"
    elif len(closes) == 0 and len(rejections) > 0:
        reasons = list(rejection_reasons.keys())
        analysis_points.append(f"EA found {len(setups)} setups but all were rejected: {', '.join(reasons)}")
        if "Order failed. Error=4756" in reasons:
            analysis_points.append("Error 4756 = Invalid volume. FixedLots needs to match broker minimum (likely 1.0).")
            analysis_points.append("This is a configuration issue, not a strategy issue. The setups were valid.")
        grade = "Config Error"
    elif len(closes) > 0:
        if win_rate >= 60:
            grade = "A"
        elif win_rate >= 40:
            grade = "B"
        elif total_pnl > 0:
            grade = "C+"
        else:
            grade = "C-" if win_rate > 20 else "D"
        analysis_points.append(f"Executed {len(closes)} trades with {win_rate}% win rate.")
        if total_pnl > 0:
            analysis_points.append(f"Net profitable day: +${total_pnl:.2f}")
        else:
            analysis_points.append(f"Net losing day: ${total_pnl:.2f}")

    # Check for counter-trend setups
    counter_trend = 0
    for setup in setups:
        if trend == "Bullish" and setup.get("direction") == "SHORT":
            counter_trend += 1
        elif trend == "Bearish" and setup.get("direction") == "LONG":
            counter_trend += 1
    if counter_trend > 0:
        analysis_points.append(f"{counter_trend} of {len(setups)} setups were counter-trend ({trend} trend but trading opposite direction).")

    # Check candle quality
    strong_candles = [s for s in setups if (s.get("close_pct", 50) or 50) <= 25 or (s.get("close_pct", 50) or 50) >= 75]
    if strong_candles:
        analysis_points.append(f"{len(strong_candles)} of {len(setups)} setup candles had strong closes (top/bottom 25%).")

    # Price movement context
    if day_range > 0:
        analysis_points.append(f"Price ranged {day_range:.1f} points today (high {high_bid:.1f} to low {low_bid:.1f}).")
        if abs(day_move) > day_range * 0.5:
            direction_word = "up" if day_move > 0 else "down"
            analysis_points.append(f"Trending day — price moved {abs(day_move):.1f} points {direction_word} ({abs(day_move)/day_range*100:.0f}% of range).")

    # Stop analysis for executed trades
    if opens:
        stops = []
        for o in opens:
            risk = o.get("risk_price", 0) or 0
            if risk > 0:
                stops.append(risk)
        if stops:
            avg_stop = sum(stops) / len(stops)
            analysis_points.append(f"Average stop distance: ${avg_stop:.2f}")

    # Build date navigation
    nav_html = '<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:20px">'
    for d in avail_dates[:14]:
        active = "background:#333;color:#fff" if d == str(target_date) else ""
        nav_html += f'<a href="/summary/{d}" style="padding:4px 12px;border-radius:4px;border:1px solid #333;color:#aaa;text-decoration:none;font-size:12px;{active}">{d}</a>'
    nav_html += '</div>'

    # Build events timeline
    timeline_html = ""
    for e in evts:
        ts = e["timestamp_est"]
        if ts:
            # Convert UTC to EST (subtract 4 hours for EDT)
            est_hour = ts.hour - 4
            if est_hour < 0:
                est_hour += 24
            time_str = f"{est_hour:02d}:{ts.minute:02d}"
        else:
            time_str = ""

        evt_type = e["event_type"]
        tag_class = "tag-b"
        if "REJECTED" in evt_type:
            tag_class = "tag-r"
        elif "FOUND" in evt_type:
            tag_class = "tag-y"
        elif "OPENED" in evt_type:
            tag_class = "tag-b"
        elif "CLOSED" in evt_type:
            tag_class = "tag-g" if (e.get("pnl_price", 0) or 0) > 0 else "tag-r"
        elif "SUMMARY" in evt_type:
            tag_class = "tag-p"

        pnl_str = f"${e['pnl_price']:.2f}" if e.get("pnl_price") else ""
        pnl_color = "#22c55e" if (e.get("pnl_price", 0) or 0) > 0 else "#ef4444" if (e.get("pnl_price", 0) or 0) < 0 else "#888"

        candle_str = ""
        if e.get("candle_open"):
            candle_str = f"O:{e['candle_open']:.1f} H:{e['candle_high']:.1f} L:{e['candle_low']:.1f} C:{e['candle_close']:.1f} ({e.get('close_pct',0):.0f}%)"

        timeline_html += f"""<tr>
            <td>{time_str}</td>
            <td><span class="tag {tag_class}">{evt_type}</span></td>
            <td>{e.get('direction','')}</td>
            <td>{e.get('level_name','')}</td>
            <td>{candle_str}</td>
            <td style="color:{pnl_color}">{pnl_str}</td>
            <td style="font-size:11px;color:#888">{e.get('notes','') or ''}</td>
        </tr>"""

    # Build trade details
    trades_html = ""
    for i, o in enumerate(opens, 1):
        c = next((c for c in closes if c["timestamp_est"] > o["timestamp_est"]), None)
        c = c or {}
        pnl = c.get("pnl_price", 0) or 0
        pnl_color = "#22c55e" if pnl > 0 else "#ef4444"
        trades_html += f"""<div style="background:#1a1a1a;border-radius:8px;padding:16px;margin-bottom:12px">
            <div style="display:flex;justify-content:space-between;align-items:center">
                <span style="font-weight:500">Trade {i}: {o.get('direction','')} on {o.get('level_name','')}</span>
                <span style="font-size:20px;font-weight:500;color:{pnl_color}">${pnl:.2f}</span>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-top:12px;font-size:13px;color:#aaa">
                <div>Entry: {o.get('entry_price','')}</div>
                <div>Stop: {o.get('stop_price','')}</div>
                <div>Risk: ${o.get('risk_price',0):.2f}</div>
                <div>1R: {o.get('target_1r','')}</div>
                <div>2R: {o.get('target_2r','')}</div>
                <div>R:R: {o.get('rr_ratio',0):.1f}</div>
            </div>
            <div style="margin-top:8px;font-size:12px;color:#666">Result: {c.get('result','')} | Duration: {c.get('duration_minutes',0)} min</div>
        </div>"""

    if not trades_html:
        trades_html = '<p style="color:#666">No trades executed today.</p>'

    # Analysis points HTML
    analysis_html = ""
    for point in analysis_points:
        analysis_html += f'<li style="margin-bottom:8px">{point}</li>'

    # Levels HTML
    levels_html = ""
    for k, v in levels.items():
        levels_html += f"<tr><td>{k}</td><td>{v}</td></tr>"

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Daily Summary — {target_date}</title>
<style>
body{{font-family:-apple-system,system-ui,sans-serif;margin:0;padding:20px;background:#0a0a0a;color:#e0e0e0;max-width:900px;margin:0 auto}}
h1{{font-size:22px;font-weight:500;margin:0 0 4px}}
h2{{font-size:16px;font-weight:500;margin:30px 0 12px;color:#aaa;border-bottom:1px solid #222;padding-bottom:6px}}
.subtitle{{font-size:14px;color:#888;margin-bottom:20px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:12px;margin-bottom:24px}}
.card{{background:#1a1a1a;border-radius:8px;padding:16px;text-align:center}}
.card .val{{font-size:22px;font-weight:500}}
.card .lbl{{font-size:11px;color:#888;margin-top:4px}}
.green{{color:#22c55e}}.red{{color:#ef4444}}.yellow{{color:#eab308}}.blue{{color:#60a5fa}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
th{{text-align:left;color:#666;font-weight:400;padding:8px;border-bottom:1px solid #222}}
td{{padding:8px;border-bottom:1px solid #1a1a1a}}
.tag{{display:inline-block;padding:2px 8px;border-radius:4px;font-size:11px}}
.tag-r{{background:#2d1515;color:#ef4444}}
.tag-y{{background:#2d2a15;color:#eab308}}
.tag-b{{background:#15202d;color:#60a5fa}}
.tag-g{{background:#152d15;color:#22c55e}}
.tag-p{{background:#1a1a2d;color:#a78bfa}}
ul{{padding-left:20px;color:#ccc;line-height:1.8}}
.grade{{font-size:48px;font-weight:500;text-align:center;padding:20px}}
a{{color:#60a5fa}}
.nav a:hover{{background:#333!important}}
.nav-tabs{{display:flex;gap:0;margin-bottom:20px;border-bottom:1px solid #333}}
.nav-tabs a{{padding:10px 20px;color:#888;text-decoration:none;font-size:14px;border-bottom:2px solid transparent}}
.nav-tabs a:hover{{color:#fff;background:#111}}
.nav-tabs a.active{{color:#fff;border-bottom:2px solid #60a5fa}}
</style></head><body>

<div class="nav-tabs">
    <a href="/">Dashboard</a>
    <a href="/summary" class="active">Daily summary</a>
    <a href="/plan">Daily plan</a>
</div>

<h1>Daily trading summary</h1>
<div class="subtitle">{target_date} | EA v{s.get('ea_version', '2.8')} | {s.get('symbol', 'SPXUSD')}</div>

<div class="nav">{nav_html}</div>

<div class="grid">
    <div class="card"><div class="val">{trend}</div><div class="lbl">Daily trend</div></div>
    <div class="card"><div class="val">{len(setups)}</div><div class="lbl">Setups found</div></div>
    <div class="card"><div class="val {('red' if len(rejections) == len(setups) and len(setups) > 0 else '')}">{len(rejections)}</div><div class="lbl">Rejected</div></div>
    <div class="card"><div class="val">{len(opens)}</div><div class="lbl">Trades</div></div>
    <div class="card"><div class="val {'green' if len(wins) > len(losses) else 'red' if losses else ''}">{len(wins)}/{len(losses)}</div><div class="lbl">Win/Loss</div></div>
    <div class="card"><div class="val {'green' if total_pnl > 0 else 'red' if total_pnl < 0 else ''}">${total_pnl:.2f}</div><div class="lbl">P&L</div></div>
</div>

<h2>Day grade</h2>
<div class="grade {'green' if grade in ('A','B') else 'yellow' if grade.startswith('C') else 'red' if grade == 'D' else 'blue'}">{grade}</div>

<h2>Analysis</h2>
<ul>{analysis_html}</ul>

<h2>Levels</h2>
<table>
<tr><th>Level</th><th>Price</th></tr>
{levels_html}
</table>

<h2>Trades</h2>
{trades_html}

<h2>Event timeline</h2>
<table>
<tr><th>Time</th><th>Event</th><th>Dir</th><th>Level</th><th>Candle</th><th>P&L</th><th>Notes</th></tr>
{timeline_html}
</table>

<h2>Casey's notes</h2>
<p style="color:#888">{s.get('user_notes', 'No notes yet. Add via POST /api/daily-note')}</p>

<h2>Lessons learned</h2>
<p style="color:#888">{s.get('lessons_learned', 'No lessons yet. Add via POST /api/daily-note')}</p>

<div style="margin-top:40px;padding-top:20px;border-top:1px solid #222;font-size:12px;color:#555">
    <a href="/">Back to dashboard</a> |
    <a href="/api/daily-log-markdown/{target_date}">Download markdown</a> |
    <a href="/api/today">Raw JSON</a>
</div>

</body></html>"""


# ======================== DASHBOARD ========================

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    today = date.today()
    async with pool.acquire() as conn:
        summary = await conn.fetchrow(
            "SELECT * FROM daily_summaries WHERE trade_date = $1", today
        )
        events_today = await conn.fetch(
            "SELECT * FROM trade_events WHERE timestamp_est::date = $1 ORDER BY timestamp_est",
            today
        )
        recent_days = await conn.fetch("""
            SELECT trade_date, total_pnl, trades_taken, trades_won, trades_lost, daily_trend, user_notes
            FROM daily_summaries ORDER BY trade_date DESC LIMIT 14
        """)
        all_time = await conn.fetchrow("""
            SELECT
                COUNT(*) as total_trades,
                SUM(CASE WHEN pnl_price > 0 THEN 1 ELSE 0 END) as wins,
                COALESCE(SUM(pnl_price), 0) as total_pnl,
                COALESCE(MAX(pnl_price), 0) as best,
                COALESCE(MIN(pnl_price), 0) as worst
            FROM trade_events WHERE event_type = 'TRADE_CLOSED'
        """)
        changelog = await conn.fetch(
            "SELECT * FROM system_changelog ORDER BY created_at DESC LIMIT 10"
        )

    s = dict(summary) if summary else {}
    at = dict(all_time) if all_time else {}
    win_rate = 0
    if at.get("total_trades", 0) > 0:
        win_rate = round(at["wins"] / at["total_trades"] * 100, 1)

    events_html = ""
    for e in events_today:
        e = dict(e)
        color = "#22c55e" if e.get("pnl_price", 0) > 0 else "#ef4444" if e.get("pnl_price", 0) < 0 else "#888"
        pnl_str = f"${e['pnl_price']:.2f}" if e.get("pnl_price") else ""
        events_html += f"""<tr>
            <td>{e['timestamp_est'].strftime('%H:%M') if e.get('timestamp_est') else ''}</td>
            <td><span class="tag">{e['event_type']}</span></td>
            <td>{e.get('direction','')}</td>
            <td>{e.get('level_name','')}</td>
            <td style="color:{color}">{pnl_str}</td>
            <td>{e.get('result','')}</td>
            <td style="font-size:12px">{e.get('notes','')}</td>
        </tr>"""

    days_html = ""
    for d in recent_days:
        d = dict(d)
        pnl = d.get("total_pnl", 0) or 0
        color = "#22c55e" if pnl > 0 else "#ef4444" if pnl < 0 else "#888"
        wr = 0
        taken = d.get("trades_taken", 0) or 0
        won = d.get("trades_won", 0) or 0
        if taken > 0:
            wr = round(won / taken * 100)
        days_html += f"""<tr>
            <td>{d['trade_date']}</td>
            <td>{d.get('daily_trend','')}</td>
            <td>{taken}</td>
            <td>{wr}%</td>
            <td style="color:{color}">${pnl:.2f}</td>
            <td style="font-size:12px">{d.get('user_notes','') or ''}</td>
        </tr>"""

    changelog_html = ""
    for c in changelog:
        c = dict(c)
        changelog_html += f"""<tr>
            <td>{c['created_at'].strftime('%Y-%m-%d') if c.get('created_at') else ''}</td>
            <td><b>v{c.get('version','')}</b></td>
            <td><span class="tag">{c.get('change_type','')}</span></td>
            <td>{c.get('description','')}</td>
            <td style="font-size:12px">{c.get('reason','')}</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>EST Liquidity Breakout — Trade Journal</title>
<style>
body{{font-family:-apple-system,system-ui,sans-serif;margin:0;padding:20px;background:#0a0a0a;color:#e0e0e0}}
h1{{font-size:20px;font-weight:500;margin:0 0 20px}}
h2{{font-size:16px;font-weight:500;margin:30px 0 10px;color:#aaa}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;margin-bottom:24px}}
.card{{background:#1a1a1a;border-radius:8px;padding:16px;text-align:center}}
.card .val{{font-size:24px;font-weight:500}}
.card .lbl{{font-size:12px;color:#888;margin-top:4px}}
.green{{color:#22c55e}}.red{{color:#ef4444}}.yellow{{color:#eab308}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
th{{text-align:left;color:#888;font-weight:400;padding:8px;border-bottom:1px solid #222}}
td{{padding:8px;border-bottom:1px solid #1a1a1a}}
.tag{{display:inline-block;padding:2px 8px;border-radius:4px;font-size:11px;background:#222;color:#aaa}}
.nav-tabs{{display:flex;gap:0;margin-bottom:20px;border-bottom:1px solid #333}}
.nav-tabs a{{padding:10px 20px;color:#888;text-decoration:none;font-size:14px;border-bottom:2px solid transparent}}
.nav-tabs a:hover{{color:#fff;background:#111}}
.nav-tabs a.active{{color:#fff;border-bottom:2px solid #60a5fa}}
</style></head><body>

<div class="nav-tabs">
    <a href="/" class="active">Dashboard</a>
    <a href="/summary">Daily summary</a>
    <a href="/plan">Daily plan</a>
</div>

<h1>EST Liquidity Breakout EA — Trade Journal</h1>

<div class="grid">
    <div class="card"><div class="val {'green' if (at.get('total_pnl',0) or 0) >= 0 else 'red'}">${at.get('total_pnl',0) or 0:.2f}</div><div class="lbl">All-time P&L</div></div>
    <div class="card"><div class="val">{at.get('total_trades',0) or 0}</div><div class="lbl">Total trades</div></div>
    <div class="card"><div class="val">{win_rate}%</div><div class="lbl">Win rate</div></div>
    <div class="card"><div class="val green">${at.get('best',0) or 0:.2f}</div><div class="lbl">Best trade</div></div>
    <div class="card"><div class="val red">${at.get('worst',0) or 0:.2f}</div><div class="lbl">Worst trade</div></div>
</div>

<h2>Today — {today}</h2>
<div class="grid">
    <div class="card"><div class="val">{s.get('trades_taken',0) or 0}</div><div class="lbl">Trades</div></div>
    <div class="card"><div class="val {'green' if (s.get('total_pnl',0) or 0) >= 0 else 'red'}">${s.get('total_pnl',0) or 0:.2f}</div><div class="lbl">P&L</div></div>
    <div class="card"><div class="val">{s.get('daily_trend','') or 'N/A'}</div><div class="lbl">Trend</div></div>
</div>

<table>
<tr><th>Time</th><th>Event</th><th>Dir</th><th>Level</th><th>P&L</th><th>Result</th><th>Notes</th></tr>
{events_html}
</table>

<h2>Daily history</h2>
<table>
<tr><th>Date</th><th>Trend</th><th>Trades</th><th>Win%</th><th>P&L</th><th>Notes</th></tr>
{days_html}
</table>

<h2>System changelog</h2>
<table>
<tr><th>Date</th><th>Version</th><th>Type</th><th>Change</th><th>Reason</th></tr>
{changelog_html}
</table>

<p style="color:#555;font-size:12px;margin-top:40px">Auto-refreshes on page load. API: /api/event, /api/stats, /api/today, /api/changelog</p>
</body></html>"""


@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

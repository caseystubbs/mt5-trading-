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

# ======================== AUTH ========================

def verify_key(key: str):
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

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
</style></head><body>
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

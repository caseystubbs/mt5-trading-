from __future__ import annotations

import json
import math
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from typing import Any, Dict, List, Optional

FEEDBACK_SCHEMA_SQL = """
ALTER TABLE macrofx_fills ADD COLUMN IF NOT EXISTS signal_score DOUBLE PRECISION;
ALTER TABLE macrofx_fills ADD COLUMN IF NOT EXISTS exit_reason TEXT;

CREATE TABLE IF NOT EXISTS macrofx_daily_equity (
    account_id TEXT NOT NULL,
    equity_date DATE NOT NULL,
    open_equity DOUBLE PRECISION NOT NULL,
    high_equity DOUBLE PRECISION NOT NULL,
    low_equity DOUBLE PRECISION NOT NULL,
    close_equity DOUBLE PRECISION NOT NULL,
    close_balance DOUBLE PRECISION,
    close_free_margin DOUBLE PRECISION,
    first_captured_at TIMESTAMPTZ NOT NULL,
    last_captured_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY(account_id, equity_date)
);
CREATE INDEX IF NOT EXISTS idx_macrofx_daily_equity_date
    ON macrofx_daily_equity(account_id, equity_date);

CREATE TABLE IF NOT EXISTS macrofx_feedback_reviews (
    id BIGSERIAL PRIMARY KEY,
    week_ending DATE NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    account_id TEXT,
    strategy_version TEXT NOT NULL DEFAULT 'macrofx-v1.1',
    metrics_json JSONB NOT NULL,
    report_markdown TEXT NOT NULL
);
"""

BACKFILL_DAILY_EQUITY_SQL = """
WITH ranked AS (
    SELECT
        account_id,
        (captured_at AT TIME ZONE 'America/New_York')::date AS equity_date,
        captured_at,
        equity,
        balance,
        free_margin,
        ROW_NUMBER() OVER (
            PARTITION BY account_id, (captured_at AT TIME ZONE 'America/New_York')::date
            ORDER BY captured_at ASC
        ) AS rn_first,
        ROW_NUMBER() OVER (
            PARTITION BY account_id, (captured_at AT TIME ZONE 'America/New_York')::date
            ORDER BY captured_at DESC
        ) AS rn_last
    FROM macrofx_heartbeats
    WHERE equity > 0
),
agg AS (
    SELECT
        account_id,
        equity_date,
        MAX(equity) FILTER (WHERE rn_first=1) AS open_equity,
        MAX(equity) AS high_equity,
        MIN(equity) AS low_equity,
        MAX(equity) FILTER (WHERE rn_last=1) AS close_equity,
        MAX(balance) FILTER (WHERE rn_last=1) AS close_balance,
        MAX(free_margin) FILTER (WHERE rn_last=1) AS close_free_margin,
        MIN(captured_at) AS first_captured_at,
        MAX(captured_at) AS last_captured_at
    FROM ranked
    GROUP BY account_id, equity_date
)
INSERT INTO macrofx_daily_equity(
    account_id,equity_date,open_equity,high_equity,low_equity,close_equity,
    close_balance,close_free_margin,first_captured_at,last_captured_at
)
SELECT
    account_id,equity_date,open_equity,high_equity,low_equity,close_equity,
    close_balance,close_free_margin,first_captured_at,last_captured_at
FROM agg
ON CONFLICT(account_id,equity_date) DO UPDATE SET
    open_equity=EXCLUDED.open_equity,
    high_equity=EXCLUDED.high_equity,
    low_equity=EXCLUDED.low_equity,
    close_equity=EXCLUDED.close_equity,
    close_balance=EXCLUDED.close_balance,
    close_free_margin=EXCLUDED.close_free_margin,
    first_captured_at=EXCLUDED.first_captured_at,
    last_captured_at=EXCLUDED.last_captured_at;
"""

async def ensure_feedback_schema(conn) -> None:
    await conn.execute(FEEDBACK_SCHEMA_SQL)
    await conn.execute(BACKFILL_DAILY_EQUITY_SQL)

async def upsert_daily_equity(conn, account_id: str, balance: float, equity: float, free_margin: float) -> None:
    if equity <= 0:
        return
    now = datetime.now(timezone.utc)
    equity_date = datetime.now(ZoneInfo("America/New_York")).date()
    await conn.execute(
        """
        INSERT INTO macrofx_daily_equity(
            account_id,equity_date,open_equity,high_equity,low_equity,close_equity,
            close_balance,close_free_margin,first_captured_at,last_captured_at
        )
        VALUES($1,$2,$3,$3,$3,$3,$4,$5,$6,$6)
        ON CONFLICT(account_id,equity_date) DO UPDATE SET
            high_equity=GREATEST(macrofx_daily_equity.high_equity,EXCLUDED.close_equity),
            low_equity=LEAST(macrofx_daily_equity.low_equity,EXCLUDED.close_equity),
            close_equity=EXCLUDED.close_equity,
            close_balance=EXCLUDED.close_balance,
            close_free_margin=EXCLUDED.close_free_margin,
            last_captured_at=EXCLUDED.last_captured_at
        """,
        account_id, equity_date, equity, balance, free_margin, now
    )

def _f(v: Any, default: float = 0.0) -> float:
    try:
        if v is None:
            return default
        return float(v)
    except Exception:
        return default

def _iso(v: Any) -> Optional[str]:
    if v is None:
        return None
    return v.isoformat() if hasattr(v, "isoformat") else str(v)

def _max_drawdown(values: List[float]) -> float:
    if not values:
        return 0.0
    peak = values[0]
    worst = 0.0
    for value in values:
        peak = max(peak, value)
        if peak > 0:
            worst = min(worst, value / peak - 1.0)
    return worst

async def build_feedback_snapshot(pool, account_id: Optional[str] = None, days: int = 120) -> Dict[str, Any]:
    async with pool.acquire() as conn:
        if not account_id:
            account_id = await conn.fetchval(
                "SELECT account_id FROM macrofx_heartbeats ORDER BY captured_at DESC LIMIT 1"
            )
        if not account_id:
            return {
                "account_id": None,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "trades": [],
                "summary": {},
                "daily_equity": [],
                "report_markdown": "# MacroFX Feedback\n\nNo demo account data yet.",
            }

        since = datetime.now(timezone.utc) - timedelta(days=max(30, days))
        open_rows = await conn.fetch(
            "SELECT * FROM macrofx_fills WHERE account_id=$1 "
            "AND action IN ('OPEN_LONG','OPEN_SHORT') AND captured_at >= $2 ORDER BY captured_at",
            account_id, since
        )
        close_rows = await conn.fetch(
            "SELECT * FROM macrofx_fills WHERE account_id=$1 "
            "AND action='CLOSE' AND captured_at >= $2 ORDER BY captured_at",
            account_id, since
        )
        excursion_rows = await conn.fetch(
            """
            SELECT ticket,
                   MIN(COALESCE(pnl,0)+COALESCE(swap,0)+COALESCE(commission,0)) AS mae_net,
                   MAX(COALESCE(pnl,0)+COALESCE(swap,0)+COALESCE(commission,0)) AS mfe_net,
                   MIN(current_price) AS min_price,
                   MAX(current_price) AS max_price,
                   COUNT(*) AS samples
            FROM macrofx_positions
            WHERE account_id=$1 AND captured_at >= $2 AND ticket IS NOT NULL
            GROUP BY ticket
            """,
            account_id, since
        )
        latest_position_rows = await conn.fetch(
            """
            SELECT DISTINCT ON (ticket)
                ticket,captured_at,symbol,side,lots,open_price,current_price,pnl,swap,commission
            FROM macrofx_positions
            WHERE account_id=$1 AND captured_at >= $2 AND ticket IS NOT NULL
            ORDER BY ticket,captured_at DESC
            """,
            account_id, since
        )
        active_target_rows = await conn.fetch(
            "SELECT symbol,direction,lots,score,reason FROM macrofx_targets "
            "WHERE active=TRUE AND expires_at>NOW() ORDER BY ABS(score) DESC"
        )
        daily_rows = await conn.fetch(
            "SELECT * FROM macrofx_daily_equity WHERE account_id=$1 AND equity_date >= $2 ORDER BY equity_date",
            account_id,
            datetime.now(ZoneInfo("America/New_York")).date() - timedelta(days=max(30, days))
        )
        latest_run = await conn.fetchrow(
            "SELECT week_ending,created_at,strategy_version,strongest_currency,weakest_currency,targets_json "
            "FROM macrofx_weekly_runs ORDER BY week_ending DESC LIMIT 1"
        )

    close_by_ticket = {int(r["ticket"]): dict(r) for r in close_rows}
    excursion_by_ticket = {int(r["ticket"]): dict(r) for r in excursion_rows}
    latest_by_ticket = {int(r["ticket"]): dict(r) for r in latest_position_rows}
    active_targets = {str(r["symbol"]): dict(r) for r in active_target_rows}

    trades: List[Dict[str, Any]] = []
    for raw in open_rows:
        opened = dict(raw)
        ticket = int(opened["ticket"])
        closed = close_by_ticket.get(ticket)
        excursion = excursion_by_ticket.get(ticket, {})
        latest = latest_by_ticket.get(ticket, {})
        symbol = str(opened["symbol"])
        target = active_targets.get(symbol)

        direction = "LONG" if opened["action"] == "OPEN_LONG" else "SHORT"
        opened_at = opened["captured_at"]
        ended_at = closed["captured_at"] if closed else None
        end_time = ended_at or datetime.now(timezone.utc)
        holding_hours = max(0.0, (end_time - opened_at).total_seconds() / 3600.0)

        entry_signal = opened.get("signal_score")
        if entry_signal is None and target:
            entry_signal = target.get("score")

        if closed:
            exit_signal = closed.get("signal_score")
            reason = closed.get("exit_reason") or closed.get("notes") or "closed"
            if exit_signal is None and reason == "target_removed":
                exit_signal = 0.0
            pnl = _f(closed.get("pnl"))
            swap = _f(closed.get("swap"))
            commission = _f(closed.get("commission"))
            net_pnl = pnl + swap + commission
            exit_price = _f(closed.get("fill_price"))
            status = "CLOSED"
        else:
            exit_signal = target.get("score") if target else 0.0
            reason = None
            pnl = _f(latest.get("pnl"))
            swap = _f(latest.get("swap"))
            commission = _f(latest.get("commission"))
            net_pnl = pnl + swap + commission
            exit_price = None
            status = "OPEN"

        trades.append({
            "ticket": ticket,
            "symbol": symbol,
            "direction": direction,
            "status": status,
            "lots": _f(opened.get("lots")),
            "opened_at": _iso(opened_at),
            "closed_at": _iso(ended_at),
            "holding_hours": holding_hours,
            "entry_price": _f(opened.get("fill_price")),
            "exit_price": exit_price,
            "entry_signal_score": None if entry_signal is None else _f(entry_signal),
            "exit_signal_score": None if exit_signal is None else _f(exit_signal),
            "entry_spread_points": _f(opened.get("spread_points")),
            "entry_slippage_points": _f(opened.get("slippage_points")),
            "pnl": pnl,
            "swap": swap,
            "commission": commission,
            "costs": swap + commission,
            "net_pnl": net_pnl,
            "mae_net": _f(excursion.get("mae_net")),
            "mfe_net": _f(excursion.get("mfe_net")),
            "min_price_seen": _f(excursion.get("min_price")),
            "max_price_seen": _f(excursion.get("max_price")),
            "position_samples": int(excursion.get("samples") or 0),
            "exit_reason": reason,
        })

    closed_trades = [t for t in trades if t["status"] == "CLOSED"]
    open_trades = [t for t in trades if t["status"] == "OPEN"]
    winners = [t for t in closed_trades if t["net_pnl"] > 0]
    losers = [t for t in closed_trades if t["net_pnl"] < 0]

    gross_profit = sum(t["net_pnl"] for t in winners)
    gross_loss = abs(sum(t["net_pnl"] for t in losers))
    net_closed = sum(t["net_pnl"] for t in closed_trades)
    avg_closed = net_closed / len(closed_trades) if closed_trades else 0.0
    win_rate = len(winners) / len(closed_trades) if closed_trades else None
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else (None if not winners else math.inf)

    daily_equity = []
    for row in daily_rows:
        r = dict(row)
        daily_equity.append({
            "date": str(r["equity_date"]),
            "open": _f(r["open_equity"]),
            "high": _f(r["high_equity"]),
            "low": _f(r["low_equity"]),
            "close": _f(r["close_equity"]),
            "balance": _f(r["close_balance"]),
            "free_margin": _f(r["close_free_margin"]),
        })

    closes = [x["close"] for x in daily_equity if x["close"] > 0]
    equity_start = closes[0] if closes else 0.0
    equity_end = closes[-1] if closes else 0.0
    equity_return = (equity_end / equity_start - 1.0) if equity_start > 0 and len(closes) > 1 else 0.0
    max_dd = _max_drawdown(closes)

    entry_slips = [t["entry_slippage_points"] for t in trades]
    entry_spreads = [t["entry_spread_points"] for t in trades]

    summary = {
        "closed_trades": len(closed_trades),
        "open_trades": len(open_trades),
        "wins": len(winners),
        "losses": len(losers),
        "win_rate": win_rate,
        "net_closed_pnl": net_closed,
        "avg_closed_pnl": avg_closed,
        "gross_profit": gross_profit,
        "gross_loss": gross_loss,
        "profit_factor": profit_factor,
        "total_costs": sum(t["costs"] for t in trades),
        "avg_mae_closed": sum(t["mae_net"] for t in closed_trades) / len(closed_trades) if closed_trades else 0.0,
        "avg_mfe_closed": sum(t["mfe_net"] for t in closed_trades) / len(closed_trades) if closed_trades else 0.0,
        "avg_entry_slippage_points": sum(entry_slips) / len(entry_slips) if entry_slips else 0.0,
        "avg_entry_spread_points": sum(entry_spreads) / len(entry_spreads) if entry_spreads else 0.0,
        "equity_start": equity_start,
        "equity_end": equity_end,
        "equity_return": equity_return,
        "max_daily_close_drawdown": max_dd,
    }

    latest = dict(latest_run) if latest_run else {}
    lines = [
        f"# MacroFX Feedback Review — {latest.get('week_ending') or datetime.now(ZoneInfo('America/New_York')).date()}",
        "",
        f"- Account: {account_id}",
        f"- Strategy: {latest.get('strategy_version') or 'macrofx-v1.1'}",
        f"- Strongest currency: {latest.get('strongest_currency') or 'N/A'}",
        f"- Weakest currency: {latest.get('weakest_currency') or 'N/A'}",
        f"- Open trades: {len(open_trades)}",
        f"- Closed trades in review window: {len(closed_trades)}",
        f"- Closed net P&L: ${net_closed:,.2f}",
        f"- Total observed swap + commission: ${summary['total_costs']:,.2f}",
        f"- Daily-close max drawdown: {max_dd:.2%}",
        "",
        "## Trade review",
        "",
        "| Pair | Side | Status | Entry score | Current/exit score | Net P&L | MAE | MFE | Hours | Exit reason |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]

    if trades:
        for t in sorted(trades, key=lambda x: x["opened_at"]):
            es = "N/A" if t["entry_signal_score"] is None else f"{t['entry_signal_score']:+.3f}"
            xs = "N/A" if t["exit_signal_score"] is None else f"{t['exit_signal_score']:+.3f}"
            lines.append(
                f"| {t['symbol']} | {t['direction']} | {t['status']} | {es} | {xs} | "
                f"${t['net_pnl']:+.2f} | ${t['mae_net']:+.2f} | ${t['mfe_net']:+.2f} | "
                f"{t['holding_hours']:.1f} | {t['exit_reason'] or '—'} |"
            )
    else:
        lines.append("| — | — | — | — | — | — | — | — | — | — |")

    lines += [
        "",
        "## Execution quality",
        "",
        f"- Average recorded entry spread: {summary['avg_entry_spread_points']:.2f} points",
        f"- Average recorded entry slippage: {summary['avg_entry_slippage_points']:.2f} points",
        "",
        "## Research discipline",
        "",
    ]

    if len(closed_trades) < 10:
        lines.append(
            f"- Only {len(closed_trades)} completed trades are available. Treat patterns as observations, not strategy-change evidence."
        )
    else:
        if win_rate is not None:
            lines.append(f"- Completed-trade win rate: {win_rate:.1%}")
        if profit_factor is not None and math.isfinite(profit_factor):
            lines.append(f"- Profit factor: {profit_factor:.2f}")
        lines.append("- Any rule change must be tested against the frozen current version before adoption.")

    lines += [
        "- Track whether higher absolute entry scores produce better net outcomes.",
        "- Track whether MFE is repeatedly surrendered before weekly exits.",
        "- Track whether MAE clusters tightly enough to justify a volatility stop test.",
        "- Track broker drag separately from signal quality: spread, slippage, swap and commission.",
        "- Never change horizons or thresholds because of one trade or one week.",
    ]

    report = "\n".join(lines)

    return {
        "account_id": account_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "latest_week": {
            "week_ending": str(latest.get("week_ending")) if latest else None,
            "strongest_currency": latest.get("strongest_currency") if latest else None,
            "weakest_currency": latest.get("weakest_currency") if latest else None,
            "strategy_version": latest.get("strategy_version") if latest else "macrofx-v1.1",
        },
        "summary": summary,
        "trades": trades,
        "daily_equity": daily_equity,
        "report_markdown": report,
    }

async def save_feedback_review(pool, week_ending, snapshot: Dict[str, Any]) -> None:
    payload = dict(snapshot)
    report = payload.pop("report_markdown", "")
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO macrofx_feedback_reviews(
                week_ending,account_id,strategy_version,metrics_json,report_markdown
            )
            VALUES($1,$2,$3,$4::jsonb,$5)
            ON CONFLICT(week_ending) DO UPDATE SET
                created_at=NOW(),
                account_id=EXCLUDED.account_id,
                strategy_version=EXCLUDED.strategy_version,
                metrics_json=EXCLUDED.metrics_json,
                report_markdown=EXCLUDED.report_markdown
            """,
            week_ending,
            snapshot.get("account_id"),
            snapshot.get("latest_week", {}).get("strategy_version") or "macrofx-v1.1",
            json.dumps(payload, default=str),
            report,
        )

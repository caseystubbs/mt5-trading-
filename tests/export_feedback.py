"""Read-only export of MacroFX history for strategy review. Writes nothing."""
import asyncio
import json
import os
import time

import asyncpg


def out(tag, rows):
    for r in rows:
        print("EXPORT", tag, json.dumps({k: (v if isinstance(v, (int, float, str, bool, type(None))) else str(v))
                                         for k, v in dict(r).items()}), flush=True)


async def main():
    conn = await asyncpg.connect(os.environ["DATABASE_URL"])
    await conn.execute("SET default_transaction_read_only = on")
    out("run", await conn.fetch("""SELECT id,week_ending,created_at,strategy_version,strongest_currency,weakest_currency,
        targets_json,snapshot_json FROM macrofx_weekly_runs ORDER BY week_ending"""))
    out("target", await conn.fetch("""SELECT weekly_run_id,symbol,direction,lots,score,active,created_at,expires_at
        FROM macrofx_targets ORDER BY weekly_run_id,symbol"""))
    out("fill", await conn.fetch("SELECT * FROM macrofx_fills ORDER BY captured_at"))
    out("equity", await conn.fetch("SELECT * FROM macrofx_daily_equity ORDER BY equity_date"))
    out("review", await conn.fetch("""SELECT week_ending,created_at,account_id,strategy_version,metrics_json
        FROM macrofx_feedback_reviews ORDER BY week_ending"""))
    out("bars", await conn.fetch("""SELECT symbol,COUNT(*) n,MIN(bar_date) first,MAX(bar_date) last
        FROM macrofx_daily_bars GROUP BY symbol ORDER BY symbol"""))
    out("possum", await conn.fetch("""SELECT symbol,ticket,side,MIN(captured_at) first_seen,MAX(captured_at) last_seen,
        MIN(pnl) mae,MAX(pnl) mfe,MAX(swap) swap_max,MIN(swap) swap_min,MAX(magic) magic
        FROM macrofx_positions WHERE magic=26092601 GROUP BY symbol,ticket,side ORDER BY first_seen"""))
    await conn.close()
    print("EXPORT DONE", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
    while True:
        time.sleep(3600)

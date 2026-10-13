"""Batch 1: EA-side entry guards on the real demo terminal.

Authorized by Casey 2026-10-13 15:31 ET. Demo account only.
Frees one slot by closing a bridge position, then sends opens that the EA
must refuse (paused, spread limit, duplicate pair, unknown symbol), then
restores the original position (same pair/direction, 0.01).

If any guard unexpectedly opens a position, that ticket is closed
immediately (or kept if it is exactly the position being restored).
"""
import asyncio
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

import asyncpg

BASE = os.environ.get("TARGET_URL", "https://mt5.freedomincomeoptions.com").rstrip("/")
EA = {"X-EA-API-Key": os.environ["EA_API_KEY"]}
ADMIN = {"X-MacroFX-Admin-Key": os.environ["MACROFX_ADMIN_KEY"]}
DB = os.environ["DATABASE_URL"]
REAL = os.environ.get("REAL_ACCOUNT", "1041307")
FREE_TICKET = int(os.environ.get("GUARD_FREE_TICKET", "8950352"))
FREE_SYMBOL = os.environ.get("GUARD_FREE_SYMBOL", "EURAUD")
KEEP_SYMBOL = os.environ.get("GUARD_KEEP_SYMBOL", "NZDUSD")
MAGIC = 26092601
REASON = "Claude batch 1 EA guard test"
RESULTS = []


def req(method, path, params=None, headers=None, body=None):
    url = BASE + path + ("?" + urllib.parse.urlencode(params) if params else "")
    h = dict(headers or {})
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        h["Content-Type"] = "application/json"
    r = urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def log(*a):
    print(time.strftime("%H:%M:%SZ", time.gmtime()), *a, flush=True)


def check(name, ok, detail=""):
    RESULTS.append(bool(ok))
    log(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    return bool(ok)


def settings(pause, spread=300):
    s, _ = req("POST", "/api/macrofx/v2/admin/settings", headers=ADMIN, body={
        "account_id": REAL, "enabled": True, "pause_entries": pause, "max_positions": 2,
        "max_lot_per_pair": 0.01, "max_spread_points": spread, "slippage_points": 30})
    return s


def create(action, **kw):
    s, b = req("POST", "/api/macrofx/v2/admin/commands", headers=ADMIN,
               body={"account_id": REAL, "action": action, "reason": REASON, **kw})
    return s, (json.loads(b).get("command_id") if s == 200 else b)


async def run_command(conn, action, **kw):
    s, cid = create(action, **kw)
    if s != 200:
        log("INFO create failed", s, cid)
        return None
    deadline = time.time() + 240
    while time.time() < deadline:
        row = await conn.fetchrow("SELECT * FROM macrofx_v2_commands WHERE command_id=$1", uuid.UUID(cid))
        if row["status"] in ("ACKED", "FAILED", "CANCELLED"):
            break
        await asyncio.sleep(3)
    log("INFO", action, kw, "->", cid, row["status"], row["result"],
        "claimed", row["claimed_at"], "acked", row["acknowledged_at"])
    return row


async def positions(conn, after):
    deadline = time.time() + 150
    while time.time() < deadline:
        s = await conn.fetchrow("SELECT captured_at,positions_json FROM macrofx_v2_position_snapshots WHERE account_id=$1", REAL)
        if s and s["captured_at"] > after:
            p = s["positions_json"]
            p = json.loads(p) if isinstance(p, str) else p
            return [x for x in p if int(x.get("magic", 0)) == MAGIC]
        await asyncio.sleep(5)
    return None


def opened_ticket(row):
    r = (row["result"] or "") if row else ""
    return int(r.rsplit("_", 1)[1]) if r.startswith("opened_ticket_") else None


async def main():
    conn = await asyncpg.connect(DB)
    if not await conn.fetchval("SELECT pg_try_advisory_lock(hashtext('macrofx_live_demo_trade'))"):
        log("INFO another test holds the lock; exiting without changes")
        return
    original = await conn.fetchrow("SELECT * FROM macrofx_v2_settings WHERE account_id=$1", REAL)
    started = await conn.fetchval("SELECT NOW()")
    restored = False
    freed = False
    try:
        hb = await conn.fetchrow("""SELECT is_demo,ea_version,NOW()-captured_at AS age FROM macrofx_heartbeats
            WHERE account_id=$1 ORDER BY captured_at DESC LIMIT 1""", REAL)
        if not check("G1 demo, fresh, EA v2.02", hb and hb["is_demo"] and hb["age"].total_seconds() < 180
                     and "2.02" in (hb["ea_version"] or ""), hb and hb["ea_version"]):
            return
        if not check("G2 no unresolved commands", await conn.fetchval(
                "SELECT COUNT(*) FROM macrofx_v2_commands WHERE account_id=$1 AND status IN ('PENDING','CLAIMED')", REAL) == 0):
            return
        pos = await positions(conn, started - __import__("datetime").timedelta(minutes=2))
        log("INFO positions before:", pos)
        tgt = next((p for p in pos or [] if int(p["ticket"]) == FREE_TICKET), None)
        if not check("G3 slot-to-free ticket present, short 0.01", tgt and FREE_SYMBOL in tgt["symbol"]
                     and str(tgt["side"]).upper() in ("SHORT", "SELL") and abs(float(tgt["lots"]) - 0.01) < 1e-9, tgt):
            return
        check("G4 two bridge positions before", len(pos) == 2, len(pos))

        # Free a slot
        settings(pause=True)
        row = await run_command(conn, "CLOSE_TICKET", ticket=FREE_TICKET)
        if not check("G5 close to free a slot", row and row["status"] == "ACKED" and row["result"] == "closed",
                     row and row["result"]):
            log("ABORT: slot not freed; no opens sent")
            return
        freed = True
        pos = await positions(conn, row["acknowledged_at"])
        check("G6 one bridge position after close", pos is not None and len(pos) == 1, pos)

        async def guard(name, expected, action, **kw):
            row = await run_command(conn, action, **kw)
            ok = check(name, row and row["status"] == "FAILED" and row["result"] == expected,
                       row and f"{row['status']} {row['result']}")
            t = opened_ticket(row)
            if t:  # guard failed and a position opened: repair immediately
                log("WARN guard let an order through, ticket", t)
                if kw.get("symbol") == FREE_SYMBOL and action == "OPEN_SHORT":
                    return t  # this is the position we were going to restore anyway
                settings(pause=True)
                fix = await run_command(conn, "CLOSE_TICKET", ticket=t)
                check(f"{name} repair close", fix and fix["status"] == "ACKED", fix and fix["result"])
            return None

        settings(pause=True)
        t = await guard("G7 paused entries refuse an open", "entries_paused", "OPEN_SHORT", symbol=FREE_SYMBOL, lots=0.01)
        if t:
            restored = True
        if not restored:
            settings(pause=False, spread=0)
            t = await guard("G8 spread limit 0 refuses an open", "spread_or_quote_block", "OPEN_SHORT", symbol=FREE_SYMBOL, lots=0.01)
            if t:
                restored = True
        settings(pause=False, spread=300)
        await guard("G9 duplicate pair refused", "pair_already_open", "OPEN_SHORT", symbol=KEEP_SYMBOL, lots=0.01)
        settings(pause=False, spread=300)
        await guard("G10 unknown 6-letter symbol refused", "pair_or_lot_limit", "OPEN_LONG", symbol="ABCDEF", lots=0.01)

        # Restore the freed position
        if not restored:
            settings(pause=False, spread=300)
            row = await run_command(conn, "OPEN_SHORT", symbol=FREE_SYMBOL, lots=0.01)
            settings(pause=True)
            t = opened_ticket(row)
            restored = check("G11 restore position (ACKED/opened)", t is not None, row and f"{row['status']} {row['result']}")
            if t:
                log("INFO restored", FREE_SYMBOL, "SHORT 0.01 ticket", t)
        settings(pause=True)
        pos = await positions(conn, await conn.fetchval("SELECT NOW()"))
        log("INFO positions after:", pos)
        check("G12 back to 2 bridge positions, one per pair, both short 0.01",
              pos is not None and len(pos) == 2 and len({p["symbol"] for p in pos}) == 2
              and all(str(p["side"]).upper() in ("SHORT", "SELL") and abs(float(p["lots"]) - 0.01) < 1e-9 for p in pos), pos)
        await asyncio.sleep(5)
        fills = await conn.fetch("""SELECT captured_at,symbol,ticket,action,lots,fill_price,spread_points,slippage_points,pnl,commission
            FROM macrofx_fills WHERE account_id=$1 AND captured_at>=$2 ORDER BY captured_at""", REAL, started)
        log("INFO fills:", [{k: str(v) for k, v in dict(f).items()} for f in fills])
    finally:
        if freed and not restored:
            log("WARN freed slot NOT restored — manual review: reopen", FREE_SYMBOL, "SHORT 0.01")
        settings(pause=True)
        if original:
            await conn.execute("""UPDATE macrofx_v2_settings SET enabled=$2,pause_entries=$3,max_positions=$4,
                max_lot_per_pair=$5,max_spread_points=$6,slippage_points=$7,revision=revision+1,updated_at=NOW()
                WHERE account_id=$1""", REAL, original["enabled"], original["pause_entries"], original["max_positions"],
                original["max_lot_per_pair"], original["max_spread_points"], original["slippage_points"])
        else:
            await conn.execute("DELETE FROM macrofx_v2_settings WHERE account_id=$1", REAL)
        await conn.execute("""UPDATE macrofx_v2_commands SET status='CANCELLED',result='cancelled_by_test_cleanup'
            WHERE account_id=$1 AND status='PENDING' AND reason=$2""", REAL, REASON)
        s, t = req("GET", "/api/macrofx/v2/control-text", {"account_id": REAL}, EA)
        check("G13 remote control restored to disabled", s == 200 and "ENABLED,0" in t, t.replace("\n", "|"))
        check("G14 no command left CLAIMED", await conn.fetchval(
            "SELECT COUNT(*) FROM macrofx_v2_commands WHERE account_id=$1 AND status='CLAIMED'", REAL) == 0)
        await conn.close()
        log(f"SUMMARY guard_tests passed={sum(RESULTS)} failed={len(RESULTS)-sum(RESULTS)} total={len(RESULTS)}")


if __name__ == "__main__":
    asyncio.run(main())
    log("RUNNER DONE - idle")
    while True:
        time.sleep(3600)

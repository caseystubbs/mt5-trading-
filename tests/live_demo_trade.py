"""Authorized demo broker execution test (Phase D) — demo account only.

Authorized by Casey 2026-10-13 14:58 ET ("lets just test it now").
Sequence: close one bridge-owned position via CLOSE_TICKET, reopen the same
pair/direction at 0.01 via OPEN_*, then attempt a duplicate open (must be
blocked by EA guards). Restores remote control to disabled at the end.

Safety:
- Single-instance: a Postgres advisory lock; a second copy exits untouched.
- Aborts before any order if the account is not a fresh v2.02 demo heartbeat,
  if commands are unresolved, or if the target ticket is not as expected.
- Never retries an order. If the close does not ACK, the open is not sent.
- pause_entries is TRUE except for the open and duplicate-open steps.
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
TICKET = int(os.environ.get("CLOSE_TICKET", "8984249"))
SYMBOL = os.environ.get("TRADE_SYMBOL", "NZDUSD")
DIRECTION = os.environ.get("TRADE_DIRECTION", "SHORT")
MAGIC = 26092601
WAIT = 240
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


def settings(pause):
    return req("POST", "/api/macrofx/v2/admin/settings", headers=ADMIN, body={
        "account_id": REAL, "enabled": True, "pause_entries": pause, "max_positions": 2,
        "max_lot_per_pair": 0.01, "max_spread_points": 300, "slippage_points": 30})


def create(action, **kw):
    s, b = req("POST", "/api/macrofx/v2/admin/commands", headers=ADMIN, body={
        "account_id": REAL, "action": action, "reason": "Claude authorized demo execution test", **kw})
    return s, (json.loads(b).get("command_id") if s == 200 else b)


async def wait_done(conn, cid):
    deadline = time.time() + WAIT
    while time.time() < deadline:
        row = await conn.fetchrow("SELECT * FROM macrofx_v2_commands WHERE command_id=$1", uuid.UUID(cid))
        if row["status"] in ("ACKED", "FAILED", "CANCELLED"):
            break
        await asyncio.sleep(3)
    d = {k: (str(v) if v is not None else None) for k, v in dict(row).items() if k != "claim_token"}
    log("INFO command", d)
    return row


async def snapshot(conn, after):
    """Wait for a position snapshot captured after `after`."""
    deadline = time.time() + 150
    while time.time() < deadline:
        s = await conn.fetchrow("SELECT captured_at,positions_json FROM macrofx_v2_position_snapshots WHERE account_id=$1", REAL)
        if s and s["captured_at"] > after:
            p = s["positions_json"]
            return json.loads(p) if isinstance(p, str) else p
        await asyncio.sleep(5)
    return None


async def fills_since(conn, ts):
    rows = await conn.fetch("""SELECT captured_at,symbol,ticket,action,lots,requested_price,fill_price,
        spread_points,slippage_points,pnl,commission,exit_reason,notes FROM macrofx_fills
        WHERE account_id=$1 AND captured_at>=$2 ORDER BY captured_at""", REAL, ts)
    return [{k: (str(v) if v is not None else None) for k, v in dict(r).items()} for r in rows]


async def main():
    conn = await asyncpg.connect(DB)
    if not await conn.fetchval("SELECT pg_try_advisory_lock(hashtext('macrofx_live_demo_trade'))"):
        log("INFO another instance holds the test lock; exiting without changes")
        await conn.close()
        return
    original = await conn.fetchrow("SELECT * FROM macrofx_v2_settings WHERE account_id=$1", REAL)
    started = await conn.fetchval("SELECT NOW()")
    try:
        # ---- Preconditions ----
        hb = await conn.fetchrow("""SELECT is_demo,ea_version,NOW()-captured_at AS age,balance,equity FROM macrofx_heartbeats
            WHERE account_id=$1 ORDER BY captured_at DESC LIMIT 1""", REAL)
        if not check("D1 demo 1041307, fresh heartbeat, EA v2.02",
                     hb and hb["is_demo"] and hb["age"].total_seconds() < 180 and "2.02" in (hb["ea_version"] or ""),
                     hb and f"{hb['ea_version']} age={int(hb['age'].total_seconds())}s bal={hb['balance']} eq={hb['equity']}"):
            return
        unresolved = await conn.fetchval("SELECT COUNT(*) FROM macrofx_v2_commands WHERE account_id=$1 AND status IN ('PENDING','CLAIMED')", REAL)
        if not check("D2 no unresolved commands", unresolved == 0, unresolved):
            return
        pos = await snapshot(conn, started - __import__("datetime").timedelta(minutes=2))
        log("INFO positions before:", pos)
        owned = [p for p in (pos or []) if int(p.get("magic", 0)) == MAGIC]
        target = next((p for p in owned if int(p["ticket"]) == TICKET), None)
        if not check("D3 target ticket is bridge-owned, expected pair/direction/size",
                     target and SYMBOL in target["symbol"] and str(target["side"]).upper() in (DIRECTION, "SELL" if DIRECTION == "SHORT" else "BUY")
                     and abs(float(target["lots"]) - 0.01) < 1e-9, target):
            return
        check("D4 bridge positions before test", len(owned) == 2, len(owned))

        # ---- Close ----
        s, _ = settings(pause=True)
        if not check("D5 remote enabled (entries paused) for close", s == 200, s):
            return
        s, close_id = create("CLOSE_TICKET", ticket=TICKET)
        if not check("D6 CLOSE_TICKET created", s == 200, close_id):
            return
        row = await wait_done(conn, close_id)
        if not check("D7 EA closed the ticket (ACKED/closed)", row["status"] == "ACKED" and row["result"] == "closed",
                     f"{row['status']} {row['result']}"):
            log("ABORT: close not confirmed; open step NOT sent. Manual review required.")
            return
        pos = await snapshot(conn, row["acknowledged_at"])
        log("INFO positions after close:", pos)
        check("D8 closed ticket absent from Railway snapshot",
              pos is not None and all(int(p["ticket"]) != TICKET for p in pos))
        s, _ = req("POST", "/api/macrofx/v2/claim", {"account_id": REAL, "command_id": close_id}, EA)
        check("D9 close command cannot be claimed again", s == 409, s)

        # ---- Open ----
        s, _ = settings(pause=False)
        check("D10 entries resumed for open step", s == 200, s)
        s, open_id = create("OPEN_SHORT" if DIRECTION == "SHORT" else "OPEN_LONG", symbol=SYMBOL, lots=0.01)
        if not check("D11 OPEN command created", s == 200, open_id):
            return
        row = await wait_done(conn, open_id)
        settings(pause=True)  # re-pause immediately after the open resolves
        ok = check("D12 EA opened position (ACKED/opened_ticket_N)",
                   row["status"] == "ACKED" and (row["result"] or "").startswith("opened_ticket_"),
                   f"{row['status']} {row['result']}")
        new_ticket = int(row["result"].rsplit("_", 1)[1]) if ok else None
        if ok:
            pos = await snapshot(conn, row["acknowledged_at"])
            log("INFO positions after open:", pos)
            mine = [p for p in pos or [] if int(p["ticket"]) == new_ticket]
            check("D13 new ticket in Railway snapshot with pair/direction/0.01/magic",
                  len(mine) == 1 and SYMBOL in mine[0]["symbol"] and abs(float(mine[0]["lots"]) - 0.01) < 1e-9
                  and int(mine[0]["magic"]) == MAGIC, mine)
            check("D14 bridge-owned positions back to 2",
                  len([p for p in pos or [] if int(p.get("magic", 0)) == MAGIC]) == 2)
            s, _ = req("POST", "/api/macrofx/v2/claim", {"account_id": REAL, "command_id": open_id}, EA)
            check("D15 open command cannot be claimed again", s == 409, s)

            # ---- Duplicate open must be blocked by EA guards ----
            settings(pause=False)
            s, dup_id = create("OPEN_SHORT" if DIRECTION == "SHORT" else "OPEN_LONG", symbol=SYMBOL, lots=0.01)
            if check("D16 duplicate open command created (to test EA guard)", s == 200, dup_id):
                row = await wait_done(conn, dup_id)
                settings(pause=True)
                check("D17 EA refused duplicate open (position_limit / pair_already_open)",
                      row["status"] == "FAILED" and row["result"] in ("position_limit", "pair_already_open"),
                      f"{row['status']} {row['result']}")
                pos = await snapshot(conn, row["acknowledged_at"] or row["created_at"])
                check("D18 still exactly 2 bridge positions, one per pair",
                      pos is not None and len([p for p in pos if int(p.get("magic", 0)) == MAGIC]) == 2, pos)

        await asyncio.sleep(10)
        fills = await fills_since(conn, started)
        log("INFO fills recorded:", fills)
        check("D19 close fill stored", any(f["action"] == "CLOSE" and f["ticket"] == str(TICKET) for f in fills))
        if new_ticket:
            check("D20 open fill stored", any(f["ticket"] == str(new_ticket) and f["action"].startswith("OPEN") for f in fills))
    finally:
        settings(pause=True)
        if original:
            await conn.execute("""UPDATE macrofx_v2_settings SET enabled=$2,pause_entries=$3,max_positions=$4,
                max_lot_per_pair=$5,max_spread_points=$6,slippage_points=$7,revision=revision+1,updated_at=NOW()
                WHERE account_id=$1""", REAL, original["enabled"], original["pause_entries"], original["max_positions"],
                original["max_lot_per_pair"], original["max_spread_points"], original["slippage_points"])
        else:
            await conn.execute("DELETE FROM macrofx_v2_settings WHERE account_id=$1", REAL)
        await conn.execute("""UPDATE macrofx_v2_commands SET status='CANCELLED',result='cancelled_by_test_cleanup'
            WHERE account_id=$1 AND status='PENDING' AND reason='Claude authorized demo execution test'""", REAL)
        s, t = req("GET", "/api/macrofx/v2/control-text", {"account_id": REAL}, EA)
        check("D21 remote control restored to disabled", s == 200 and "ENABLED,0" in t, t.replace("\n", "|"))
        claimed = await conn.fetchval("SELECT COUNT(*) FROM macrofx_v2_commands WHERE account_id=$1 AND status='CLAIMED'", REAL)
        check("D22 no command left CLAIMED (uncertain outcome)", claimed == 0, claimed)
        await conn.close()
        log(f"SUMMARY demo_trade passed={sum(RESULTS)} failed={len(RESULTS)-sum(RESULTS)} total={len(RESULTS)}")


if __name__ == "__main__":
    asyncio.run(main())
    log("RUNNER DONE - idle")
    while True:
        time.sleep(3600)

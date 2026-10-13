"""Batch 2: terminal restart + network outage behaviour (demo only).

Authorized by Casey 2026-10-13. The runner waits for Casey's actions:
  Phase R: Casey exits MT4 -> runner sees heartbeats stop, queues a harmless
           PAUSE_ENTRIES with remote control enabled (entries paused).
           Casey waits >= 6 minutes, restarts MT4. The command has expired and
           must never be claimed after the restart.
  Phase N: Casey disconnects the PC from the internet ~3 minutes, reconnects.
           Remote control is disabled; the EA must resume cleanly with the
           same positions and no commands executed.
No orders are sent in this batch.
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
MAGIC = 26092601
GAP = 100          # seconds without heartbeat => terminal offline (EA polls every 60s)
REASON = "Claude batch 2 restart test"
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


async def last_hb(conn):
    return await conn.fetchrow("""SELECT captured_at,NOW()-captured_at AS age,ea_version FROM macrofx_heartbeats
        WHERE account_id=$1 ORDER BY captured_at DESC LIMIT 1""", REAL)


async def wait_offline(conn, label, limit=3600):
    log(f"WAITING for MT4 to go offline ({label})")
    deadline = time.time() + limit
    while time.time() < deadline:
        hb = await last_hb(conn)
        if hb["age"].total_seconds() >= GAP:
            log(f"OFFLINE detected ({label}); last heartbeat {hb['captured_at']}")
            return hb["captured_at"]
        await asyncio.sleep(5)
    return None


async def wait_online(conn, since, label, limit=3600):
    log(f"WAITING for MT4 to come back ({label})")
    deadline = time.time() + limit
    while time.time() < deadline:
        hb = await last_hb(conn)
        if hb["captured_at"] > since:
            log(f"ONLINE again ({label}); heartbeat {hb['captured_at']} {hb['ea_version']}")
            return hb["captured_at"]
        await asyncio.sleep(5)
    return None


async def snapshot(conn):
    s = await conn.fetchrow("SELECT captured_at,positions_json FROM macrofx_v2_position_snapshots WHERE account_id=$1", REAL)
    p = s["positions_json"]
    p = json.loads(p) if isinstance(p, str) else p
    return s["captured_at"], sorted((x["symbol"], int(x["ticket"]), x["side"], float(x["lots"]))
                                    for x in p if int(x.get("magic", 0)) == MAGIC)


async def main():
    conn = await asyncpg.connect(DB)
    if not await conn.fetchval("SELECT pg_try_advisory_lock(hashtext('macrofx_live_demo_trade'))"):
        log("INFO another test holds the lock; exiting")
        return
    original = await conn.fetchrow("SELECT * FROM macrofx_v2_settings WHERE account_id=$1", REAL)
    cid = None
    try:
        hb = await last_hb(conn)
        if not check("S1 EA online, v2.02", hb["age"].total_seconds() < 90 and "2.02" in hb["ea_version"], hb["ea_version"]):
            return
        if not check("S2 no unresolved commands", await conn.fetchval(
                "SELECT COUNT(*) FROM macrofx_v2_commands WHERE account_id=$1 AND status IN ('PENDING','CLAIMED')", REAL) == 0):
            return
        _, before = await snapshot(conn)
        log("INFO bridge positions at start:", before)

        # ---------------- Phase R: restart ----------------
        log("READY FOR STEP 1: close MT4 completely now (File > Exit)")
        off = await wait_offline(conn, "restart")
        if not check("R1 terminal offline detected", off is not None):
            return
        s, _ = req("POST", "/api/macrofx/v2/admin/settings", headers=ADMIN, body={
            "account_id": REAL, "enabled": True, "pause_entries": True, "max_positions": 2,
            "max_lot_per_pair": 0.01, "max_spread_points": 300, "slippage_points": 30})
        check("R2 remote enabled (entries paused) while terminal offline", s == 200, s)
        s, b = req("POST", "/api/macrofx/v2/admin/commands", headers=ADMIN,
                   body={"account_id": REAL, "action": "PAUSE_ENTRIES", "reason": REASON})
        check("R3 command queued while terminal offline", s == 200, s)
        cid = json.loads(b)["command_id"] if s == 200 else None
        created = await conn.fetchval("SELECT created_at FROM macrofx_v2_commands WHERE command_id=$1", uuid.UUID(cid))
        log(f"INFO command {cid} created {created}; expires 5 min later. KEEP MT4 CLOSED until 6 minutes have passed.")
        on = await wait_online(conn, off, "restart")
        if not check("R4 terminal restarted", on is not None):
            return
        row = await conn.fetchrow("SELECT status,claimed_at,expires_at FROM macrofx_v2_commands WHERE command_id=$1", uuid.UUID(cid))
        valid_test = on > row["expires_at"]
        check("R5 restart happened after the command expired (valid test)", valid_test,
              f"restart {on} expires {row['expires_at']}")
        log("INFO watching 3 poll cycles after restart")
        await asyncio.sleep(190)
        row = await conn.fetchrow("SELECT status,claimed_at,result FROM macrofx_v2_commands WHERE command_id=$1", uuid.UUID(cid))
        if valid_test:
            check("R6 expired command never claimed after restart", row["status"] == "PENDING" and row["claimed_at"] is None,
                  f"{row['status']} claimed={row['claimed_at']}")
        else:
            log("INFO restart was before expiry, so EA was entitled to run it:", dict(row))
        _, after = await snapshot(conn)
        check("R7 positions unchanged across restart", after == before, after)
        await conn.execute("UPDATE macrofx_v2_commands SET status='CANCELLED',result='expired_unclaimed_restart_test' WHERE command_id=$1 AND status='PENDING'", uuid.UUID(cid))
        if not original:
            await conn.execute("DELETE FROM macrofx_v2_settings WHERE account_id=$1", REAL)
        s, t = req("GET", "/api/macrofx/v2/control-text", {"account_id": REAL}, EA)
        check("R8 remote control back to disabled", "ENABLED,0" in t, t.replace("\n", "|"))

        # ---------------- Phase N: network outage ----------------
        log("READY FOR STEP 2: disconnect the PC from the internet now (about 3 minutes), then reconnect")
        off = await wait_offline(conn, "network")
        if not check("N1 network outage detected", off is not None):
            return
        on = await wait_online(conn, off, "network")
        if not check("N2 EA reconnected on its own", on is not None):
            return
        log("INFO outage length", (on - off).total_seconds(), "s; watching 2 poll cycles")
        await asyncio.sleep(130)
        hb = await last_hb(conn)
        check("N3 heartbeats steady after reconnect", hb["age"].total_seconds() < 90, int(hb["age"].total_seconds()))
        snap_at, after = await snapshot(conn)
        check("N4 position snapshots resumed", (await conn.fetchval("SELECT NOW()") - snap_at).total_seconds() < 90)
        check("N5 positions unchanged across outage", after == before, after)
        n = await conn.fetchval("""SELECT COUNT(*) FROM macrofx_v2_commands WHERE account_id=$1
            AND created_at>$2 AND reason<>$3""", REAL, off, REASON)
        check("N6 no commands created or executed during/after outage", n == 0, n)
    finally:
        if original:
            await conn.execute("""UPDATE macrofx_v2_settings SET enabled=$2,pause_entries=$3,max_positions=$4,
                max_lot_per_pair=$5,max_spread_points=$6,slippage_points=$7,revision=revision+1,updated_at=NOW()
                WHERE account_id=$1""", REAL, original["enabled"], original["pause_entries"], original["max_positions"],
                original["max_lot_per_pair"], original["max_spread_points"], original["slippage_points"])
        else:
            await conn.execute("DELETE FROM macrofx_v2_settings WHERE account_id=$1", REAL)
        if cid:
            await conn.execute("UPDATE macrofx_v2_commands SET status='CANCELLED',result='cancelled_by_test_cleanup' WHERE command_id=$1 AND status='PENDING'", uuid.UUID(cid))
        s, t = req("GET", "/api/macrofx/v2/control-text", {"account_id": REAL}, EA)
        check("Z1 final: remote control disabled", s == 200 and "ENABLED,0" in t, s)
        await conn.close()
        log(f"SUMMARY restart_tests passed={sum(RESULTS)} failed={len(RESULTS)-sum(RESULTS)} total={len(RESULTS)}")


if __name__ == "__main__":
    asyncio.run(main())
    log("RUNNER DONE - idle")
    while True:
        time.sleep(3600)

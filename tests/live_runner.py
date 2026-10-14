"""Authenticated production verification runner for MacroFX Bridge v2.

Runs INSIDE Railway so credentials never leave the platform. Reads
EA_API_KEY, MACROFX_ADMIN_KEY and DATABASE_URL from the environment and never
prints them.

Safety:
- All write-path tests use a synthetic account (CLAUDE-TEST-<ts>), never the
  real broker account. No real EA can receive these commands.
- The real demo account (REAL_ACCOUNT, default 1041307) is only READ.
- No broker orders are possible from this runner.
- Synthetic rows are deleted at the end.
"""
import asyncio
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor

import asyncpg

BASE = os.environ.get("TARGET_URL", "https://mt5.freedomincomeoptions.com").rstrip("/")
EA_KEY = os.environ["EA_API_KEY"]
ADMIN_KEY = os.environ["MACROFX_ADMIN_KEY"]
DB = os.environ["DATABASE_URL"]
REAL = os.environ.get("REAL_ACCOUNT", "1041307")
ACC = "CLAUDE-TEST-" + str(int(time.time()))

RESULTS = []


def req(method, path, params=None, headers=None, body=None):
    url = BASE + path + ("?" + urllib.parse.urlencode(params) if params else "")
    data = None
    h = dict(headers or {})
    if body is not None:
        data = json.dumps(body).encode()
        h["Content-Type"] = "application/json"
    r = urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


EA = {"X-EA-API-Key": EA_KEY}
ADMIN = {"X-MacroFX-Admin-Key": ADMIN_KEY}


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail else ""), flush=True)


def hb(acc):
    return req("POST", "/api/macrofx/heartbeat", {"account_id": acc, "is_demo": "true",
               "ea_version": "claude-live-runner", "broker": "TEST"}, EA)


def settings(acc, **kw):
    return req("POST", "/api/macrofx/v2/admin/settings", headers=ADMIN, body={"account_id": acc, **kw})


def create(acc, action="PAUSE_ENTRIES", **kw):
    return req("POST", "/api/macrofx/v2/admin/commands", headers=ADMIN,
               body={"account_id": acc, "action": action, "reason": "claude live verification", **kw})


def control(acc):
    return req("GET", "/api/macrofx/v2/control-text", {"account_id": acc}, EA)


def claim(acc, cid):
    return req("POST", "/api/macrofx/v2/claim", {"account_id": acc, "command_id": cid}, EA)


def ack(acc, cid, status="ACKED", token=None, result="paused"):
    p = {"account_id": acc, "command_id": cid, "status": status, "result": result}
    if token is not None:
        p["claim_token"] = token
    return req("POST", "/api/macrofx/v2/ack", p, EA)


def cmds_in(text):
    return [l.split(",")[1] for l in text.splitlines() if l.startswith("COMMAND,")]


async def main():
    conn = await asyncpg.connect(DB)
    try:
        # ---------- Phase A ----------
        check("A1 db connectivity", await conn.fetchval("SELECT 1") == 1)
        control(REAL)  # first v2 request applies the v2 schema on a fresh process
        tables = {r["tablename"] for r in await conn.fetch("SELECT tablename FROM pg_tables WHERE schemaname='public'")}
        need = {"macrofx_heartbeats", "macrofx_v2_settings", "macrofx_v2_commands",
                "macrofx_v2_position_snapshots", "macrofx_weekly_runs", "macrofx_targets", "macrofx_fills"}
        check("A2 required tables present", need <= tables, ",".join(sorted(need - tables)))
        cols = {r["column_name"] for r in await conn.fetch(
            "SELECT column_name FROM information_schema.columns WHERE table_name='macrofx_v2_commands'")}
        check("A3 migration applied (claim_token column)", "claim_token" in cols)

        real_hb = await conn.fetchrow("""SELECT is_demo,ea_version,captured_at,NOW()-captured_at AS age
            FROM macrofx_heartbeats WHERE account_id=$1 ORDER BY captured_at DESC LIMIT 1""", REAL)
        check(f"A4 real account {REAL} latest heartbeat is demo and fresh",
              real_hb and real_hb["is_demo"] and real_hb["age"].total_seconds() < 600,
              real_hb and f"ea={real_hb['ea_version']} age={int(real_hb['age'].total_seconds())}s")
        real_settings = await conn.fetchrow("SELECT enabled,pause_entries,max_positions,max_lot_per_pair,revision FROM macrofx_v2_settings WHERE account_id=$1", REAL)
        print("INFO real account settings:", dict(real_settings) if real_settings else "none (defaults: disabled)")
        open_real = await conn.fetch("SELECT command_id,action,status,created_at FROM macrofx_v2_commands WHERE account_id=$1 AND status IN ('PENDING','CLAIMED')", REAL)
        print("INFO real account unresolved commands:", [dict(r) for r in open_real])

        s, _ = req("GET", "/api/macrofx/v2/admin/commands", {"account_id": REAL}, ADMIN)
        check("A5 admin key authenticates", s == 200, s)
        s, _ = req("GET", "/api/macrofx/v2/admin/commands", {"account_id": REAL}, {"X-MacroFX-Admin-Key": "bad"})
        check("A6 bad admin key rejected", s == 403, s)
        s, _ = req("GET", "/api/macrofx/v2/admin/commands", {"account_id": REAL}, {"X-MacroFX-Admin-Key": EA_KEY})
        check("A7 EA key not accepted as admin", s == 403, s)
        s, _ = control(REAL)
        check("A8 EA key authenticates (control-text, real account, read-only)", s == 200, s)
        s, _ = req("GET", "/api/macrofx/v2/control-text", {"account_id": REAL}, {"X-EA-API-Key": ADMIN_KEY})
        check("A9 admin key not accepted as EA key", s == 403, s)
        s, _ = req("POST", "/api/macrofx/heartbeat", {"account_id": ACC, "is_demo": "false"}, EA)
        check("A10 non-demo heartbeat rejected", s == 409, s)
        s, _ = create(ACC)
        check("A11 no heartbeat -> command creation blocked", s == 409, s)

        s, _ = hb(ACC)
        check("A12 synthetic demo heartbeat accepted", s == 200, s)
        s, t = control(ACC)
        check("A13 remote control defaults disabled", s == 200 and "ENABLED,0" in t and "MAX_POSITIONS,0" in t, t.replace("\n", "|"))

        # ---------- Phase B ----------
        s, b = create(ACC)
        cid0 = json.loads(b)["command_id"] if s == 200 else None
        check("B1 admin creates PAUSE_ENTRIES", s == 200, s)
        check("B2 not delivered while remote disabled", cid0 not in cmds_in(control(ACC)[1]))
        s, _ = claim(ACC, cid0)
        check("B3 claim rejected while remote disabled", s == 409, s)
        await conn.execute("UPDATE macrofx_v2_commands SET status='CANCELLED' WHERE command_id=$1", uuid.UUID(cid0))

        s, _ = settings(ACC, enabled=True, pause_entries=False)
        check("B4 enable remote control (synthetic account)", s == 200, s)
        s, b = create(ACC)
        cid = json.loads(b)["command_id"]
        t = control(ACC)[1]
        check("B5 command appears in EA queue when enabled", cid in cmds_in(t))
        check("B6 PAUSE command latched server pause", "PAUSE_ENTRIES,1" in t)
        s, b = claim(ACC, cid)
        token = json.loads(b).get("claim_token", "") if s == 200 else ""
        check("B7 atomic claim succeeds with token", s == 200 and len(token) == 32, s)
        s, _ = claim(ACC, cid)
        check("B8 duplicate claim rejected", s == 409, s)
        check("B9 claimed command not delivered again", cid not in cmds_in(control(ACC)[1]))
        s, _ = ack(ACC, cid, status="DONE", token=token)
        check("B10 invalid ack status rejected", s == 422, s)
        s, _ = ack(ACC, cid)
        check("B11 ack without token rejected (v2.01-style second chart)", s == 409, s)
        s, _ = ack(ACC, cid, token="0" * 32)
        check("B12 ack with wrong token rejected (second chart cannot overwrite)", s == 409, s)
        s, _ = ack(ACC, cid, token=token)
        check("B13 ack by claimant succeeds", s == 200, s)
        s, _ = ack(ACC, cid, token=token, status="FAILED")
        check("B14 second ack rejected", s == 409, s)
        s, b = req("GET", "/api/macrofx/v2/admin/commands", {"account_id": ACC}, ADMIN)
        row = next((r for r in json.loads(b) if r["command_id"] == cid), {})
        check("B15 history records ACKED with timestamps", row.get("status") == "ACKED" and row.get("claimed_at") and row.get("acknowledged_at"))
        check("B16 history never exposes claim_token", "claim_token" not in row)

        s, b = create(ACC)
        cexp = json.loads(b)["command_id"]
        await conn.execute("UPDATE macrofx_v2_commands SET expires_at=NOW()-INTERVAL '1 second' WHERE command_id=$1", uuid.UUID(cexp))
        check("B17 expired command not delivered", cexp not in cmds_in(control(ACC)[1]))
        check("B18 expired command not claimable", claim(ACC, cexp)[0] == 409)

        s, b = create(ACC)
        cc = json.loads(b)["command_id"]
        with ThreadPoolExecutor(10) as ex:
            codes = list(ex.map(lambda _: claim(ACC, cc)[0], range(10)))
        check("B19 10 concurrent claims -> exactly one winner", codes.count(200) == 1 and codes.count(409) == 9, codes)
        s, _ = claim(ACC + "X", cc)
        check("B20 other account cannot claim", s in (409,), s)
        await conn.execute("UPDATE macrofx_v2_commands SET status='CANCELLED' WHERE command_id=$1", uuid.UUID(cc))

        # ---------- Phase C (server-side controls) ----------
        check("C1 max lot >0.01 rejected", settings(ACC, max_lot_per_pair=0.02)[0] == 422)
        check("C2 max positions >2 rejected", settings(ACC, max_positions=3)[0] == 422)
        check("C3 unsupported action rejected", create(ACC, action="DELETE_ALL")[0] == 422)
        check("C4 open with 0.02 lots rejected", create(ACC, action="OPEN_LONG", symbol="EURUSD", lots=0.02)[0] == 422)
        check("C5 invalid symbol rejected", create(ACC, action="OPEN_LONG", symbol="EUR/USD", lots=0.01)[0] == 422)
        # Synthetic account only; no real EA polls this account id.
        s1, b1 = create(ACC, action="OPEN_LONG", symbol="EURUSD", lots=0.01)
        s2, _ = create(ACC, action="OPEN_SHORT", symbol="EURUSD", lots=0.01)
        check("C6 duplicate pending open for same pair rejected", s1 == 200 and s2 == 409, (s1, s2))
        await conn.execute("UPDATE macrofx_v2_commands SET status='CANCELLED' WHERE account_id=$1 AND status IN ('PENDING','CLAIMED')", ACC)
        await conn.execute("UPDATE macrofx_heartbeats SET captured_at=NOW()-INTERVAL '11 minutes' WHERE account_id=$1", ACC)
        check("C7 stale heartbeat blocks command creation", create(ACC)[0] == 409)
        check("C8 stale heartbeat blocks EA polling", control(ACC)[0] == 409)

        # ---------- Phase E (read-only, real account) ----------
        s, b = req("GET", "/api/macrofx/v2/admin/reconcile-preview", {"account_id": REAL}, ADMIN)
        before = await conn.fetchval("SELECT COUNT(*) FROM macrofx_v2_commands WHERE account_id=$1", REAL)
        print("INFO reconcile-preview real account HTTP", s, b[:1500])
        after = await conn.fetchval("SELECT COUNT(*) FROM macrofx_v2_commands WHERE account_id=$1", REAL)
        check("E1 reconcile preview responds (200, or 409 with explicit reason)", s in (200, 409), s)
        check("E2 reconcile preview created no commands", before == after)
    finally:
        # Remove all synthetic rows so production history stays clean.
        for acc in (ACC, ACC + "X"):
            await conn.execute("DELETE FROM macrofx_v2_commands WHERE account_id=$1", acc)
            await conn.execute("DELETE FROM macrofx_v2_settings WHERE account_id=$1", acc)
            await conn.execute("DELETE FROM macrofx_heartbeats WHERE account_id=$1", acc)
        for tbl in ("macrofx_daily_equity",):
            try:
                await conn.execute(f"DELETE FROM {tbl} WHERE account_id=$1", ACC)
            except Exception:
                pass
        left = await conn.fetchval("SELECT COUNT(*) FROM macrofx_v2_commands WHERE account_id LIKE 'CLAUDE-TEST-%'")
        print("INFO synthetic rows remaining:", left)
        await conn.close()

    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"SUMMARY account={ACC} passed={passed} failed={len(RESULTS) - passed} total={len(RESULTS)}", flush=True)
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    code = asyncio.run(main())
    # Keep the container idle so the run is not restarted and repeated.
    if os.environ.get("RUNNER_SLEEP_AFTER", "1") == "1":
        print("RUNNER DONE - idle", flush=True)
        while True:
            time.sleep(3600)
    sys.exit(code)

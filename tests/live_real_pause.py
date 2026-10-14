"""Real-terminal PAUSE_ENTRIES lifecycle test for the demo account.

Runs inside Railway (keys never leave it). Safe by construction:
- Settings are enabled with pause_entries=TRUE for the whole test, so no
  entries are possible even if EnableTrading is ON in the EA.
- Only a PAUSE_ENTRIES command is created. No OPEN/CLOSE commands.
- Original settings are restored at the end (row deleted if none existed).
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
WAIT = int(os.environ.get("WAIT_SECONDS", "240"))
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


def check(name, ok, detail=""):
    RESULTS.append(bool(ok))
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail else ""), flush=True)


async def main():
    conn = await asyncpg.connect(DB)
    original = await conn.fetchrow("SELECT * FROM macrofx_v2_settings WHERE account_id=$1", REAL)
    print("INFO original settings:", dict(original) if original else "none", flush=True)
    cid = None
    try:
        hb = await conn.fetchrow("""SELECT is_demo,ea_version,NOW()-captured_at AS age FROM macrofx_heartbeats
            WHERE account_id=$1 ORDER BY captured_at DESC LIMIT 1""", REAL)
        ok = hb and hb["is_demo"] and hb["age"].total_seconds() < 180 and "2.02" in (hb["ea_version"] or "")
        check("R1 real account demo, fresh, EA v2.02", ok, hb and f"{hb['ea_version']} age={int(hb['age'].total_seconds())}s")
        if not ok:
            return 1
        unresolved = await conn.fetchval("SELECT COUNT(*) FROM macrofx_v2_commands WHERE account_id=$1 AND status IN ('PENDING','CLAIMED')", REAL)
        check("R2 no unresolved commands before test", unresolved == 0, unresolved)
        if unresolved:
            return 1

        s, b = req("POST", "/api/macrofx/v2/admin/settings", headers=ADMIN, body={
            "account_id": REAL, "enabled": True, "pause_entries": True,
            "max_positions": 2, "max_lot_per_pair": 0.01, "max_spread_points": 300, "slippage_points": 30})
        check("R3 remote control enabled with entries PAUSED", s == 200, s)

        s, b = req("POST", "/api/macrofx/v2/admin/commands", headers=ADMIN, body={
            "account_id": REAL, "action": "PAUSE_ENTRIES", "reason": "Claude real-terminal lifecycle test (v2.02)"})
        check("R4 PAUSE_ENTRIES created", s == 200, s)
        cid = json.loads(b)["command_id"]
        print("INFO command_id", cid, "created", time.strftime("%H:%M:%SZ", time.gmtime()), flush=True)

        row = None
        deadline = time.time() + WAIT
        while time.time() < deadline:
            row = await conn.fetchrow("SELECT * FROM macrofx_v2_commands WHERE command_id=$1", uuid.UUID(cid))
            if row["status"] in ("ACKED", "FAILED"):
                break
            await asyncio.sleep(3)
        print("INFO final row:", {k: (str(v) if v is not None else None) for k, v in dict(row).items() if k != "claim_token"}, flush=True)
        check("R5 EA received and claimed it", row["claimed_at"] is not None, row["status"])
        check("R6 EA acknowledged it with the claim token", row["status"] == "ACKED", f"{row['status']} result={row['result']}")
        check("R7 EA result is 'paused'", row["result"] == "paused", row["result"])
        if row["claimed_at"] and row["acknowledged_at"]:
            print("INFO latency create->claim", (row["claimed_at"] - row["created_at"]).total_seconds(),
                  "s; claim->ack", (row["acknowledged_at"] - row["claimed_at"]).total_seconds(), "s", flush=True)

        s, t = req("GET", "/api/macrofx/v2/control-text", {"account_id": REAL}, EA)
        check("R8 command not delivered again", cid not in t, s)
        s, _ = req("POST", "/api/macrofx/v2/claim", {"account_id": REAL, "command_id": cid}, EA)
        check("R9 duplicate claim rejected", s == 409, s)
        s, _ = req("POST", "/api/macrofx/v2/ack", {"account_id": REAL, "command_id": cid, "status": "FAILED",
                   "claim_token": "0" * 32, "result": "overwrite-attempt"}, EA)
        check("R10 foreign ack cannot overwrite result", s == 409, s)
        final = await conn.fetchrow("SELECT status,result FROM macrofx_v2_commands WHERE command_id=$1", uuid.UUID(cid))
        check("R11 stored result unchanged", final["status"] == "ACKED" and final["result"] == "paused", dict(final))
    finally:
        # Restore the original settings exactly.
        if original:
            await conn.execute("""UPDATE macrofx_v2_settings SET enabled=$2,pause_entries=$3,max_positions=$4,
                max_lot_per_pair=$5,max_spread_points=$6,slippage_points=$7,revision=revision+1,updated_at=NOW()
                WHERE account_id=$1""", REAL, original["enabled"], original["pause_entries"], original["max_positions"],
                original["max_lot_per_pair"], original["max_spread_points"], original["slippage_points"])
        else:
            await conn.execute("DELETE FROM macrofx_v2_settings WHERE account_id=$1", REAL)
        if cid:
            await conn.execute("UPDATE macrofx_v2_commands SET status='CANCELLED',result=COALESCE(result,'cancelled_by_test_cleanup') WHERE command_id=$1 AND status='PENDING'", uuid.UUID(cid))
        s, t = req("GET", "/api/macrofx/v2/control-text", {"account_id": REAL}, EA)
        check("R12 settings restored (remote control disabled)", s == 200 and "ENABLED,0" in t, t.replace("\n", "|"))
        unresolved = await conn.fetchval("SELECT COUNT(*) FROM macrofx_v2_commands WHERE account_id=$1 AND status IN ('PENDING','CLAIMED')", REAL)
        check("R13 no unresolved commands after test", unresolved == 0, unresolved)
        await conn.close()
    print(f"SUMMARY real_pause passed={sum(RESULTS)} failed={len(RESULTS)-sum(RESULTS)} total={len(RESULTS)}", flush=True)
    return 0


if __name__ == "__main__":
    asyncio.run(main())
    print("RUNNER DONE - idle", flush=True)
    while True:
        time.sleep(3600)

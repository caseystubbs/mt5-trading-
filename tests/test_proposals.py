"""Weekly plan -> approval -> execution, against a simulated EA.

The executor runs in-process (executor_tick) against the isolated test DB; the
"EA" polls, claims, posts fills/positions and acks through the real HTTP API.
"""
import asyncio
import itertools
import json
import uuid
from datetime import datetime, timedelta, timezone

import pytest

import macrofx
import macrofx_proposals as mp
from conftest import ADMIN, EA, sql

_week = itertools.count(1)
_ticket = itertools.count(5000000)


# ---------------------------------------------------------------- helpers
def tick(account, now=None):
    async def run():
        macrofx._macro_pool = None
        pool = await macrofx.get_pool()
        try:
            await mp.executor_tick(pool, now=now or datetime.now(timezone.utc), account=account)
        finally:
            await pool.close()
            macrofx._macro_pool = None
    asyncio.run(run())


@pytest.fixture
def window_open(monkeypatch):
    monkeypatch.setattr(mp, "in_window", lambda t: True)


def hb(api, account):
    r = api.post("/api/macrofx/heartbeat", headers=EA, params={
        "account_id": account, "is_demo": "true", "ea_version": "MacroFX-MT4-Bridge-2.02-claimtoken",
        "balance": 1000, "equity": 1000})
    assert r.status_code == 200


class FakeEA:
    """Minimal MT4 EA: positions, poll/claim/execute/fill/ack."""

    def __init__(self, api, account, positions):
        self.api, self.account = api, account
        self.positions = {p["ticket"]: dict(p) for p in positions}
        self.mode = "normal"   # normal | spread_block | claim_only
        self.upload()

    def upload(self):
        body = "".join(f"{p['symbol']}.m,{t},{'SELL' if p['direction']=='SHORT' else 'BUY'},0.01,1,1,0,0,0,{p.get('magic', 26092601)}\n"
                       for t, p in self.positions.items())
        r = self.api.post("/api/macrofx/positions-csv", headers={**EA, "Content-Type": "text/plain"},
                          params={"account_id": self.account}, content=body)
        assert r.status_code == 200

    def poll(self):
        hb(self.api, self.account)
        self.upload()
        text = self.api.get("/api/macrofx/v2/control-text", headers=EA, params={"account_id": self.account}).text
        for line in text.splitlines():
            if not line.startswith("COMMAND,"):
                continue
            _, cid, action, symbol, ticket, lots = line.split(",")
            r = self.api.post("/api/macrofx/v2/claim", headers=EA, params={"account_id": self.account, "command_id": cid})
            if r.status_code != 200:
                continue
            token = r.json()["claim_token"]
            if self.mode == "claim_only":
                continue
            paused = "PAUSE_ENTRIES,1" in text
            if action == "CLOSE_TICKET":
                t = int(ticket)
                if t not in self.positions:
                    status, result = "FAILED", "ticket_not_owned_or_closed"
                else:
                    p = self.positions.pop(t)
                    self.fill(p["symbol"], "CLOSE", t)
                    status, result = "ACKED", "closed"
            else:
                if paused:
                    status, result = "FAILED", "entries_paused"
                elif self.mode == "spread_block":
                    status, result = "FAILED", "spread_or_quote_block"
                elif any(p["symbol"] == symbol for p in self.positions.values()):
                    status, result = "FAILED", "pair_already_open"
                elif len(self.positions) >= 2:
                    status, result = "FAILED", "position_limit"
                else:
                    t = next(_ticket)
                    self.positions[t] = {"symbol": symbol, "direction": "LONG" if action == "OPEN_LONG" else "SHORT"}
                    self.fill(symbol, action, t)
                    status, result = "ACKED", f"opened_ticket_{t}"
            self.upload()
            self.api.post("/api/macrofx/v2/ack", headers=EA, params={"account_id": self.account, "command_id": cid,
                          "status": status, "result": result, "claim_token": token})

    def fill(self, symbol, action, ticket):
        self.api.post("/api/macrofx/fill", headers=EA, params={
            "account_id": self.account, "symbol": symbol, "action": action, "lots": 0.01, "ticket": ticket,
            "fill_price": 1.0, "spread_points": 8, "notes": "remote_command",
            "exit_reason": "remote_command" if action == "CLOSE" else ""})

    def held(self):
        return sorted((p["symbol"], p["direction"]) for p in self.positions.values())


def new_run(targets, created=None):
    """Insert a weekly run that is the latest by week_ending."""
    n = next(_week)
    week = datetime(3000, 1, 1).date() + timedelta(days=7 * n)
    created = created or datetime(2026, 10, 17, 1, 0, tzinfo=timezone.utc)  # Fri 9 PM ET
    rid = sql("""INSERT INTO macrofx_weekly_runs(week_ending,created_at,strategy_version,snapshot_json,targets_json,report_markdown)
                 VALUES($1,$2,'macrofx-v1.1','[]',$3::jsonb,'') RETURNING id""", week, created, json.dumps(targets), fetch=True)[0]["id"]
    for t in targets:
        sql("""INSERT INTO macrofx_targets(weekly_run_id,expires_at,symbol,direction,lots,score)
               VALUES($1,NOW()+INTERVAL '7 days',$2,$3,0.01,$4)""", rid, t["symbol"], t["direction"], t["score"])
    return rid


def plans(account):
    return sql("SELECT * FROM macrofx_v2_proposals WHERE account_id=$1 ORDER BY id DESC", account, fetch=True)


def latest(account):
    p = plans(account)[0]
    p["steps"] = json.loads(p["steps_json"]) if isinstance(p["steps_json"], str) else p["steps_json"]
    return p


def drive(api, ea, account, rounds=20):
    """Alternate executor ticks and EA polls until the plan is terminal."""
    for _ in range(rounds):
        tick(account)
        ea.poll()
        if latest(account)["status"] not in ("APPROVED", "EXECUTING"):
            break
        sql("UPDATE macrofx_v2_proposals SET next_attempt_at=NULL WHERE account_id=$1 AND next_attempt_at IS NOT NULL "
            "AND status='EXECUTING' AND NOT (steps_json::text LIKE '%spread_tries%')", account)
    return latest(account)


def approve_now(api, pid):
    """Approve, then make it due now. (The server's real window may be closed when tests run,
    e.g. after 4 PM ET; window behaviour itself is covered by test_window_and_schedule.)"""
    r = api.post(f"/api/macrofx/v2/admin/proposals/{pid}/approve", headers=ADMIN, params={"run_now": "true"})
    assert r.status_code == 200, r.text
    sql("UPDATE macrofx_v2_proposals SET execute_after=NOW()-INTERVAL '1 minute' WHERE id=$1", pid)
    return r


ROTATE = [{"symbol": "EURUSD", "direction": "SHORT", "score": -1.78}, {"symbol": "AUDCHF", "direction": "LONG", "score": 1.63}]
HELD = [{"ticket": 111, "symbol": "EURAUD", "direction": "SHORT"}, {"ticket": 222, "symbol": "NZDUSD", "direction": "SHORT"}]


# ---------------------------------------------------------------- pure functions
def test_window_and_schedule():
    et = mp.ET
    fri_9pm = datetime(2026, 10, 16, 21, 0, tzinfo=et)
    mon_4am = datetime(2026, 10, 19, 4, 0, tzinfo=et)
    assert mp.default_execute_after(fri_9pm.astimezone(timezone.utc)) == mon_4am.astimezone(timezone.utc)
    assert not mp.in_window(datetime(2026, 10, 18, 17, 30, tzinfo=et))   # Sunday reopen
    assert not mp.in_window(datetime(2026, 10, 19, 3, 59, tzinfo=et))
    assert mp.in_window(datetime(2026, 10, 19, 4, 0, tzinfo=et))
    assert not mp.in_window(datetime(2026, 10, 19, 16, 0, tzinfo=et))
    assert mp.next_window_start(datetime(2026, 10, 16, 18, 0, tzinfo=et)) == mon_4am.astimezone(timezone.utc)
    # DST: first Monday after US clocks change is still 04:00 ET
    assert mp.default_execute_after(datetime(2026, 10, 31, 1, 0, tzinfo=timezone.utc)).astimezone(et).hour == 4


def test_build_steps_closes_first_and_respects_cap():
    pos = [{"symbol": "EURAUD", "direction": "SHORT", "ticket": 1, "lots": .01},
           {"symbol": "NZDUSD", "direction": "SHORT", "ticket": 2, "lots": .01}]
    steps, holds = mp.build_steps(pos, [{"symbol": "EURAUD", "direction": "SHORT", "score": -1.8},
                                        {"symbol": "EURUSD", "direction": "SHORT", "score": -1.7}])
    assert [(s["kind"], s["symbol"]) for s in steps] == [("CLOSE", "NZDUSD"), ("OPEN", "EURUSD")]
    assert holds == [{"symbol": "EURAUD", "direction": "SHORT", "ticket": 1}]
    flip, _ = mp.build_steps([{"symbol": "EURAUD", "direction": "LONG", "ticket": 1, "lots": .01}],
                             [{"symbol": "EURAUD", "direction": "SHORT", "score": -1.8}])
    assert [(s["kind"], s["reason"]) for s in flip] == [("CLOSE", "direction flipped"), ("OPEN", "new target")]
    none, _ = mp.build_steps(pos, [{"symbol": "EURAUD", "direction": "SHORT"}, {"symbol": "NZDUSD", "direction": "SHORT"}])
    assert none == []


# ---------------------------------------------------------------- end to end
def test_full_weekly_rotation_with_approval(api, account, window_open):
    hb(api, account)
    ea = FakeEA(api, account, HELD)
    new_run(ROTATE)
    tick(account)
    p = latest(account)
    assert p["status"] == "PROPOSED"
    assert [(s["kind"], s["symbol"]) for s in p["steps"]] == [
        ("CLOSE", "EURAUD"), ("CLOSE", "NZDUSD"), ("OPEN", "EURUSD"), ("OPEN", "AUDCHF")]
    assert p["execute_after"].astimezone(mp.ET).strftime("%a %H:%M") == "Mon 04:00"

    # Nothing happens without approval
    tick(account); ea.poll()
    assert ea.held() == [("EURAUD", "SHORT"), ("NZDUSD", "SHORT")]
    assert sql("SELECT COUNT(*) n FROM macrofx_v2_commands WHERE account_id=$1", account, fetch=True)[0]["n"] == 0

    # Approval needs the admin key
    assert api.post(f"/api/macrofx/v2/admin/proposals/{p['id']}/approve").status_code == 403
    assert api.post(f"/api/macrofx/v2/admin/proposals/{p['id']}/approve", headers={"X-MacroFX-Admin-Key": "x"}).status_code == 403
    r = api.post(f"/api/macrofx/v2/admin/proposals/{p['id']}/approve", headers=ADMIN, params={"run_now": "true"})
    assert r.status_code == 200 and r.json()["status"] == "APPROVED"
    sql("UPDATE macrofx_v2_proposals SET execute_after=NOW()-INTERVAL '1 minute' WHERE id=$1", p["id"])
    assert api.post(f"/api/macrofx/v2/admin/proposals/{p['id']}/approve", headers=ADMIN).status_code == 409

    p = drive(api, ea, account)
    assert p["status"] == "DONE", p["log_json"]
    assert [s["status"] for s in p["steps"]] == ["DONE"] * 4
    assert ea.held() == [("AUDCHF", "LONG"), ("EURUSD", "SHORT")]
    # Remote control is off again
    assert "ENABLED,0" in api.get("/api/macrofx/v2/control-text", headers=EA, params={"account_id": account}).text
    # Fills are labelled as model trades with score and version
    fills = sql("""SELECT symbol,action,notes,exit_reason,signal_score,strategy_version FROM macrofx_fills
                   WHERE account_id=$1 ORDER BY captured_at""", account, fetch=True)
    closes = [f for f in fills if f["action"] == "CLOSE"]
    opens = [f for f in fills if f["action"].startswith("OPEN")]
    assert all(f["exit_reason"] == "target_removed" and f["notes"] == "target_removed" for f in closes)
    assert all(f["notes"] == "target_open" and f["strategy_version"] == "macrofx-v1.1" for f in opens)
    assert sorted(round(f["signal_score"], 2) for f in opens) == [-1.78, 1.63]
    # Every command went through the normal claim path, closes before opens
    cmds = sql("SELECT action,status FROM macrofx_v2_commands WHERE account_id=$1 ORDER BY created_at", account, fetch=True)
    assert [c["action"] for c in cmds] == ["CLOSE_TICKET", "CLOSE_TICKET", "OPEN_SHORT", "OPEN_LONG"]
    assert all(c["status"] == "ACKED" for c in cmds)


def test_no_changes_when_positions_match(api, account, window_open):
    hb(api, account)
    FakeEA(api, account, HELD)
    new_run([{"symbol": "EURAUD", "direction": "SHORT", "score": -1.8}, {"symbol": "NZDUSD", "direction": "SHORT", "score": -1.5}])
    tick(account)
    assert latest(account)["status"] == "NO_CHANGES"


def test_approved_plan_waits_outside_window(api, account, monkeypatch):
    monkeypatch.setattr(mp, "in_window", lambda t: False)
    hb(api, account)
    ea = FakeEA(api, account, HELD)
    new_run(ROTATE)
    tick(account)
    p = latest(account)
    approve_now(api, p["id"])
    sql("UPDATE macrofx_v2_proposals SET execute_after=NOW()-INTERVAL '1 minute' WHERE id=$1", p["id"])
    tick(account); ea.poll(); tick(account)
    p = latest(account)
    assert p["status"] == "EXECUTING" and p["next_attempt_at"] is not None
    assert sql("SELECT COUNT(*) n FROM macrofx_v2_commands WHERE account_id=$1", account, fetch=True)[0]["n"] == 0
    assert ea.held() == [("EURAUD", "SHORT"), ("NZDUSD", "SHORT")]


def test_not_before_execute_after(api, account, window_open):
    hb(api, account)
    ea = FakeEA(api, account, HELD)
    new_run(ROTATE, created=datetime.now(timezone.utc) - timedelta(hours=1))
    tick(account)
    p = latest(account)
    api.post(f"/api/macrofx/v2/admin/proposals/{p['id']}/approve", headers=ADMIN)  # keeps scheduled time
    sql("UPDATE macrofx_v2_proposals SET execute_after=NOW()+INTERVAL '2 days' WHERE id=$1", p["id"])
    tick(account); ea.poll()
    assert latest(account)["status"] == "APPROVED"
    assert ea.held() == [("EURAUD", "SHORT"), ("NZDUSD", "SHORT")]


def test_spread_block_retries_hourly_not_immediately(api, account, window_open):
    hb(api, account)
    ea = FakeEA(api, account, [{"ticket": 333, "symbol": "EURAUD", "direction": "SHORT"}])
    new_run([{"symbol": "EURAUD", "direction": "SHORT", "score": -1.8}, {"symbol": "EURUSD", "direction": "SHORT", "score": -1.7}])
    tick(account)
    p = latest(account)
    assert [(s["kind"], s["symbol"]) for s in p["steps"]] == [("OPEN", "EURUSD")]
    approve_now(api, p["id"])
    ea.mode = "spread_block"
    tick(account); ea.poll(); tick(account)
    p = latest(account)
    assert p["steps"][0]["status"] == "RETRY" and p["steps"][0]["spread_tries"] == 1
    assert p["next_attempt_at"] > datetime.now(timezone.utc) + timedelta(minutes=50)
    before = sql("SELECT COUNT(*) n FROM macrofx_v2_commands WHERE account_id=$1", account, fetch=True)[0]["n"]
    tick(account); tick(account)
    assert sql("SELECT COUNT(*) n FROM macrofx_v2_commands WHERE account_id=$1", account, fetch=True)[0]["n"] == before
    # An hour later the spread is normal and it goes through
    ea.mode = "normal"
    sql("UPDATE macrofx_v2_proposals SET next_attempt_at=NOW()-INTERVAL '1 second' WHERE id=$1", p["id"])
    p = drive(api, ea, account)
    assert p["status"] == "DONE" and ea.held() == [("EURAUD", "SHORT"), ("EURUSD", "SHORT")]
    assert "ENABLED,0" in api.get("/api/macrofx/v2/control-text", headers=EA, params={"account_id": account}).text


def test_claimed_but_unacked_stops_for_review_and_never_retries(api, account, window_open):
    hb(api, account)
    ea = FakeEA(api, account, HELD)
    new_run(ROTATE)
    tick(account)
    p = latest(account)
    approve_now(api, p["id"])
    ea.mode = "claim_only"
    tick(account); ea.poll()
    sql("UPDATE macrofx_v2_commands SET claimed_at=NOW()-INTERVAL '4 minutes' WHERE account_id=$1 AND status='CLAIMED'", account)
    tick(account)
    p = latest(account)
    assert p["status"] == "NEEDS_REVIEW"
    assert p["steps"][0]["status"] == "UNCERTAIN"
    n = sql("SELECT COUNT(*) n FROM macrofx_v2_commands WHERE account_id=$1", account, fetch=True)[0]["n"]
    tick(account); tick(account)
    assert sql("SELECT COUNT(*) n FROM macrofx_v2_commands WHERE account_id=$1", account, fetch=True)[0]["n"] == n == 1
    assert "ENABLED,0" in api.get("/api/macrofx/v2/control-text", headers=EA, params={"account_id": account}).text


def test_manual_close_is_respected(api, account, window_open):
    hb(api, account)
    ea = FakeEA(api, account, HELD)
    new_run([{"symbol": "EURAUD", "direction": "SHORT", "score": -1.8}, {"symbol": "EURUSD", "direction": "SHORT", "score": -1.7}])
    tick(account)
    p = latest(account)
    assert [(s["kind"], s["symbol"]) for s in p["steps"]] == [("CLOSE", "NZDUSD"), ("OPEN", "EURUSD")]
    # Operator closes NZDUSD and EURAUD by hand before Monday
    ea.positions = {}
    ea.upload()
    approve_now(api, p["id"])
    p = drive(api, ea, account)
    assert p["status"] == "DONE"
    assert p["steps"][0]["status"] == "SKIPPED" and p["steps"][0]["result"] == "already closed"
    # EURAUD (closed by hand, still a target) is NOT reopened; only the planned open runs
    assert ea.held() == [("EURUSD", "SHORT")]


def test_reject_and_cancel(api, account, window_open):
    hb(api, account)
    ea = FakeEA(api, account, HELD)
    new_run(ROTATE)
    tick(account)
    p = latest(account)
    assert api.post(f"/api/macrofx/v2/admin/proposals/{p['id']}/reject", headers=ADMIN).json()["status"] == "REJECTED"
    tick(account); ea.poll()
    assert ea.held() == [("EURAUD", "SHORT"), ("NZDUSD", "SHORT")]
    # Regenerate, approve, then cancel while the first command is waiting for the EA
    assert api.post("/api/macrofx/v2/admin/proposals/regenerate", headers=ADMIN).status_code in (200, 409)
    sql("UPDATE macrofx_v2_proposals SET status='SUPERSEDED' WHERE account_id=$1", account)
    new_run(ROTATE)
    tick(account)
    p = latest(account)
    approve_now(api, p["id"])
    tick(account)
    assert latest(account)["steps"][0]["status"] == "SENT"
    r = api.post(f"/api/macrofx/v2/admin/proposals/{p['id']}/cancel", headers=ADMIN)
    assert r.status_code == 200 and r.json()["status"] == "CANCELLED"
    ea.poll()
    assert ea.held() == [("EURAUD", "SHORT"), ("NZDUSD", "SHORT")]
    assert sql("SELECT status FROM macrofx_v2_commands WHERE account_id=$1", account, fetch=True)[0]["status"] == "CANCELLED"


def test_stale_ea_blocks_execution(api, account, window_open):
    hb(api, account)
    ea = FakeEA(api, account, HELD)
    new_run(ROTATE)
    tick(account)
    p = latest(account)
    approve_now(api, p["id"])
    sql("UPDATE macrofx_heartbeats SET captured_at=NOW()-INTERVAL '5 minutes' WHERE account_id=$1", account)
    tick(account)
    assert sql("SELECT COUNT(*) n FROM macrofx_v2_commands WHERE account_id=$1", account, fetch=True)[0]["n"] == 0
    assert "EA offline" in json.dumps(latest(account)["log_json"])


def test_proposals_endpoint_is_public_and_clean(api):
    r = api.get("/api/macrofx/v2/proposals")
    assert r.status_code == 200 and "claim_token" not in r.text

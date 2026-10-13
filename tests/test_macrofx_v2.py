"""MacroFX Bridge v2 backend tests (isolated DB, no broker access)."""
import concurrent.futures as cf
import json
import uuid

import httpx

from conftest import (ADMIN, ADMIN_KEY, EA, EA_KEY, ack, claim, control, create,
                      enable, heartbeat, sql)


def command_ids(text):
    return [l.split(",")[1] for l in text.splitlines() if l.startswith("COMMAND,")]


def ready(api, account, pause=True):
    assert heartbeat(api, account).status_code == 200
    assert enable(api, account, pause=pause).status_code == 200


# ---------- Authentication ----------

def test_admin_rejects_missing_and_wrong_key(api, account):
    heartbeat(api, account)
    body = {"account_id": account, "enabled": False}
    assert api.post("/api/macrofx/v2/admin/settings", json=body).status_code == 403
    assert api.post("/api/macrofx/v2/admin/settings", json=body,
                    headers={"X-MacroFX-Admin-Key": "wrong"}).status_code == 403
    assert api.post("/api/macrofx/v2/admin/settings", json=body, headers=ADMIN).status_code == 200


def test_admin_and_ea_keys_are_not_interchangeable(api, account):
    heartbeat(api, account)
    assert api.post("/api/macrofx/v2/admin/settings", json={"account_id": account},
                    headers={"X-MacroFX-Admin-Key": EA_KEY}).status_code == 403
    assert api.get("/api/macrofx/v2/control-text", params={"account_id": account},
                   headers={"X-EA-API-Key": ADMIN_KEY}).status_code == 403
    assert api.get("/api/macrofx/v2/admin/commands", params={"account_id": account},
                   headers={"X-MacroFX-Admin-Key": EA_KEY}).status_code == 403


def test_ea_endpoints_reject_bad_key(api, account):
    heartbeat(api, account)
    bad = {"X-EA-API-Key": "nope"}
    cid = str(uuid.uuid4())
    assert api.get("/api/macrofx/v2/control-text", params={"account_id": account}, headers=bad).status_code == 403
    assert api.post("/api/macrofx/v2/claim", params={"account_id": account, "command_id": cid}, headers=bad).status_code == 403
    assert api.post("/api/macrofx/v2/ack", params={"account_id": account, "command_id": cid, "status": "ACKED"}, headers=bad).status_code == 403
    assert api.post("/api/macrofx/heartbeat", params={"account_id": account}, headers=bad).status_code == 403


# ---------- Demo-only and heartbeat freshness ----------

def test_live_heartbeat_rejected(api, account):
    assert heartbeat(api, account, is_demo=False).status_code == 409


def test_no_heartbeat_blocks_everything(api, account):
    assert enable(api, account).status_code == 409
    assert create(api, account).status_code == 409
    assert control(api, account).status_code == 409


def test_stale_heartbeat_blocks_command_operations(api, account):
    ready(api, account)
    cid = create(api, account).json()["command_id"]
    sql("UPDATE macrofx_heartbeats SET captured_at=NOW()-INTERVAL '11 minutes' WHERE account_id=$1", account)
    assert create(api, account).status_code == 409
    assert control(api, account).status_code == 409
    assert claim(api, account, cid).status_code == 409


def test_non_demo_latest_heartbeat_blocks(api, account):
    ready(api, account)
    sql("INSERT INTO macrofx_heartbeats(account_id,is_demo) VALUES($1,FALSE)", account)
    assert create(api, account).status_code == 409


# ---------- Defaults and settings validation ----------

def test_remote_control_defaults_disabled(api, account):
    heartbeat(api, account)
    text = control(api, account).text
    assert "ENABLED,0" in text and "PAUSE_ENTRIES,1" in text and "MAX_POSITIONS,0" in text
    assert create(api, account).status_code == 200
    assert command_ids(control(api, account).text) == []  # never delivered while disabled


def test_settings_cannot_exceed_hard_limits(api, account):
    heartbeat(api, account)
    for bad in ({"max_lot_per_pair": 0.02}, {"max_positions": 3},
                {"slippage_points": 101}, {"max_spread_points": 5000}):
        assert enable(api, account, **bad).status_code == 422, bad


# ---------- Command validation ----------

def test_invalid_commands_rejected(api, account):
    ready(api, account)
    assert create(api, account, action="DELETE_ALL").status_code == 422
    assert create(api, account, action="CLOSE_TICKET").status_code == 422
    assert create(api, account, action="OPEN_LONG", symbol="EURUSD", lots=0.02).status_code == 422
    assert create(api, account, action="OPEN_LONG", symbol="EUR/USD", lots=0.01).status_code == 422
    assert create(api, account, action="OPEN_LONG", symbol="", lots=0.01).status_code == 422


def test_duplicate_pending_open_rejected(api, account):
    ready(api, account)
    assert create(api, account, action="OPEN_LONG", symbol="EURUSD", lots=0.01).status_code == 200
    assert create(api, account, action="OPEN_SHORT", symbol="eurusd", lots=0.01).status_code == 409


# ---------- Command lifecycle ----------

def test_full_pause_lifecycle(api, account):
    ready(api, account, pause=False)
    r = create(api, account)
    assert r.status_code == 200
    cid = r.json()["command_id"]
    assert command_ids(control(api, account).text) == [cid]
    c = claim(api, account, cid)
    assert c.status_code == 200
    token = c.json()["claim_token"]
    assert claim(api, account, cid).status_code == 409            # duplicate claim
    assert command_ids(control(api, account).text) == []           # not delivered again
    assert ack(api, account, cid, token=token, result="paused").status_code == 200
    assert ack(api, account, cid, token=token).status_code == 409  # second ack
    rows = api.get("/api/macrofx/v2/admin/commands", headers=ADMIN, params={"account_id": account}).json()
    row = next(r for r in rows if r["command_id"] == cid)
    assert row["status"] == "ACKED" and row["result"] == "paused"
    assert row["claimed_at"] and row["acknowledged_at"]
    assert "claim_token" not in row                                 # never exposed


def test_pause_command_latches_server_pause(api, account):
    ready(api, account, pause=False)
    assert "PAUSE_ENTRIES,0" in control(api, account).text
    create(api, account, action="PAUSE_ENTRIES")
    assert "PAUSE_ENTRIES,1" in control(api, account).text


def test_expired_command_not_delivered_or_claimable(api, account):
    ready(api, account)
    cid = create(api, account).json()["command_id"]
    sql("UPDATE macrofx_v2_commands SET expires_at=NOW()-INTERVAL '1 second' WHERE command_id=$1", uuid.UUID(cid))
    assert command_ids(control(api, account).text) == []
    assert claim(api, account, cid).status_code == 409


def test_claim_rejected_when_remote_disabled(api, account):
    heartbeat(api, account)
    cid = create(api, account).json()["command_id"]
    assert claim(api, account, cid).status_code == 409


def test_claim_rejected_for_other_account(api, account):
    ready(api, account)
    other = account + "x"
    ready(api, other)
    cid = create(api, account).json()["command_id"]
    assert claim(api, other, cid).status_code == 409
    assert claim(api, account, cid).status_code == 200


def test_invalid_acknowledgements_rejected(api, account):
    ready(api, account)
    cid = create(api, account).json()["command_id"]
    assert ack(api, account, cid, token="x").status_code == 409            # not claimed yet
    token = claim(api, account, cid).json()["claim_token"]
    assert ack(api, account, cid, status="DONE", token=token).status_code == 422
    assert ack(api, account, str(uuid.uuid4()), token=token).status_code == 409
    assert ack(api, account, cid).status_code == 409                       # missing token
    assert ack(api, account, cid, token="wrong").status_code == 409        # second chart
    assert ack(api, account, cid, status="FAILED", token=token, result="x").status_code == 200


def test_concurrent_claims_single_winner(base_url, account):
    with httpx.Client(base_url=base_url, timeout=20) as api:
        ready(api, account)
        cid = create(api, account).json()["command_id"]

    def one(_):
        with httpx.Client(base_url=base_url, timeout=20) as c:
            return claim(c, account, cid).status_code

    with cf.ThreadPoolExecutor(12) as ex:
        codes = list(ex.map(one, range(12)))
    assert codes.count(200) == 1, codes
    assert codes.count(409) == 11, codes


def test_concurrent_polling_has_no_schema_errors(base_url, account):
    with httpx.Client(base_url=base_url, timeout=20) as api:
        ready(api, account)

    def one(_):
        with httpx.Client(base_url=base_url, timeout=20) as c:
            return control(c, account).status_code

    with cf.ThreadPoolExecutor(16) as ex:
        codes = list(ex.map(one, range(48)))
    assert set(codes) == {200}, codes


# ---------- Reconciliation preview (read-only) ----------

def _weekly(targets):
    run = sql("""INSERT INTO macrofx_weekly_runs(week_ending,strategy_version,snapshot_json,targets_json,report_markdown)
                 VALUES(CURRENT_DATE + (random()*100000)::int,'test','{}','[]','') RETURNING id""", fetch=True)[0]["id"]
    sql("UPDATE macrofx_targets SET active=FALSE")
    for sym, d, lots in targets:
        sql("""INSERT INTO macrofx_targets(weekly_run_id,expires_at,symbol,direction,lots,score)
               VALUES($1,NOW()+INTERVAL '7 days',$2,$3,$4,1)""", run, sym, d, lots)
    return run


def _positions(api, account, rows):
    body = "symbol,ticket,side,lots,open,cur,pnl,swap,comm,magic\n" + "".join(
        f"{s},{t},{side},{lots},1,1,0,0,0,{magic}\n" for s, t, side, lots, magic in rows)
    r = api.post("/api/macrofx/positions-csv", headers={**EA, "Content-Type": "text/plain"},
                 params={"account_id": account}, content=body)
    assert r.status_code == 200


def _preview(api, account):
    return api.get("/api/macrofx/v2/admin/reconcile-preview", headers=ADMIN, params={"account_id": account})


def _count_commands(account):
    return sql("SELECT COUNT(*) AS n FROM macrofx_v2_commands WHERE account_id=$1", account, fetch=True)[0]["n"]


def test_reconcile_requires_fresh_snapshot(api, account):
    ready(api, account)
    _weekly([("EURUSD", "LONG", 0.01)])
    assert _preview(api, account).status_code == 409
    _positions(api, account, [])
    sql("UPDATE macrofx_v2_position_snapshots SET captured_at=NOW()-INTERVAL '3 minutes' WHERE account_id=$1", account)
    assert _preview(api, account).status_code == 409


def test_reconcile_suffixes_direction_size_and_ownership(api, account):
    ready(api, account)
    run = _weekly([("EURUSD", "LONG", 0.01), ("USDJPY", "SHORT", 0.01)])
    _positions(api, account, [
        ("EURUSD.m", 111, "BUY", 0.01, 26092601),   # matches target (suffix handled)
        ("GBPUSDm", 222, "SELL", 0.01, 26092601),   # unexpected -> close candidate
        ("AUDUSD", 333, "BUY", 0.05, 12345),        # manual trade, other magic -> ignored
    ])
    before = _count_commands(account)
    p = _preview(api, account)
    assert p.status_code == 200, p.text
    d = p.json()
    assert d["weekly_run_id"] == run
    assert {x["symbol"] for x in d["open_positions"]} == {"EURUSD", "GBPUSD"}
    assert [c["ticket"] for c in d["close_candidates"]] == [222]
    assert d["open_candidates"] == []          # closes resolved first
    assert _count_commands(account) == before  # preview never writes commands


def test_reconcile_wrong_direction_or_size_is_close_candidate(api, account):
    ready(api, account)
    _weekly([("EURUSD", "LONG", 0.01)])
    _positions(api, account, [("EURUSD", 444, "SELL", 0.01, 26092601)])
    assert [c["ticket"] for c in _preview(api, account).json()["close_candidates"]] == [444]


def test_reconcile_manual_close_only_suggests(api, account):
    ready(api, account)
    _weekly([("EURUSD", "LONG", 0.01)])
    _positions(api, account, [])  # operator manually closed the position
    before = _count_commands(account)
    d = _preview(api, account).json()
    assert d["open_candidates"] == [{"symbol": "EURUSD", "action": "OPEN_LONG", "lots": 0.01}]
    assert _count_commands(account) == before
    assert "Never auto-open" in d["note"]


def test_reconcile_duplicate_positions_need_manual_review(api, account):
    ready(api, account)
    _weekly([("EURUSD", "LONG", 0.01)])
    _positions(api, account, [("EURUSD", 1, "BUY", 0.01, 26092601), ("EURUSD.m", 2, "BUY", 0.01, 26092601)])
    assert _preview(api, account).status_code == 409


def test_reconcile_reports_unresolved_commands(api, account):
    ready(api, account)
    _weekly([("EURUSD", "LONG", 0.01)])
    _positions(api, account, [])
    create(api, account)
    assert _preview(api, account).json()["unresolved_commands"] == 1


def test_reconcile_rejects_stale_target_set(api, account):
    ready(api, account)
    _weekly([("EURUSD", "LONG", 0.01)])
    sql("UPDATE macrofx_targets SET expires_at=NOW()-INTERVAL '1 minute'")
    _positions(api, account, [])
    assert _preview(api, account).status_code == 409


def test_concurrent_duplicate_open_creates_one(base_url, account):
    with httpx.Client(base_url=base_url, timeout=20) as api:
        ready(api, account)

    def one(_):
        with httpx.Client(base_url=base_url, timeout=20) as c:
            return create(c, account, action="OPEN_LONG", symbol="GBPUSD", lots=0.01).status_code

    with cf.ThreadPoolExecutor(8) as ex:
        codes = list(ex.map(one, range(8)))
    assert codes.count(200) == 1 and codes.count(409) == 7, codes


def test_claimed_but_unacked_command_is_never_redelivered(api, account):
    """Uncertain outcome (EA crashed after claim): must stay CLAIMED, not retried."""
    ready(api, account)
    cid = create(api, account, action="OPEN_LONG", symbol="AUDUSD", lots=0.01).json()["command_id"]
    assert claim(api, account, cid).status_code == 200
    sql("UPDATE macrofx_v2_commands SET expires_at=NOW()-INTERVAL '1 hour' WHERE command_id=$1", uuid.UUID(cid))
    assert command_ids(control(api, account).text) == []
    assert claim(api, account, cid).status_code == 409
    # and a fresh duplicate open for the same pair is blocked while the first is unresolved
    assert create(api, account, action="OPEN_LONG", symbol="AUDUSD", lots=0.01).status_code == 409

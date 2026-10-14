"""MacroFX weekly plan -> approval -> scheduled execution (demo only).

Flow
1. After each Friday model run, the executor builds a *plan* for the account:
   close bridge positions the model dropped, then open the new targets.
   If nothing needs to change the plan is NO_CHANGES.
2. A human approves (or rejects) the plan on the dashboard with the admin key.
3. Approved plans run inside the execution window (Mon-Fri 04:00-16:00 ET),
   by default from Monday 04:00 ET, after the London open and away from the
   Sunday-reopen spreads. Steps go one at a time through the normal v2 command
   path (claim token, EA safety checks), closes first, then opens.
4. Remote control is switched on only while a step is in flight and switched
   off when the plan finishes, is cancelled, or needs review.

Safety rules
- Demo heartbeat must be fresh and the EA must be v2.x before any step.
- Opens are skipped if the pair is already held or the 2-position cap is hit.
- Closes are skipped if the ticket is no longer open (e.g. closed by hand).
- A plan is built from the positions held when it is built, so a position the
  operator closed by hand is never reopened inside the same week.
- Opens run with a tight spread cap; a spread block retries hourly.
- A command that the EA claimed but never acknowledged is NEVER retried: the
  plan stops in NEEDS_REVIEW and remote control is switched off.
"""
from __future__ import annotations

import asyncio
import json
import os
import uuid
from datetime import datetime, time as dtime, timedelta, timezone
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Header, HTTPException

from macrofx import get_pool
from macrofx_control_v2 import admin_auth, database

router = APIRouter(prefix="/api/macrofx/v2", tags=["macrofx-v2-proposals"])

ET = ZoneInfo("America/New_York")
ACCOUNT = os.environ.get("MACROFX_DASHBOARD_ACCOUNT", "1041307")
MAGIC = 26092601
CANON = ("EURUSD", "GBPUSD", "AUDUSD", "NZDUSD", "USDJPY", "USDCAD", "USDCHF",
         "EURGBP", "EURJPY", "EURCHF", "EURCAD", "EURAUD", "EURNZD",
         "GBPJPY", "GBPCHF", "GBPCAD", "GBPAUD", "GBPNZD",
         "AUDJPY", "AUDCHF", "AUDCAD", "AUDNZD",
         "NZDJPY", "NZDCHF", "NZDCAD", "CADJPY", "CADCHF", "CHFJPY")
WINDOW_START = dtime(4, 0)    # ET, after the London open
WINDOW_END = dtime(16, 0)     # ET, well before the 17:00 rollover
EXEC_MAX_SPREAD = float(os.environ.get("MACROFX_EXEC_MAX_SPREAD", "30"))  # points (3 pips)
SPREAD_RETRY_MIN = 60
SPREAD_MAX_TRIES = 8
UNCLAIMED_MAX_TRIES = 4
CLAIM_STUCK_SEC = 180
REASON_PREFIX = "Weekly plan #"

SCHEMA = """
CREATE TABLE IF NOT EXISTS macrofx_v2_proposals (
 id BIGSERIAL PRIMARY KEY,
 account_id TEXT NOT NULL,
 weekly_run_id BIGINT NOT NULL,
 week_ending DATE,
 strategy_version TEXT,
 created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 status TEXT NOT NULL,
 steps_json JSONB NOT NULL DEFAULT '[]'::jsonb,
 positions_json JSONB NOT NULL DEFAULT '[]'::jsonb,
 execute_after TIMESTAMPTZ,
 next_attempt_at TIMESTAMPTZ,
 decided_at TIMESTAMPTZ,
 decided_note TEXT,
 finished_at TIMESTAMPTZ,
 log_json JSONB NOT NULL DEFAULT '[]'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_macrofx_v2_proposals_acct ON macrofx_v2_proposals(account_id,id);
"""
OPEN_STATES = ("PROPOSED", "APPROVED", "EXECUTING")
_schema_ready = False


async def ensure_schema(pool):
    global _schema_ready
    await database()  # v2 command schema (adds proposal_id etc.)
    if not _schema_ready:
        async with pool.acquire() as conn:
            await conn.execute(SCHEMA)
        _schema_ready = True


# ---------------------------------------------------------------- time window
def in_window(t: datetime) -> bool:
    e = t.astimezone(ET)
    return e.weekday() < 5 and WINDOW_START <= e.time() < WINDOW_END


def next_window_start(t: datetime) -> datetime:
    """Earliest moment >= t inside the execution window."""
    if in_window(t):
        return t
    e = t.astimezone(ET)
    d = e.date()
    if e.time() >= WINDOW_START:
        d += timedelta(days=1)
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return datetime.combine(d, WINDOW_START, tzinfo=ET).astimezone(timezone.utc)


def default_execute_after(run_created: datetime) -> datetime:
    """The first window start strictly after the weekend that follows the run (normally Monday 04:00 ET)."""
    e = run_created.astimezone(ET)
    d = e.date() + timedelta(days=1)
    while d.weekday() != 0:          # next Monday
        d += timedelta(days=1)
    if e.weekday() < 4:              # run happened Mon-Thu (manual/forced run): next window instead
        return next_window_start(run_created)
    return datetime.combine(d, WINDOW_START, tzinfo=ET).astimezone(timezone.utc)


# ---------------------------------------------------------------- helpers
def canonical(sym: str) -> str:
    s = (sym or "").upper()
    return next((c for c in CANON if c in s), s[:6])


def _j(v, default):
    if v is None:
        return default
    if isinstance(v, str):
        try:
            return json.loads(v)
        except Exception:
            return default
    return v


def _side(s: str) -> str:
    return "LONG" if str(s).upper() in ("BUY", "LONG") else "SHORT"


async def _owned_positions(conn, account: str, max_age_sec: Optional[int] = None):
    snap = await conn.fetchrow("""SELECT captured_at,positions_json FROM macrofx_v2_position_snapshots
        WHERE account_id=$1""", account)
    if not snap:
        return None, None
    if max_age_sec is not None and (datetime.now(timezone.utc) - snap["captured_at"]).total_seconds() > max_age_sec:
        return None, snap["captured_at"]
    pos = [p for p in _j(snap["positions_json"], []) if int(p.get("magic", 0)) == MAGIC]
    return [{"symbol": canonical(p["symbol"]), "broker_symbol": p["symbol"], "ticket": int(p["ticket"]),
             "direction": _side(p["side"]), "lots": float(p.get("lots", 0))} for p in pos], snap["captured_at"]


def build_steps(positions: List[Dict[str, Any]], targets: List[Dict[str, Any]], max_positions: int = 2):
    """Pure planning function: closes first, then opens. Never more than max_positions."""
    want = {t["symbol"]: t for t in targets}
    steps, kept, seen = [], [], set()
    for p in positions:
        t = want.get(p["symbol"])
        dup = p["symbol"] in seen
        seen.add(p["symbol"])
        if t and t["direction"] == p["direction"] and not dup:
            kept.append(p)
            continue
        reason = ("duplicate position" if dup else
                  "direction flipped" if t else "no longer a target")
        steps.append({"kind": "CLOSE", "symbol": p["symbol"], "direction": p["direction"],
                      "ticket": p["ticket"], "lots": p["lots"], "reason": reason, "status": "PENDING"})
    held = {p["symbol"] for p in kept}
    slots = max_positions - len(kept)
    for t in sorted(targets, key=lambda x: -abs(float(x.get("score") or 0))):
        if t["symbol"] in held:
            continue
        if slots <= 0:
            break
        steps.append({"kind": "OPEN", "symbol": t["symbol"], "direction": t["direction"],
                      "lots": float(t.get("lots") or 0.01), "score": float(t.get("score") or 0),
                      "reason": "new target", "status": "PENDING"})
        slots -= 1
    holds = [{"symbol": p["symbol"], "direction": p["direction"], "ticket": p["ticket"]} for p in kept]
    return steps, holds


def _log(entries: List[Dict[str, Any]], msg: str, now: datetime) -> List[Dict[str, Any]]:
    return (entries + [{"at": now.isoformat(), "msg": msg}])[-60:]


async def _set_remote(conn, account: str, enabled: bool, pause: bool):
    if not enabled:
        await conn.execute("""UPDATE macrofx_v2_settings SET enabled=FALSE,pause_entries=TRUE,
            revision=revision+1,updated_at=NOW() WHERE account_id=$1""", account)
        return
    await conn.execute("""INSERT INTO macrofx_v2_settings(account_id,enabled,pause_entries,max_positions,
          max_lot_per_pair,max_spread_points,slippage_points) VALUES($1,TRUE,$2,2,0.01,$3,30)
        ON CONFLICT(account_id) DO UPDATE SET enabled=TRUE,pause_entries=$2,max_positions=2,
          max_lot_per_pair=0.01,max_spread_points=$3,slippage_points=30,
          revision=macrofx_v2_settings.revision+1,updated_at=NOW()""", account, pause, EXEC_MAX_SPREAD)


async def _save(conn, pid: int, **fields):
    cols, vals = [], []
    for i, (k, v) in enumerate(fields.items(), start=2):
        if k in ("steps_json", "log_json", "positions_json"):
            cols.append(f"{k}=${i}::jsonb")
            vals.append(json.dumps(v))
        else:
            cols.append(f"{k}=${i}")
            vals.append(v)
    await conn.execute(f"UPDATE macrofx_v2_proposals SET {','.join(cols)} WHERE id=$1", pid, *vals)


# ---------------------------------------------------------------- plan creation
async def ensure_plan_for_latest_run(conn, account: str, now: datetime, force: bool = False):
    run = await conn.fetchrow("""SELECT id,week_ending,created_at,strategy_version FROM macrofx_weekly_runs
        ORDER BY week_ending DESC LIMIT 1""")
    if not run:
        return None
    existing = await conn.fetchrow("""SELECT id,status FROM macrofx_v2_proposals
        WHERE account_id=$1 AND weekly_run_id=$2 AND status<>'SUPERSEDED' ORDER BY id DESC LIMIT 1""", account, run["id"])
    if existing and not force:
        return existing["id"]
    if existing and existing["status"] in ("EXECUTING",):
        raise HTTPException(409, "A plan for this week is executing; cancel it first")
    positions, snap_at = await _owned_positions(conn, account, max_age_sec=600)
    if positions is None:
        return None  # wait for a fresh snapshot from the EA
    targets = [{"symbol": r["symbol"], "direction": r["direction"], "lots": float(r["lots"]),
                "score": float(r["score"] or 0)} for r in await conn.fetch(
        "SELECT symbol,direction,lots,score FROM macrofx_targets WHERE weekly_run_id=$1", run["id"])]
    steps, holds = build_steps(positions, targets)
    async with conn.transaction():
        # Older plans that never started are superseded by the newer run (or a regenerate).
        await conn.execute("""UPDATE macrofx_v2_proposals SET status='SUPERSEDED',finished_at=NOW()
            WHERE account_id=$1 AND status IN ('PROPOSED','APPROVED')""", account)
        if force:
            await conn.execute("""UPDATE macrofx_v2_proposals SET status='SUPERSEDED',finished_at=COALESCE(finished_at,NOW())
                WHERE account_id=$1 AND weekly_run_id=$2 AND status IN ('NO_CHANGES','REJECTED','EXPIRED')""",
                account, run["id"])
        status = "PROPOSED" if steps else "NO_CHANGES"
        pid = await conn.fetchval("""INSERT INTO macrofx_v2_proposals(account_id,weekly_run_id,week_ending,
              strategy_version,status,steps_json,positions_json,execute_after,log_json)
            VALUES($1,$2,$3,$4,$5,$6::jsonb,$7::jsonb,$8,$9::jsonb) RETURNING id""",
            account, run["id"], run["week_ending"], run["strategy_version"], status,
            json.dumps(steps), json.dumps({"held": positions, "keep": holds, "snapshot_at": snap_at.isoformat()}),
            default_execute_after(run["created_at"]),
            json.dumps(_log([], f"Plan built from week ending {run['week_ending']}: "
                                f"{len([s for s in steps if s['kind']=='CLOSE'])} close, "
                                f"{len([s for s in steps if s['kind']=='OPEN'])} open, {len(holds)} hold", now)))
    return pid


# ---------------------------------------------------------------- execution
async def _preconditions(conn, account: str) -> Optional[str]:
    hb = await conn.fetchrow("""SELECT is_demo,ea_version,captured_at FROM macrofx_heartbeats
        WHERE account_id=$1 ORDER BY captured_at DESC LIMIT 1""", account)
    if not hb or not hb["is_demo"]:
        return "no demo heartbeat"
    if (datetime.now(timezone.utc) - hb["captured_at"]).total_seconds() > 180:
        return "EA offline (no heartbeat in 3 min)"
    if "Bridge-2." not in (hb["ea_version"] or ""):
        return f"EA version {hb['ea_version']} cannot run commands"
    return None


async def _send(conn, account: str, prop, step) -> str:
    cid = uuid.uuid4()
    action = "CLOSE_TICKET" if step["kind"] == "CLOSE" else ("OPEN_LONG" if step["direction"] == "LONG" else "OPEN_SHORT")
    await _set_remote(conn, account, True, pause=(step["kind"] == "CLOSE"))
    await conn.execute("""INSERT INTO macrofx_v2_commands(command_id,account_id,action,symbol,ticket,lots,reason,
          expires_at,signal_score,strategy_version,proposal_id)
        VALUES($1,$2,$3,$4,$5,$6,$7,NOW()+INTERVAL '5 minutes',$8,$9,$10)""",
        cid, account, action, step["symbol"] if step["kind"] == "OPEN" else step["symbol"],
        int(step.get("ticket") or 0), float(step.get("lots") or 0) if step["kind"] == "OPEN" else 0.0,
        f"{REASON_PREFIX}{prop['id']}: {step['kind'].lower()} {step['symbol']} ({step['reason']})",
        step.get("score"), prop["strategy_version"], prop["id"])
    return str(cid)


async def _finish(conn, account: str, prop, steps, log, now, status: str, msg: str):
    await _set_remote(conn, account, False, True)
    await _save(conn, prop["id"], status=status, steps_json=steps, finished_at=now,
                next_attempt_at=None, log_json=_log(log, msg, now))


async def advance(conn, account: str, prop, now: datetime):
    """Advance one approved/executing plan by at most one step."""
    steps = _j(prop["steps_json"], [])
    log = _j(prop["log_json"], [])
    if prop["status"] == "APPROVED":
        await _save(conn, prop["id"], status="EXECUTING", log_json=_log(log, "Execution started", now))
        log = _log(log, "Execution started", now)
    if not in_window(now):
        nxt = next_window_start(now)
        if prop["next_attempt_at"] is None or prop["next_attempt_at"] < nxt:
            await _set_remote(conn, account, False, True)
            await _save(conn, prop["id"], next_attempt_at=nxt,
                        log_json=_log(log, f"Outside the execution window; waiting until {nxt.astimezone(ET):%a %H:%M} ET", now))
        return
    sent = any(s["status"] == "SENT" for s in steps)
    if not sent and prop["next_attempt_at"] and prop["next_attempt_at"] > now:
        return
    problem = await _preconditions(conn, account)
    if problem:
        await _set_remote(conn, account, False, True)
        await _save(conn, prop["id"], next_attempt_at=now + timedelta(minutes=5),
                    log_json=_log(log, f"Waiting: {problem}", now))
        return

    step = next((s for s in steps if s["status"] in ("PENDING", "RETRY", "SENT")), None)
    if step is None:
        failed = [s for s in steps if s["status"] == "FAILED"]
        await _finish(conn, account, prop, steps, log, now, "FAILED" if failed else "DONE",
                      "Plan finished" + (f" with {len(failed)} failed step(s)" if failed else "") + "; remote control off")
        return

    if step["status"] == "SENT":
        cmd = await conn.fetchrow("""SELECT status,result,claimed_at,expires_at FROM macrofx_v2_commands
            WHERE command_id=$1""", uuid.UUID(step["command_id"]))
        if cmd is None:
            step["status"] = "FAILED"; step["result"] = "command missing"
        elif cmd["status"] == "PENDING":
            if cmd["expires_at"] > now:
                return  # waiting for the EA's next poll
            await conn.execute("UPDATE macrofx_v2_commands SET status='CANCELLED',result='expired_unclaimed' WHERE command_id=$1 AND status='PENDING'",
                               uuid.UUID(step["command_id"]))
            step["attempts"] = step.get("attempts", 0) + 1
            if step["attempts"] >= UNCLAIMED_MAX_TRIES:
                step["status"] = "FAILED"; step["result"] = "EA never claimed the command"
            else:
                step["status"] = "RETRY"; step["result"] = "not claimed in 5 min; resending"
        elif cmd["status"] == "CLAIMED":
            if cmd["claimed_at"] and (now - cmd["claimed_at"]).total_seconds() > CLAIM_STUCK_SEC:
                step["status"] = "UNCERTAIN"; step["result"] = "claimed but never acknowledged"
                await _finish(conn, account, prop, steps, log, now, "NEEDS_REVIEW",
                              f"{step['kind']} {step['symbol']}: EA claimed the order but never reported back. "
                              "Not retried. Check MT4 and positions by hand. Remote control off.")
            return
        elif cmd["status"] == "ACKED":
            step["status"] = "DONE"; step["result"] = cmd["result"]
        else:  # FAILED / CANCELLED
            res = cmd["result"] or ""
            step["result"] = res
            if res == "spread_or_quote_block":
                step["spread_tries"] = step.get("spread_tries", 0) + 1
                if step["spread_tries"] >= SPREAD_MAX_TRIES:
                    step["status"] = "FAILED"
                else:
                    step["status"] = "RETRY"
                    await _set_remote(conn, account, False, True)
                    await _save(conn, prop["id"], steps_json=steps, next_attempt_at=now + timedelta(minutes=SPREAD_RETRY_MIN),
                                log_json=_log(log, f"{step['symbol']}: spread above {EXEC_MAX_SPREAD:.0f} points; retrying in 1 hour", now))
                    return
            elif res in ("ticket_not_owned_or_closed", "pair_already_open", "position_limit"):
                step["status"] = "SKIPPED"
            elif res == "local_safety_block" or res.startswith("broker_error"):
                step["status"] = "FAILED"
                await _finish(conn, account, prop, steps, log, now, "NEEDS_REVIEW",
                              f"{step['kind']} {step['symbol']} refused by the EA ({res}). "
                              "Check EnableTrading / kill switch / broker. Remote control off.")
                return
            else:
                step["status"] = "FAILED"
        await _save(conn, prop["id"], steps_json=steps, next_attempt_at=None,
                    log_json=_log(log, f"{step['kind']} {step['symbol']}: {step['status']} ({step.get('result')})", now))
        return

    # PENDING / RETRY: revalidate against what is actually held right now
    if prop["next_attempt_at"] and prop["next_attempt_at"] > now:
        return
    positions, _ = await _owned_positions(conn, account, max_age_sec=180)
    if positions is None:
        await _save(conn, prop["id"], next_attempt_at=now + timedelta(minutes=2),
                    log_json=_log(log, "Waiting for a fresh position snapshot", now))
        return
    unresolved = await conn.fetchval("""SELECT COUNT(*) FROM macrofx_v2_commands WHERE account_id=$1
        AND (status='CLAIMED' OR (status='PENDING' AND expires_at>NOW()))""", account)
    if unresolved:
        await _save(conn, prop["id"], next_attempt_at=now + timedelta(minutes=2),
                    log_json=_log(log, "Waiting: another command is in flight", now))
        return
    if step["kind"] == "CLOSE":
        if not any(p["ticket"] == int(step["ticket"]) for p in positions):
            step["status"] = "SKIPPED"; step["result"] = "already closed"
            await _save(conn, prop["id"], steps_json=steps, log_json=_log(log, f"CLOSE {step['symbol']}: already closed, skipped", now))
            return
    else:
        if any(p["symbol"] == step["symbol"] for p in positions):
            step["status"] = "SKIPPED"; step["result"] = "already held"
            await _save(conn, prop["id"], steps_json=steps, log_json=_log(log, f"OPEN {step['symbol']}: already held, skipped", now))
            return
        if len(positions) >= 2:
            step["status"] = "SKIPPED"; step["result"] = "2 positions already open"
            await _save(conn, prop["id"], steps_json=steps, log_json=_log(log, f"OPEN {step['symbol']}: position cap reached, skipped", now))
            return
    step["command_id"] = await _send(conn, account, prop, step)
    step["status"] = "SENT"
    step["sent_at"] = now.isoformat()
    await _save(conn, prop["id"], steps_json=steps, next_attempt_at=None,
                log_json=_log(log, f"Sent {step['kind']} {step['symbol']}", now))


async def executor_tick(pool, now: Optional[datetime] = None, account: str = ACCOUNT):
    now = now or datetime.now(timezone.utc)
    await ensure_schema(pool)
    async with pool.acquire() as conn:
        if not await conn.fetchval("SELECT pg_try_advisory_lock(hashtext('macrofx_v2_executor'))"):
            return
        try:
            await ensure_plan_for_latest_run(conn, account, now)
            await conn.execute("""UPDATE macrofx_v2_proposals SET status='EXPIRED',finished_at=NOW()
                WHERE account_id=$1 AND status='PROPOSED' AND created_at < NOW() - INTERVAL '7 days'""", account)
            prop = await conn.fetchrow("""SELECT * FROM macrofx_v2_proposals WHERE account_id=$1
                AND status IN ('APPROVED','EXECUTING') ORDER BY id LIMIT 1""", account)
            if prop and now >= (prop["execute_after"] or now):
                await advance(conn, account, prop, now)
        finally:
            await conn.execute("SELECT pg_advisory_unlock(hashtext('macrofx_v2_executor'))")


async def executor_loop(interval: int = 30):
    while True:
        try:
            await executor_tick(await get_pool())
        except Exception as e:  # never let the loop die
            print("MACROFX_EXECUTOR_ERROR", repr(e)[:300], flush=True)
        await asyncio.sleep(interval)


# ---------------------------------------------------------------- API
def _public(r) -> Dict[str, Any]:
    d = {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in dict(r).items()}
    for k in ("steps_json", "log_json", "positions_json"):
        d[k] = _j(d.get(k), [])
    return d


async def list_proposals(pool, account: str = ACCOUNT, limit: int = 10):
    await ensure_schema(pool)
    async with pool.acquire() as conn:
        rows = await conn.fetch("""SELECT * FROM macrofx_v2_proposals WHERE account_id=$1
            ORDER BY id DESC LIMIT $2""", account, limit)
    return [_public(r) for r in rows]


@router.get("/proposals")
async def get_proposals():
    return await list_proposals(await get_pool())


async def _decide(pid: int, key: str, new_status: str, allowed: tuple, note: str, **extra):
    admin_auth(key)
    pool = await get_pool()
    await ensure_schema(pool)
    now = datetime.now(timezone.utc)
    async with pool.acquire() as conn:
        p = await conn.fetchrow("SELECT * FROM macrofx_v2_proposals WHERE id=$1", pid)
        if not p:
            raise HTTPException(404, "No such plan")
        if p["status"] not in allowed:
            raise HTTPException(409, f"Plan is {p['status']}")
        log = _log(_j(p["log_json"], []), note, now)
        await _save(conn, pid, status=new_status, decided_at=now, decided_note=note, log_json=log, **extra)
        return _public(await conn.fetchrow("SELECT * FROM macrofx_v2_proposals WHERE id=$1", pid))


@router.post("/admin/proposals/{pid}/approve")
async def approve(pid: int, run_now: bool = False, x_macrofx_admin_key: str = Header(default="")):
    extra = {}
    note = "Approved on dashboard"
    if run_now:
        extra["execute_after"] = next_window_start(datetime.now(timezone.utc))
        note += " (run at the next execution window)"
    return await _decide(pid, x_macrofx_admin_key, "APPROVED", ("PROPOSED",), note, **extra)


@router.post("/admin/proposals/{pid}/reject")
async def reject(pid: int, x_macrofx_admin_key: str = Header(default="")):
    return await _decide(pid, x_macrofx_admin_key, "REJECTED", ("PROPOSED", "APPROVED"),
                         "Rejected on dashboard", finished_at=datetime.now(timezone.utc))


@router.post("/admin/proposals/{pid}/cancel")
async def cancel(pid: int, x_macrofx_admin_key: str = Header(default="")):
    admin_auth(x_macrofx_admin_key)
    pool = await get_pool()
    await ensure_schema(pool)
    now = datetime.now(timezone.utc)
    async with pool.acquire() as conn:
        if not await conn.fetchval("SELECT pg_try_advisory_lock(hashtext('macrofx_v2_executor'))"):
            raise HTTPException(409, "Executor busy; try again in a few seconds")
        try:
            p = await conn.fetchrow("SELECT * FROM macrofx_v2_proposals WHERE id=$1", pid)
            if not p or p["status"] not in ("APPROVED", "EXECUTING"):
                raise HTTPException(409, "Only an approved or executing plan can be cancelled")
            steps = _j(p["steps_json"], [])
            uncertain = False
            for s in steps:
                if s["status"] == "SENT":
                    n = await conn.execute("""UPDATE macrofx_v2_commands SET status='CANCELLED',result='cancelled_by_operator'
                        WHERE command_id=$1 AND status='PENDING'""", uuid.UUID(s["command_id"]))
                    if n.endswith(" 0"):
                        uncertain = True  # already claimed by the EA
                        s["status"] = "UNCERTAIN"
                    else:
                        s["status"] = "SKIPPED"; s["result"] = "cancelled"
                elif s["status"] in ("PENDING", "RETRY"):
                    s["status"] = "SKIPPED"; s["result"] = "cancelled"
            await _finish(conn, p["account_id"], p, steps, _j(p["log_json"], []), now,
                          "NEEDS_REVIEW" if uncertain else "CANCELLED",
                          "Cancelled on dashboard" + ("; one order was already claimed by the EA, check MT4" if uncertain else "")
                          + "; remote control off")
            return _public(await conn.fetchrow("SELECT * FROM macrofx_v2_proposals WHERE id=$1", pid))
        finally:
            await conn.execute("SELECT pg_advisory_unlock(hashtext('macrofx_v2_executor'))")


@router.post("/admin/proposals/regenerate")
async def regenerate(x_macrofx_admin_key: str = Header(default="")):
    """Rebuild this week's plan from the positions held right now (e.g. after a manual trade)."""
    admin_auth(x_macrofx_admin_key)
    pool = await get_pool()
    await ensure_schema(pool)
    async with pool.acquire() as conn:
        if not await conn.fetchval("SELECT pg_try_advisory_lock(hashtext('macrofx_v2_executor'))"):
            raise HTTPException(409, "Executor busy; try again in a few seconds")
        try:
            pid = await ensure_plan_for_latest_run(conn, ACCOUNT, datetime.now(timezone.utc), force=True)
        finally:
            await conn.execute("SELECT pg_advisory_unlock(hashtext('macrofx_v2_executor'))")
    if pid is None:
        raise HTTPException(409, "No weekly run or no fresh position snapshot yet")
    return {"proposal_id": pid}

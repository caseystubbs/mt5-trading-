"""MacroFX Bridge v2 remote-control API (demo only).

This module is intentionally additive. v1.5 targets remain unchanged until an
MT4 v2 bridge is installed and the operator explicitly enables v2.
Admin commands require MACROFX_ADMIN_KEY, distinct from the EA credential.
"""
import os
import uuid
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from macrofx import get_pool, _verify

router = APIRouter(prefix="/api/macrofx/v2", tags=["macrofx-v2"])

SCHEMA = """
CREATE TABLE IF NOT EXISTS macrofx_v2_settings (
 account_id TEXT PRIMARY KEY,
 enabled BOOLEAN NOT NULL DEFAULT FALSE,
 pause_entries BOOLEAN NOT NULL DEFAULT TRUE,
 max_positions INTEGER NOT NULL DEFAULT 2,
 max_lot_per_pair DOUBLE PRECISION NOT NULL DEFAULT 0.01,
 max_spread_points DOUBLE PRECISION NOT NULL DEFAULT 300,
 slippage_points INTEGER NOT NULL DEFAULT 30,
 revision BIGINT NOT NULL DEFAULT 1,
 updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS macrofx_v2_commands (
 command_id UUID PRIMARY KEY,
 account_id TEXT NOT NULL,
 action TEXT NOT NULL CHECK(action IN ('CLOSE_TICKET','OPEN_LONG','OPEN_SHORT','PAUSE_ENTRIES','RESUME_ENTRIES')),
 symbol TEXT,
 ticket BIGINT,
 lots DOUBLE PRECISION,
 status TEXT NOT NULL DEFAULT 'PENDING' CHECK(status IN ('PENDING','CLAIMED','ACKED','FAILED','CANCELLED')),
 claimed_at TIMESTAMPTZ,
 reason TEXT NOT NULL,
 created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 expires_at TIMESTAMPTZ NOT NULL,
 acknowledged_at TIMESTAMPTZ,
 result TEXT
);
ALTER TABLE macrofx_v2_commands ADD COLUMN IF NOT EXISTS claimed_at TIMESTAMPTZ;
DO $ BEGIN
 IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='macrofx_v2_commands_status_check_v2') THEN
  ALTER TABLE macrofx_v2_commands DROP CONSTRAINT IF EXISTS macrofx_v2_commands_status_check;
  ALTER TABLE macrofx_v2_commands ADD CONSTRAINT macrofx_v2_commands_status_check_v2
   CHECK(status IN ('PENDING','CLAIMED','ACKED','FAILED','CANCELLED'));
 END IF;
END $;
CREATE INDEX IF NOT EXISTS idx_macrofx_v2_commands_poll ON macrofx_v2_commands(account_id,status,created_at);
"""

class SettingsUpdate(BaseModel):
    account_id: str = Field(min_length=1, max_length=32)
    enabled: bool = False
    pause_entries: bool = True
    max_positions: int = Field(default=2, ge=0, le=2)
    max_lot_per_pair: float = Field(default=0.01, gt=0, le=0.01)
    max_spread_points: float = Field(default=300, ge=0, le=1000)
    slippage_points: int = Field(default=30, ge=0, le=100)

class CommandCreate(BaseModel):
    account_id: str = Field(min_length=1, max_length=32)
    action: str
    symbol: str = ""
    ticket: int = 0
    lots: float = 0
    reason: str = Field(min_length=3, max_length=500)

class CommandAck(BaseModel):
    account_id: str
    command_id: uuid.UUID
    status: str
    result: str = ""

def admin_auth(key: str):
    configured = os.environ.get("MACROFX_ADMIN_KEY", "")
    if not configured or key != configured:
        raise HTTPException(403, "Admin authentication required")

async def database():
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(SCHEMA)
    return pool

async def require_demo(conn, account_id: str):
    hb = await conn.fetchrow(
        "SELECT is_demo,captured_at FROM macrofx_heartbeats WHERE account_id=$1 ORDER BY captured_at DESC LIMIT 1",
        account_id)
    if not hb or not hb["is_demo"]:
        raise HTTPException(409, "A verified demo heartbeat is required")
    if datetime.now(timezone.utc)-hb["captured_at"] > timedelta(minutes=10):
        raise HTTPException(409, "Demo heartbeat is stale")

@router.post("/admin/settings")
async def update_settings(body: SettingsUpdate, x_macrofx_admin_key: str = Header(default="")):
    admin_auth(x_macrofx_admin_key)
    pool = await database()
    async with pool.acquire() as conn:
        await require_demo(conn, body.account_id)
        row = await conn.fetchrow("""
          INSERT INTO macrofx_v2_settings(account_id,enabled,pause_entries,max_positions,
          max_lot_per_pair,max_spread_points,slippage_points)
          VALUES($1,$2,$3,$4,$5,$6,$7)
          ON CONFLICT(account_id) DO UPDATE SET enabled=$2,pause_entries=$3,max_positions=$4,
          max_lot_per_pair=$5,max_spread_points=$6,slippage_points=$7,
          revision=macrofx_v2_settings.revision+1,updated_at=NOW()
          RETURNING *""",body.account_id,body.enabled,body.pause_entries,body.max_positions,
          body.max_lot_per_pair,body.max_spread_points,body.slippage_points)
    return dict(row)

@router.post("/admin/commands")
async def create_command(body: CommandCreate, x_macrofx_admin_key: str = Header(default="")):
    admin_auth(x_macrofx_admin_key)
    if body.action not in ("CLOSE_TICKET","OPEN_LONG","OPEN_SHORT","PAUSE_ENTRIES","RESUME_ENTRIES"):
        raise HTTPException(422,"Unsupported action")
    if body.action == "CLOSE_TICKET" and body.ticket <= 0:
        raise HTTPException(422,"Closing requires a ticket")
    if body.action.startswith("OPEN_") and (not body.symbol.isalpha() or len(body.symbol)!=6 or body.lots!=0.01):
        raise HTTPException(422,"Opening requires a six-letter pair and 0.01 lots")
    pool = await database()
    async with pool.acquire() as conn:
        await require_demo(conn,body.account_id)
        cid=uuid.uuid4()
        await conn.execute("""
          INSERT INTO macrofx_v2_commands(command_id,account_id,action,symbol,ticket,lots,reason,expires_at)
          VALUES($1,$2,$3,$4,$5,$6,$7,NOW()+INTERVAL '5 minutes')""",
          cid,body.account_id,body.action,body.symbol.upper(),body.ticket,body.lots,body.reason)
    return {"command_id":str(cid),"status":"PENDING","expires_in_seconds":300}

@router.get("/control-text",response_class=PlainTextResponse)
async def control_text(account_id: str, x_ea_api_key: str = Header(default="",alias="X-EA-API-Key")):
    _verify(x_ea_api_key)
    pool = await database()
    async with pool.acquire() as conn:
        await require_demo(conn,account_id)
        settings=await conn.fetchrow("SELECT * FROM macrofx_v2_settings WHERE account_id=$1",account_id)
        if not settings:
            return "VERSION,2\nENABLED,0\nPAUSE_ENTRIES,1\nMAX_POSITIONS,0\nMAX_LOT_PER_PAIR,0.01\nMAX_SPREAD_POINTS,300\nSLIPPAGE_POINTS,30\n"
        lines=["VERSION,2",f"REVISION,{settings['revision']}",
               f"ENABLED,{int(settings['enabled'])}",
               f"PAUSE_ENTRIES,{int(settings['pause_entries'])}",
               f"MAX_POSITIONS,{settings['max_positions']}",
               f"MAX_LOT_PER_PAIR,{settings['max_lot_per_pair']}",
               f"MAX_SPREAD_POINTS,{settings['max_spread_points']}",
               f"SLIPPAGE_POINTS,{settings['slippage_points']}"]
        if settings["enabled"]:
            commands=await conn.fetch("""
              SELECT * FROM macrofx_v2_commands WHERE account_id=$1 AND status='PENDING'
              AND expires_at>NOW() ORDER BY created_at LIMIT 10""",account_id)
            for c in commands:
                lines.append(f"COMMAND,{c['command_id']},{c['action']},{c['symbol'] or ''},{c['ticket'] or 0},{c['lots'] or 0}")
        return "\n".join(lines)+"\n"

@router.post("/claim")
async def claim_command(account_id: str, command_id: uuid.UUID,
                        x_ea_api_key: str = Header(default="", alias="X-EA-API-Key")):
    """Atomic, single-consumer claim. Never automatically retry uncertain executions."""
    _verify(x_ea_api_key)
    pool = await database()
    async with pool.acquire() as conn:
        await require_demo(conn, account_id)
        settings = await conn.fetchrow(
            "SELECT enabled FROM macrofx_v2_settings WHERE account_id=$1", account_id)
        if not settings or not settings["enabled"]:
            raise HTTPException(409, "Remote control disabled")
        claimed = await conn.fetchval("""
          UPDATE macrofx_v2_commands SET status='CLAIMED',claimed_at=NOW()
          WHERE command_id=$1 AND account_id=$2 AND status='PENDING'
            AND expires_at>NOW() RETURNING command_id""", command_id, account_id)
    if not claimed:
        raise HTTPException(409, "Already claimed or expired")
    return {"status": "CLAIMED"}

@router.post("/ack")
async def acknowledge(account_id: str, command_id: uuid.UUID, status: str, result: str = "", x_ea_api_key: str = Header(default="",alias="X-EA-API-Key")):
    _verify(x_ea_api_key)
    if status not in ("ACKED","FAILED"):
        raise HTTPException(422,"Invalid acknowledgement")
    pool=await database()
    async with pool.acquire() as conn:
        await require_demo(conn,account_id)
        updated=await conn.fetchval("""
          UPDATE macrofx_v2_commands SET status=$3,result=$4,acknowledged_at=NOW()
          WHERE command_id=$1 AND account_id=$2 AND status='CLAIMED'
          RETURNING command_id""",command_id,account_id,status,result[:1000])
    if not updated:
        raise HTTPException(409,"Command already handled or expired")
    return {"status":"ok"}

@router.get("/admin/commands")
async def list_commands(account_id: str, x_macrofx_admin_key: str = Header(default="")):
    admin_auth(x_macrofx_admin_key)
    pool=await database()
    async with pool.acquire() as conn:
        rows=await conn.fetch("SELECT * FROM macrofx_v2_commands WHERE account_id=$1 ORDER BY created_at DESC LIMIT 50",account_id)
    return [dict(r) for r in rows]

@router.get("/admin/reconcile-preview")
async def reconcile_preview(account_id: str, x_macrofx_admin_key: str = Header(default="")):
    """Read-only target comparison. Never issues a trade."""
    admin_auth(x_macrofx_admin_key)
    pool = await database()
    async with pool.acquire() as conn:
        await require_demo(conn, account_id)
        snapshot = await conn.fetchrow(
            "SELECT captured_at,positions_json FROM macrofx_v2_position_snapshots WHERE account_id=$1",
            account_id)
        if not snapshot or datetime.now(timezone.utc)-snapshot["captured_at"] > timedelta(minutes=2):
            raise HTTPException(409, "Fresh complete position snapshot required")
        settings = await conn.fetchrow(
            "SELECT * FROM macrofx_v2_settings WHERE account_id=$1", account_id)
        targets = await conn.fetch("""
            SELECT t.symbol,t.direction,t.lots,t.weekly_run_id FROM macrofx_targets t
            WHERE t.active=TRUE AND t.expires_at>NOW()
            ORDER BY ABS(t.score) DESC LIMIT 3""")
        latest = await conn.fetchval("SELECT MAX(id) FROM macrofx_weekly_runs")
        if not latest or not targets or len(targets)>2 or any(t["weekly_run_id"]!=latest for t in targets):
            raise HTTPException(409, "Current weekly target set is unavailable or invalid")
        positions = snapshot["positions_json"]
        if isinstance(positions,str):
            import json
            positions=json.loads(positions)
        owned = [p for p in positions if int(p.get("magic",0))==26092601]
        for p in owned:
            p["symbol"] = next((symbol for symbol in (
                "EURUSD","GBPUSD","AUDUSD","NZDUSD","USDJPY","USDCAD","USDCHF",
                "EURGBP","EURJPY","EURCHF","EURCAD","EURAUD","EURNZD",
                "GBPJPY","GBPCHF","GBPCAD","GBPAUD","GBPNZD",
                "AUDJPY","AUDCHF","AUDCAD","AUDNZD",
                "NZDJPY","NZDCHF","NZDCAD","CADJPY","CADCHF","CHFJPY")
                if symbol in p["symbol"]), p["symbol"])
        desired = {t["symbol"]:(t["direction"],float(t["lots"])) for t in targets}
        if len(owned)>2 or len({p["symbol"] for p in owned})!=len(owned):
            raise HTTPException(409, "Unexpected bridge positions; manual review")
        closes=[]
        for p in owned:
            direction = "LONG" if str(p["side"]).upper() in ("BUY","LONG") else "SHORT"
            if p["symbol"] not in desired or desired[p["symbol"]] != (direction,float(p["lots"])):
                closes.append({"ticket":p["ticket"],"symbol":p["symbol"],"action":"CLOSE_TICKET"})
        opens=[]
        if not closes:
            current={p["symbol"] for p in owned}
            for t in targets:
                if t["symbol"] not in current:
                    opens.append({"symbol":t["symbol"],"action":"OPEN_LONG" if t["direction"]=="LONG" else "OPEN_SHORT","lots":float(t["lots"])})
        pending=await conn.fetchval("""SELECT COUNT(*) FROM macrofx_v2_commands
            WHERE account_id=$1 AND status IN ('PENDING','CLAIMED')""",account_id)
    return {"account_id":account_id,"weekly_run_id":latest,
            "snapshot_at":snapshot["captured_at"].isoformat(),
            "enabled":bool(settings and settings["enabled"]),
            "paused":bool(not settings or settings["pause_entries"]),
            "open_positions":owned,"targets":[dict(t) for t in targets],
            "close_candidates":closes,"open_candidates":opens,
            "unresolved_commands":pending,
            "note":"Preview only. Never auto-open after a manual close; operator must review and explicitly authorize a new reconciliation."}


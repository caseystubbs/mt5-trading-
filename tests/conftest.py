"""Test harness for the MacroFX v2 backend.

Runs a real uvicorn server against an isolated PostgreSQL database
(TEST_DATABASE_URL), never the production database. Credentials used here
are throwaway test values.
"""
import asyncio
import os
import socket
import subprocess
import sys
import time
import uuid

import asyncpg
import httpx
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_DB = os.environ.get("TEST_DATABASE_URL", "postgresql://postgres@127.0.0.1:55432/macrofx_test")
EA_KEY = "test-ea-key"
ADMIN_KEY = "test-admin-key"


def sql(query, *args, fetch=False):
    async def run():
        conn = await asyncpg.connect(TEST_DB)
        try:
            if fetch:
                return [dict(r) for r in await conn.fetch(query, *args)]
            return await conn.execute(query, *args)
        finally:
            await conn.close()
    return asyncio.run(run())


def _free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.fixture(scope="session")
def base_url():
    sql("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
    port = _free_port()
    env = dict(os.environ, DATABASE_URL=TEST_DB, EA_API_KEY=EA_KEY,
               MACROFX_ADMIN_KEY=ADMIN_KEY, PYTHONPATH=ROOT)
    env.pop("MACROFX_API_KEY", None)
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "tests.app_under_test:app",
         "--host", "127.0.0.1", "--port", str(port), "--log-level", "warning"],
        cwd=ROOT, env=env)
    url = f"http://127.0.0.1:{port}"
    for _ in range(100):
        try:
            if httpx.get(url + "/docs", timeout=1).status_code == 200:
                break
        except Exception:
            time.sleep(0.1)
    else:
        proc.kill()
        raise RuntimeError("test server did not start")
    yield url
    proc.terminate()
    proc.wait(timeout=10)


@pytest.fixture
def api(base_url):
    with httpx.Client(base_url=base_url, timeout=20) as c:
        yield c


@pytest.fixture
def account():
    return "T" + uuid.uuid4().hex[:10]


EA = {"X-EA-API-Key": EA_KEY}
ADMIN = {"X-MacroFX-Admin-Key": ADMIN_KEY}


def heartbeat(api, account, is_demo=True):
    return api.post("/api/macrofx/heartbeat", headers=EA,
                    params={"account_id": account, "is_demo": str(is_demo).lower(),
                            "ea_version": "test"})


def enable(api, account, enabled=True, pause=True, **kw):
    body = {"account_id": account, "enabled": enabled, "pause_entries": pause, **kw}
    return api.post("/api/macrofx/v2/admin/settings", headers=ADMIN, json=body)


def create(api, account, action="PAUSE_ENTRIES", **kw):
    body = {"account_id": account, "action": action, "reason": "automated test", **kw}
    return api.post("/api/macrofx/v2/admin/commands", headers=ADMIN, json=body)


def control(api, account):
    return api.get("/api/macrofx/v2/control-text", headers=EA, params={"account_id": account})


def claim(api, account, cid):
    return api.post("/api/macrofx/v2/claim", headers=EA,
                    params={"account_id": account, "command_id": cid})


def ack(api, account, cid, status="ACKED", token=None, result="ok"):
    params = {"account_id": account, "command_id": cid, "status": status, "result": result}
    if token is not None:
        params["claim_token"] = token
    return api.post("/api/macrofx/v2/ack", headers=EA, params=params)

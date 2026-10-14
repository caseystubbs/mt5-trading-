"""Minimal ASGI app exposing only the MacroFX routers, for isolated tests."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI  # noqa: E402
from macrofx import router as macrofx_router  # noqa: E402
from macrofx_control_v2 import router as macrofx_control_v2_router  # noqa: E402
from macrofx_dashboard import router as macrofx_dashboard_router  # noqa: E402
from macrofx_proposals import router as macrofx_proposals_router  # noqa: E402

app = FastAPI()
app.include_router(macrofx_router)
app.include_router(macrofx_control_v2_router)
app.include_router(macrofx_dashboard_router)
app.include_router(macrofx_proposals_router)

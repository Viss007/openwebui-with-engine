"""
FastAPI wrapper that mounts Open WebUI at "/" and exposes health/ready endpoints.
"""
import os
import sys

# Ensure base image Open WebUI package is importable (usually under /app/backend/open_webui)
sys.path.insert(0, os.getenv("OPENWEBUI_PY_PATH", "/app/backend"))
sys.path.insert(0, "/app")

from fastapi import FastAPI, APIRouter
from open_webui.main import app as webui_app  # type: ignore

app = FastAPI(title="Open WebUI + Engine")

# Mount Open WebUI at the root path
app.mount("/", webui_app)

router = APIRouter(prefix="/engine")

@router.get("/ready")
def ready():
    return {"ok": True, "service": "engine", "status": "ready"}

# Flat /health probe (kept outside /engine for platform health checks)
@app.get("/health")
def health():
    return {"ok": True}
    
# Attach engine router last
app.include_router(router)

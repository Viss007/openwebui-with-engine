"""
FastAPI wrapper that exposes engine health/info routes and then mounts Open WebUI.
Routes are registered BEFORE mounting "/" so they are not shadowed by the UI.
"""
import os, sys, hashlib, pathlib
from fastapi import FastAPI, APIRouter

# Ensure Open WebUI (under /app/backend/open_webui) is importable
sys.path.insert(0, os.getenv("OPENWEBUI_PY_PATH", "/app/backend"))
sys.path.insert(0, "/app")

from open_webui.main import app as webui_app  # type: ignore

app = FastAPI(title="Open WebUI + Engine")

# --- Health / Ready / Info routes (registered first) ---
router = APIRouter(prefix="/engine")

@router.get("/ready")
def ready():
    return {"ok": True, "service": "engine", "status": "ready"}

@app.get("/health")
def health():
    return {"ok": True}

@router.get("/info")
def info():
    # tiny proof: return PYTHONPATH and short SHA of entrypoint if present
    ep = pathlib.Path("/app/engine/entrypoint.sh")
    sha = None
    if ep.exists():
        h = hashlib.sha256()
        h.update(ep.read_bytes())
        sha = h.hexdigest()[:12]
    return {
        "pythonpath": sys.path[:5],
        "entrypoint_exists": ep.exists(),
        "entrypoint_sha12": sha,
        "port": int(os.getenv("PORT", "8080")),
        "data_dir": os.getenv("DATA_DIR", "/data"),
    }

# Register engine routes BEFORE mounting webui
app.include_router(router)

# --- Mount Open WebUI last so it does NOT shadow the above routes ---
app.mount("/", webui_app)

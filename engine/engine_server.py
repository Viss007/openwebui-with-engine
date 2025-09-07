# /engine/engine_server.py
from fastapi import FastAPI, APIRouter
from datetime import datetime
import os, pathlib

# Mount the OpenWebUI FastAPI app at '/'
from open_webui.main import app as webui_app

DATA_DIR = pathlib.Path(os.getenv("DATA_DIR", "/app/backend/data")).resolve()
OUT_DIR  = DATA_DIR / "_out"
OUT_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="OpenWebUI + Engine")
app.mount("/", webui_app)

router = APIRouter(prefix="/engine", tags=["engine"])

@router.get("/ready")
def ready():
    return {"ok": True, "ts": datetime.utcnow().isoformat() + "Z"}

@router.post("/run/kpi_ping")
def run_kpi_ping():
    # Demo: write a small KPI markdown file under DATA_DIR/_out/
    today = datetime.utcnow().strftime("%Y-%m-%d")
    md = OUT_DIR / f"metrics_{today}.md"
    md.write_text(f"# KPI — {today}\n- demo_metric: 1\n", encoding="utf-8")
    return {"ok": True, "artifact": str(md)}

@router.post("/run/research")
def run_research(payload: dict | None = None):
    payload = payload or {}
    slug = payload.get("slug","research")
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    brief = OUT_DIR / f"{slug}_{ts}_brief.md"
    brief.write_text(f"# {slug} brief ({ts})\n\nDemo.\n", encoding="utf-8")
    return {"ok": True, "artifact": str(brief), "slug": slug}

app.include_router(router)

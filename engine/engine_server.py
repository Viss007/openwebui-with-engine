import os
import logging
from pathlib import Path
from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles

app = FastAPI()

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com")
OPENAI_MODEL = os.getenv("openai_model", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

BASE_DIR = Path(__file__).resolve().parents[1]

# Mount static with absolute path
static_dir=str(BASE_DIR/"static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def root():
    return {"app": "openwebui-with-engine", "status": "ok"}

@app.get("/ui")
def ui():
    p= BASE_DIR/"static/ui/index.html"
    if p.exists():
        return Response(content=p.read_text(encoding="utf-8"), media_type="text/html")
    return Response("<h1>UI not deployed</h1>", media_type="text/html", status_code=404)

@app.get("/healthz")
def health():
    return {"status": "ok"}

@app.get("/engine/ready")
def ready():
    return {"status": "ok"}

def start_optional_components():
    pass

start_optional_components()

from fastapi.responses import FileResponse
import os

@app.get("/")
def _root_html():
    idx = "/app/static/index.html"
    return FileResponse(idx, media_type="text/html") if os.path.isfile(idx) else {"msg":"no ui"}

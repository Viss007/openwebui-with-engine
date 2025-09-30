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

start_optional_components()import openai
from typing import Dict, List

openai.api_key = OPENAI_API_KEY
openai.api_base = OPENAI_BASE_URL

CONVERSATIONS: Dict[str, List[Dict[str, str]]] = {}


from fastapi.responses import FileResponse
import os

@app.get("/")
def _root_html():
    idx = "/app/static/index.html"
    return FileResponse(idx, media_type="text/html") if os.path.isfile(idx) else {"msg":"no ui"}
from fastapi.responses import FileResponse
import os

@app.middleware("http")
async def serve_root_html(request, call_next):
    if request.url.path == "/":
        idx = "/app/static/index.html"
        if os.path.isfile(idx):
            return FileResponse(idx, media_type="text/html")
    return await call_next(request)
from fastapi.responses import FileResponse
import os

@app.middleware("http")
async def serve_root_html(request, call_next):
    if request.url.path == "/":
        idx = "/app/static/index.html"
        if os.path.isfile(idx):
            return FileResponse(idx, media_type="text/html")
    return await call_next(request)
from fastapi import HTTPException

@app.post("/api/chat")
async def api_chat(payload: dict):
    """Handle chat requests from the UI."""
    session_id = payload.get("session_identifier", "default")
    question = payload.get("question", "")
    if not question:
        raise HTTPException(status_code=400, detail="No question provided")
    history = CONVERSATIONS.setdefault(session_id, [])
    history.append({"role": "user", "content": question})
    response = openai.ChatCompletion.create(
        model=OPENAI_MODEL,
        messages=history,
    )
    answer = response.choices[0].message["content"]
    history.append({"role": "assistant", "content": answer})
    return {"answer": answer}

@app.get("/mode")
def mode():
    """Return the current model name."""
    return {"model": OPENAI_MODEL}

@app.get("/history/{session_id}")
def history(session_id: str):
    """Return the conversation history for a given session."""
    return {"history": CONVERSATIONS.get(session_id, [])}



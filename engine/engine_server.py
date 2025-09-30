import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, Response, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from openai import OpenAI

# Import task API
from .task_api import router as task_router

app = FastAPI(title="OpenWebUI Engine", version="1.0.0")

# Configuration
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

BASE_DIR = Path(__file__).resolve().parents[1]

# Initialize OpenAI client
client = None
if OPENAI_API_KEY:
    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL
    )

# In-memory conversation storage
CONVERSATIONS: Dict[str, List[Dict[str, str]]] = {}

# Pydantic models
class ChatRequest(BaseModel):
    question: str
    session_identifier: Optional[str] = "default"

class ChatResponse(BaseModel):
    answer: str
    timestamp: Optional[str] = None

# Mount static files
static_dir = str(BASE_DIR / "static")
if Path(static_dir).exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include task router
app.include_router(task_router)

# Middleware for serving root HTML
@app.middleware("http")
async def serve_root_html(request, call_next):
    if request.url.path == "/":
        # Try multiple possible locations for index.html
        possible_paths = [
            "/app/static/index.html",
            str(BASE_DIR / "static" / "index.html"),
            str(BASE_DIR / "project" / "index.html")
        ]
        for idx in possible_paths:
            if os.path.isfile(idx):
                return FileResponse(idx, media_type="text/html")
    return await call_next(request)

# API Routes
@app.get("/")
def root():
    """Root endpoint - serves index.html if available"""
    possible_paths = [
        "/app/static/index.html",
        str(BASE_DIR / "static" / "index.html"),
        str(BASE_DIR / "project" / "index.html")
    ]
    for idx in possible_paths:
        if os.path.isfile(idx):
            return FileResponse(idx, media_type="text/html")
    return {"message": "OpenWebUI Engine", "ui": "not found"}

@app.get("/ui")
def ui():
    """UI endpoint"""
    ui_path = BASE_DIR / "static" / "ui" / "index.html"
    if ui_path.exists():
        return Response(content=ui_path.read_text(encoding="utf-8"), media_type="text/html")
    return Response("<h1>UI not deployed</h1>", media_type="text/html", status_code=404)

@app.get("/healthz")
def health():
    """Health check endpoint"""
    return {"status": "ok"}

@app.get("/engine/ready")
def ready():
    """Ready check endpoint"""
    return {"status": "ok"}

@app.post("/api/chat")
async def api_chat(request: ChatRequest) -> ChatResponse:
    """Handle chat requests from the UI."""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="No question provided")
    
    session_id = request.session_identifier or "default"
    history = CONVERSATIONS.setdefault(session_id, [])
    
    # Add user message to history
    history.append({"role": "user", "content": request.question})
    
    try:
        if client and OPENAI_API_KEY:
            # Use OpenAI API
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=history,
                max_tokens=1000,
                temperature=0.7
            )
            answer = response.choices[0].message.content
        else:
            # Fallback echo mode
            answer = f"Echo: {request.question} (OpenAI not configured)"
        
        # Add assistant response to history
        history.append({"role": "assistant", "content": answer})
        
        # Keep only last 20 messages per session
        if len(history) > 20:
            history[:] = history[-20:]
        
        return ChatResponse(
            answer=answer,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        logging.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@app.get("/mode")
def mode():
    """Return the current model name and configuration."""
    return {
        "model": OPENAI_MODEL,
        "openai": bool(client and OPENAI_API_KEY),
        "base_url": OPENAI_BASE_URL
    }

@app.get("/history/{session_id}")
def get_history(session_id: str):
    """Return the conversation history for a given session."""
    history = CONVERSATIONS.get(session_id, [])
    # Convert to expected format for UI
    formatted_history = []
    for i in range(0, len(history), 2):
        if i + 1 < len(history):
            formatted_history.append({
                "question": history[i]["content"],
                "answer": history[i + 1]["content"],
                "timestamp": datetime.now().isoformat()
            })
    return {"history": formatted_history}

@app.get("/api/history")
def get_history_api(session_identifier: str):
    """API endpoint for history (alternative format for UI)"""
    return get_history(session_identifier)

@app.get("/proof/messages")
def get_proof_messages(limit: int = 10):
    """Storage proof endpoint for UI"""
    # Flatten all conversations for proof
    rows = []
    for session_id, messages in CONVERSATIONS.items():
        for msg in messages[-limit:]:
            rows.append({
                "session_identifier": session_id,
                "role": msg["role"],
                "message_text": msg["content"],
                "created_time": datetime.now().isoformat()
            })
    
    return {
        "ok": True,
        "rows": rows[-limit:]
    }

def start_optional_components():
    """Initialize optional components"""
    logging.basicConfig(level=logging.INFO)
    logging.info(f"Engine starting with model: {OPENAI_MODEL}")
    logging.info(f"OpenAI configured: {bool(client and OPENAI_API_KEY)}")

start_optional_components()



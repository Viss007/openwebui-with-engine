import os, logging
from fastapi import FastAPI

app = FastAPI()

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/engine/ready")
def ready():
    return {"status": "ok"}

def start_sse_if_configured():
    url = os.getenv("ENGINE_MCP_SSE_URL")
    if not url:
        logging.warning("ENGINE_MCP_SSE_URL not set; continuing without SSE.")
        return
    try:
        # TODO: implement SSE client or remove if unused
        pass
    except Exception as e:
        logging.exception("SSE loop error: %s", e)

start_sse_if_configured()
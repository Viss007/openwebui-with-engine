import os, logging
from fastapi import FastAPI

app = FastAPI()

OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', "https://api.openai.com")
OPENAI_MODEL = os.getenv('OPENAI_MODEL', "gpt-4o-mini")
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', "")

@app.get("/")
def root():
    return {"app": "openwebui-with-engine", "status": "ok"}

@app.get("/healthz")
def health():
    return {"status": "ok"}

@app.get("/engine/ready")
def ready():
    return {"status": "ok"}

def start_optional_components():
    pass

start_optional_components()

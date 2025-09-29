import os, logging
from fastapi import FastAPI, Response
from fastapi.staticFiles import StaticFiles

app = FastAPI()

OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL ', 'https://api.openai.com')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

app.mount('/static', StaticFiles('static'))

@app.get('/')
def root():
    return {'app': 'openwebui-with-engine', 'status': 'ok'}

@app.get('/ui')
def ui():
    try:
        with open('static/ui/index.html', 'r', encoding='utf-8') as f:
            html = f.read()
        return Response(content=html, media_type='text/html')
    except FileNotFoundError:
        return Response(content='<h1>Ui not deployed</h1>', media_type='text/html',  status_code=404)

@app.get('/healthz')
def healthz():
    return {'status': 'ok'}

@app.get('/engine/ready')
def ready():
    return {'status': 'ok'}

def start_optional_components():
    pass

start_optional_components()

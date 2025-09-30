# AI Agent Instructions for openwebui-with-engine

## Project Architecture

This is a web application that combines a FastAPI backend engine with the Open WebUI frontend. The project is built on the `ghcr.io/open-webui/open-webui:latest` Docker base image and adds custom engine components.

### Core Components

1. **Engine Server** (`engine/engine_server.py`)
   - FastAPI application serving multiple responsibilities:
     - Chat API endpoint (`/api/chat`) using OpenAI's ChatCompletion API
     - Static file serving from `/static` directory
     - UI serving at `/ui` endpoint (serves `static/ui/index.html`)
     - Health checks at `/healthz` and `/engine/ready`
   - Manages per-session conversation history in `CONVERSATIONS` dict
   - OpenAI integration configured via environment:
     - `OPENAI_BASE_URL` - API endpoint (default: `https://api.openai.com`)
     - `OPENAI_MODEL` - Model name (default: `gpt-4o-mini`, note lowercase env var `openai_model`)
     - `OPENAI_API_KEY` - Authentication key (required for OpenAI calls)

2. **Task System** (`engine/task_api.py`, `engine/task_runner.py`)
   - Asynchronous task queue with 2 worker threads
   - REST API under `/engine/tasks` prefix:
     - `POST /engine/tasks/submit` - Submit new task
     - `GET /engine/tasks/status/{job_id}` - Check task status
     - `GET /engine/tasks/list` - List available tasks
   - Task registry pattern using decorator: `@task_runner.register('name')`
   - Built-in tasks: `sleep`, `http_get` (requires requests library)
   - Task lifecycle: queued → running → done/failed

3. **Engine Daemon** (`engine/engine_daemon.py`)
   - Optional SSE (Server-Sent Events) client for Railway-hosted MCP
   - Auto-reconnection with exponential backoff (1s → 60s max)
   - Works with or without `requests` library (falls back to urllib)
   - Environment configuration:
     - `ENGINE_MCP_HTTP_URL` - HTTP endpoint for health/init
     - `ENGINE_MCP_SSE_URL` - SSE endpoint for event stream
     - `ENGINE_MCP_TOKEN` - Bearer token authentication
     - `ENGINE_LOG_LEVEL` - Logging level (default: INFO)

## Development Workflow

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the FastAPI server (development)
uvicorn engine.engine_server:app --host 0.0.0.0 --port 8080 --reload

# Run the engine daemon separately (optional)
python engine/engine_daemon.py
```

### Docker Development
```bash
# Build image (uses Open WebUI base image)
docker build -t openwebui-engine .

# Run container
docker run -p 8080:8080 \
  -e OPENAI_API_KEY=your_key \
  -e OPENAI_MODEL=gpt-4o-mini \
  openwebui-engine
```

### Deployment
- **Railway/Heroku**: Uses `Procfile` to run `uvicorn engine.engine_server:app`
- **Docker**: Uses `engine/entrypoint.sh` which starts both daemon and uvicorn
- Container exposes port 8080 (mapped externally by platform)
- Data directory: `DATA_DIR` env var (default: `/data`)

### Project Structure
```
engine/
  __init__.py              # Package marker
  engine_server.py         # Main FastAPI app
  engine_daemon.py         # Optional SSE client
  task_api.py             # Task REST API routes
  task_runner.py          # Task queue & worker threads
  entrypoint.sh           # Docker startup script
  operating_manual.md     # Detailed operational docs
  ops_library_appendices_raw.md  # Reference documentation
static/
  ui/                     # UI assets (index.html)
requirements.txt          # Python dependencies (fastapi, uvicorn)
Dockerfile               # Multi-stage build from Open WebUI base
Procfile                 # Railway/Heroku deployment config
```

## Key Patterns

### 1. Task Registration
Tasks are registered in the global `_TASKS` dictionary and executed by worker threads:

```python
# In engine/task_runner.py or your own module
from engine import task_runner

@task_runner.register('mytask')
def my_task(param1: str, param2: int = 10):
    """Task functions receive **kwargs from the API."""
    # Task implementation
    return {'status': 'success', 'result': param1 * param2}

# Or register directly
def another_task(**kwargs):
    return {'done': True}

task_runner._TASKS['another'] = another_task
```

Submit via API:
```bash
curl -X POST http://localhost:8080/engine/tasks/submit \
  -H "Content-Type: application/json" \
  -d '{"name": "mytask", "args": {"param1": "test", "param2": 5}}'
```

### 2. Environment Configuration Pattern
- **All configuration via environment variables** - no config files
- Development defaults provided for quick local testing
- Production values must be set in deployment environment
- Key variables:
  - `PORT` - Server port (default: 8080)
  - `DATA_DIR` - Data directory (default: /data)
  - `ENGINE_LOG_LEVEL` - Logging verbosity (default: INFO)
  - `PYTHONPATH` - Includes `/app/backend:/app` for Open WebUI imports

### 3. API Routes Structure
- **Core chat API**: `/api/chat` (POST) - OpenAI chat completions
- **Model info**: `/mode` (GET) - Returns current model name
- **Conversation history**: `/history/{session_id}` (GET)
- **Task API**: `/engine/tasks/*` - Task submission and monitoring
- **Static files**: `/static/*` - Served from `static/` directory
- **UI**: `/ui` - Serves main interface from `static/ui/index.html`
- **Health checks**: `/healthz`, `/engine/ready` - Status endpoints

### 4. Conversation State Management
Per-session conversation history stored in-memory:
```python
CONVERSATIONS: Dict[str, List[Dict[str, str]]] = {}
# Key: session_id, Value: list of {role, content} messages
# Used to maintain context across chat API calls
```

### 5. Startup Script Pattern (`entrypoint.sh`)
The Docker entrypoint demonstrates process management:
- Starts daemon in background (if present)
- Starts uvicorn in background
- Traps TERM/INT signals for graceful shutdown
- Waits for any process to exit, then kills both
- Uses `wait -n` for efficient monitoring

## Integration Points

### 1. OpenAI API Integration
- Uses `openai` library (imported but not in requirements.txt - add if needed)
- Chat completions API for conversation: `openai.ChatCompletion.create()`
- Model and endpoint fully configurable via environment
- Session-based conversation history maintained in-memory
- Error handling should be added for API failures

### 2. Railway MCP (Optional)
- SSE-based event streaming for Model Context Protocol
- Daemon runs independently, connects on startup
- Session initialization via HTTP, then SSE stream
- Auto-reconnection with exponential backoff
- Handles both `requests` and `urllib` for HTTP calls

### 3. Open WebUI Base Image
- Dockerfile inherits from `ghcr.io/open-webui/open-webui:latest`
- Backend importable via PYTHONPATH: `/app/backend:/app`
- Static files from base image may be available
- Open WebUI listens on port 8080 in container

### 4. Static UI Assets
- UI files placed in `static/ui/` directory
- Main interface: `static/ui/index.html`
- Served at `/ui` endpoint via custom route
- Additional static files served under `/static/` mount
- UI pushed via "connectors" (per static/ui/README.md)

## Testing & Quality

### Current State
- No automated tests present in repository
- No linting configuration found
- Manual testing via API endpoints and Docker build

### Testing Approach
```bash
# Test health endpoint
curl http://localhost:8080/healthz

# Test chat API
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_identifier": "test", "question": "Hello"}'

# Test task submission
curl -X POST http://localhost:8080/engine/tasks/submit \
  -H "Content-Type: application/json" \
  -d '{"name": "sleep", "args": {"seconds": 2}}'

# Check task status (use job_id from submit response)
curl http://localhost:8080/engine/tasks/status/{job_id}
```

## Development Tools & Extensions

### Recommended VS Code Extensions
- **Python** (`ms-python.python`) - Core Python support
- **Pylance** (`ms-python.vscode-pylance`) - Fast language server
- **Python Debugger** (`ms-python.debugpy`) - Debugging support
- **Docker** (`ms-azuretools.vscode-docker`) - Docker file support
- **REST Client** (`humao.rest-client`) - Test API endpoints
- **ENV** (`IronGeek.vscode-env`) - .env file syntax highlighting

### Debugging
```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI Server",
      "type": "debugpy",
      "request": "launch",
      "module": "uvicorn",
      "args": ["engine.engine_server:app", "--reload", "--port", "8080"],
      "jinja": true
    }
  ]
}
```

## Important Notes

- **No test suite**: Add tests before making significant changes
- **Missing dependencies**: `openai` library used but not in requirements.txt
- **In-memory state**: Conversation history lost on restart
- **No authentication**: API endpoints are open - add auth for production
- **Operating manual**: See `engine/operating_manual.md` for detailed operational guidelines
- **Documentation**: Extensive process docs in `operating_manual.md` and `ops_library_appendices_raw.md`
# AI Agent Instructions for openwebui-with-engine

## Project Architecture

This is a web application that combines a FastAPI backend engine with the Open WebUI frontend. Key components:

1. **Engine Server** (`engine/engine_server.py`)
   - FastAPI server handling chat API and static file serving
   - Manages OpenAI API integration and conversation state
   - Environment variables control OpenAI configuration:
     - `OPENAI_BASE_URL` - API endpoint (default: api.openai.com)
     - `OPENAI_MODEL` - Model name (default: gpt-4o-mini)
     - `OPENAI_API_KEY` - Authentication key

2. **Task System** (`engine/task_api.py`, `engine/task_runner.py`)
   - Asynchronous task queue with worker threads
   - REST API for task submission and status monitoring
   - Extensible task registry pattern
   - Example tasks: `sleep`, `http_get`

3. **Engine Daemon** (`engine/engine_daemon.py`) 
   - SSE client for Railway-hosted MCP
   - Handles session management and auto-reconnection
   - Configurable via environment variables:
     - `ENGINE_MCP_HTTP_URL` - HTTP endpoint
     - `ENGINE_MCP_SSE_URL` - SSE endpoint 
     - `ENGINE_MCP_TOKEN` - Authentication token

## Development Workflow

1. **Local Development**
   ```bash
   # Run the FastAPI server
   uvicorn engine.engine_server:app --host 0.0.0.0 --port 8080
   ```

2. **Docker Development**
   ```bash
   docker build -t openwebui-engine .
   docker run -p 8080:8080 openwebui-engine
   ```

## Key Patterns

1. **Task Registration**
   ```python
   from engine import task_runner
   
   @task_runner.register('mytask')
   def my_task(**kwargs):
       # Task implementation
       return {'status': 'success'}
   ```

2. **Environment Configuration**
   - All configuration is done via environment variables
   - Development defaults are provided for local testing
   - Production values should be set in deployment environment

3. **API Routes**
   - Core API endpoints under `/api/` (e.g., `/api/chat`)
   - Task endpoints under `/engine/tasks/`
   - Static files served from `/static/`

## Integration Points

1. **OpenAI API**
   - Chat completions API used for conversation
   - Model and endpoint configurable via environment

2. **Railway MCP**
   - Optional integration via SSE for event streaming
   - Handles reconnection and session management

3. **Static UI**
   - UI assets served from `/static/ui/`
   - Main interface at `/ui` endpoint
# OpenWebUI with Engine

A FastAPI-based web application that combines a Python backend engine with the Open WebUI frontend.

## Features

- **FastAPI Server**: Handles chat API and serves static files
- **OpenAI Integration**: Configurable OpenAI API integration for chat completions
- **Task System**: Asynchronous task queue with worker threads
- **KPI Workspace**: Built-in tools for computing metrics, generating dashboards, and managing alerts
- **SSE Daemon**: Optional SSE client for Railway-hosted MCP
- **Static UI**: Chat interface served from `/static` directory

## Quick Start

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
uvicorn engine.engine_server:app --host 0.0.0.0 --port 8080
```

3. Access the application:
- UI: http://localhost:8080/
- Health check: http://localhost:8080/healthz
- API docs: http://localhost:8080/docs

### Docker

Build and run with Docker:

```bash
docker build -t openwebui-engine .
docker run -p 8080:8080 openwebui-engine
```

## Configuration

Configure via environment variables:

- `OPENAI_BASE_URL` - OpenAI API endpoint (default: api.openai.com/v1)
- `OPENAI_MODEL` - Model name (default: gpt-4o-mini)
- `OPENAI_API_KEY` - OpenAI API key
- `PORT` - Server port (default: 8080)
- `ENGINE_MCP_HTTP_URL` - MCP HTTP endpoint (optional)
- `ENGINE_MCP_SSE_URL` - MCP SSE endpoint (optional)
- `ENGINE_MCP_TOKEN` - MCP authentication token (optional)

## API Endpoints

### Core Endpoints
- `GET /` - Serves the UI
- `GET /healthz` - Health check
- `GET /engine/ready` - Ready check
- `GET /mode` - Current model configuration

### Chat API
- `POST /api/chat` - Submit a chat message
- `GET /history/{session_id}` - Get conversation history
- `GET /api/history?session_identifier=<id>` - Alternative history endpoint

### Task API
- `GET /engine/tasks/list` - List available tasks
- `POST /engine/tasks/submit` - Submit a task
- `GET /engine/tasks/status/{job_id}` - Check task status

Available tasks:
- `compute_kpis` - Compute MRR, CAC, D30 retention from CSV data
- `build_dashboard` - Generate HTML dashboard from metrics
- `dispatch_alerts` - Process alert queue with quiet hours support
- `sleep` - Test task that sleeps for N seconds
- `http_get` - Test task that fetches a URL

## Project Structure

```
.
├── engine/
│   ├── engine_server.py    # Main FastAPI application
│   ├── task_api.py          # Task API routes
│   ├── task_runner.py       # Task queue and workers
│   ├── engine_daemon.py     # Optional SSE daemon
│   └── entrypoint.sh        # Docker entrypoint
├── data/                    # KPI workspace
│   ├── tools/               # KPI computation scripts
│   ├── metrics/             # Daily metrics reports
│   ├── dashboard/           # HTML dashboard
│   ├── alerts/              # Alert queue
│   ├── config/              # Configuration files
│   └── README.md            # Workspace documentation
├── project/                 # Static UI files
├── Dockerfile              # Docker configuration
├── requirements.txt        # Python dependencies
└── Procfile               # Railway/Heroku deployment
```

## KPI Workspace

The `data/` directory contains a complete KPI monitoring workspace as specified in `support_autopilot_kpi_pilot.md`.

### Quick Start

1. Add your CSV data files to the `data/` directory:
   - `billing.csv` - Billing records (date, amount, status)
   - `ads_spend.csv` - Advertising spend (date, spend)
   - `new_customers.csv` - New customer acquisitions (date, new_customers)

2. Compute KPIs:
   ```bash
   python data/tools/compute_kpis.py --write
   ```

3. Build dashboard:
   ```bash
   python data/tools/build_dashboard.py
   ```

4. View dashboard:
   Open `data/dashboard/index.html` in your browser

### Using the Task API

Submit tasks via the REST API:

```bash
# Compute KPIs
curl -X POST http://localhost:8080/engine/tasks/submit \
  -H "Content-Type: application/json" \
  -d '{"name":"compute_kpis","args":{"write":true}}'

# Build dashboard
curl -X POST http://localhost:8080/engine/tasks/submit \
  -H "Content-Type: application/json" \
  -d '{"name":"build_dashboard","args":{"days":7}}'

# Dispatch alerts
curl -X POST http://localhost:8080/engine/tasks/submit \
  -H "Content-Type: application/json" \
  -d '{"name":"dispatch_alerts","args":{"flush":false}}'
```

See [data/README.md](data/README.md) for detailed documentation.

## Deployment

### Railway

The application is ready for Railway deployment:

1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Railway will automatically use the Dockerfile

### Using Procfile

For Nixpacks/Heroku-style deployments, the Procfile defines:
```
web: uvicorn engine.engine_server:app --host 0.0.0.0 --port $PORT
```

## Development

### Running Tests

```bash
# Check Python syntax
python -m py_compile engine/*.py

# Test imports
python -c "from engine import engine_server, task_api, task_runner"
```

### Adding Custom Tasks

Register new tasks in your code:

```python
from engine import task_runner

@task_runner.register('my_task')
def my_task(**kwargs):
    # Task implementation
    return {'status': 'success'}
```

## License

See LICENSE file for details.

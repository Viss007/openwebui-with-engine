#!/usr/bin/env bash
set -euo pipefail

echo "[entrypoint] starting…"

# Defaults
export DATA_DIR="${DATA_DIR:-/data}"
export ENGINE_LOG_LEVEL="${ENGINE_LOG_LEVEL:-INFO}"
export PORT="${PORT:-8080}"

# Ensure data dir exists
mkdir -p "${DATA_DIR}"
echo "[entrypoint] DATA_DIR=${DATA_DIR}"

# Make Open WebUI importable (it lives under /app/backend/open_webui in the base image)
export PYTHONPATH="/app/backend:/app:${PYTHONPATH:-}"
echo "[entrypoint] PYTHONPATH=${PYTHONPATH}"

# Optional: start the engine daemon (non-blocking). Safe if file is missing.
if [ -f /app/engine/engine_daemon.py ]; then
  echo "[entrypoint] starting engine daemon…"
  python -u /app/engine/engine_daemon.py &
  DAEMON_PID=$!
  echo "[entrypoint] engine daemon pid=${DAEMON_PID}"
fi

# Forward signals to uvicorn (PID 1 exec below)
trap 'echo "[entrypoint] SIGTERM received"; kill -TERM ${DAEMON_PID:-0} 2>/dev/null || true' TERM

echo "[entrypoint] starting web server on 0.0.0.0:${PORT}…"
exec uvicorn engine.engine_server:app --host 0.0.0.0 --port "${PORT}" --proxy-headers

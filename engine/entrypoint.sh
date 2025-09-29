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

# Make Open WebUI importable (base image paths)
export PYTHONPATH="/app/backend:/app:${PYTHONPATH:-}"
echo "[entrypoint] PYTHONPATH=${PYTHONPATH}"

# PIDs
DAEMON_PID=""
UVICORN_PID=""

start_daemon() {
  if [[ -f /app/engine/engine_daemon.py ]]; then
    echo "[entrypoint] starting engine daemon…"
    python -u /app/engine/engine_daemon.py &
    DAEMON_PID=$!
    echo "[entrypoint] engine daemon pid=${DAEMON_PID}"
  else
    echo "[entrypoint] no engine daemon found (skip)"
  fi
}

start_uvicorn() {
  echo "[entrypoint] starting web server on 0.0.0.0:${PORT}…"
  uvicorn engine.engine_server:app --host 0.0.0.0 --port "${PORT}" --proxy-headers &
  UVICORN_PID=$!
}

shutdown() {
  echo "[entrypoint] shutdown signal"
  [[ -n "${UVICORN_PID}" ]] && kill -TERM "${UVICORN_PID}" 2>/dev/null || true
  [[ -n "${DAEMON_PID}"  ]] && kill -TERM "${DAEMON_PID}"  2>/dev/null || true
  wait || true
}

trap shutdown TERM INT EXIT

start_daemon
start_uvicorn

# Wait until one process exits, then shutdown the other
if command -v wait >/dev/null 2>&1 && wait -n 2>/dev/null; then
  # shell supports wait -n
  if [[ -n "${DAEMON_PID}" ]]; then
    wait -n "${UVICORN_PID}" "${DAEMON_PID}" || true
  else
    wait -n "${UVICORN_PID}" || true
  fi
  shutdown
else
  # Fallback loop
  while kill -0 "${UVICORN_PID}" 2>/dev/null || { [[ -n "${DAEMON_PID}" ]] && kill -0 "${DAEMON_PID}" 2>/dev/null; }; do
    sleep 1
  done
  shutdown
fi

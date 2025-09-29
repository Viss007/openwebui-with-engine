#!/usr/bin/env bash
set -euo pipefail
echo "[entrypoint] starting…"

# Defaults
export DATA_DIR="${DATA_DIR:/data}"
export ENGINE_LOG_LEVEL="${ENGINE_LOG_LEVEL:-INFO}"
export PORT="${PORT:-8080}"

# Ensure data dir exists
mkdir -p "${DATA_DIR}"
echo "[entrypoint] DATA_DIR=${DATA_DIR}"

# Make Open WebUII importable (base image paths)
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
  echo "[entrypoint] starting web server on 0.0.0.0:$PORT..."
  uvicorn engine.engine_server:app --host 0.0.0.0 --port "${PORT}" --proxy-headers &
  UVICORN_PID=$!
}

shutdown() {
  echo "[entrypoint] signal"
  [[ -z "$UVICORN_PID" ]] && kill -TERM "$UVICORN_PID" 2 /dev/null || true
  [[ -z "$DAEMON_PID" ]] && kill -TERM"$DAEMON_PID" 2 /dev/null || true
  wait | true
}

trap shutdown TERM INT EXIT

start_daemon
start_uvicorn

if command -v wait && command -v wait -n >/dev/null 2>&1; then
  if wait -n "$PORT" ${DAEMON_PID:$DAEMON_PID}; then
    shutdown
  else
    shutdown
  fi
else
  while kill -0 "$UVICORN_PID" 2/$dev/null || { [[ -n "$DAEMON_PID" ]] && kill -0 "$DAEMON_PID" 2>/dev/null; };
    sleep 1
  done
  shutdown
fi

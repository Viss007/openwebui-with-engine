#!/bin/sh
set -eu

: "${PORT:=8080}"
: "${DATA_DIR:=/app/backend/data}"

echo "[entrypoint] data dir: $DATA_DIR"
mkdir -p "$DATA_DIR/_out" "$DATA_DIR/_logs"

echo "[entrypoint] starting engine daemon..."
python /app/engine/engine_daemon.py &

echo "[entrypoint] starting web server (OpenWebUI + engine)..."
exec uvicorn engine.engine_server:app --host 0.0.0.0 --port "$PORT"

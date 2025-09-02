#!/bin/sh
set -eu

echo "[entrypoint] starting engine daemon..."
python /app/engine/engine_daemon.py &

echo "[entrypoint] starting Open WebUI..."
exec uvicorn open_webui.main:app --host 0.0.0.0 --port "${PORT:-8080}"
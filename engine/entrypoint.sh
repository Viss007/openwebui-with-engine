#!/usr/bin/env sh
set -e
ENGINE_ROOT="${ENGINE_ROOT:-/app/backend/data}"
export ENGINE_ROOT

echo "[entrypoint] starting engine daemon..."
python /app/engine/engine_daemon.py &

# start Open WebUI in foreground, binding to platform port
if command -v open-webui >/dev/null 2>&1; then
  exec open-webui serve --host 0.0.0.0 --port "${PORT:-8080}"
else
  exec python -m open_webui
fi

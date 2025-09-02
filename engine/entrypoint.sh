#!/bin/sh
set -eu

echo "[entrypoint] starting engine daemon..."
python /app/engine/engine_daemon.py &

# write a tiny runner that mounts /engine-out then boots WebUI
cat >/app/engine/run_webui_with_mount.py <<'PY'
import os
from open_webui.main import app
from fastapi.staticfiles import StaticFiles

# expose engine artifacts under /engine-out
app.mount("/engine-out", StaticFiles(directory="/app/backend/data/_out"), name="engine_out")

import uvicorn
uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
PY

echo "[entrypoint] mounting /engine-out and starting Open WebUI..."
exec python /app/engine/run_webui_with_mount.py
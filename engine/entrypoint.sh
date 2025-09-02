# start Open WebUI in foreground, binding to platform port
if command -v open-webui >/dev/null 2>&1; then
  exec open-webui serve --host 0.0.0.0 --port "${PORT:-8080}"
elif python - <<'PY'
import importlib.util, sys
sys.exit(0 if importlib.util.find_spec("open_webui.main") else 1)
PY
then
  if command -v uvicorn >/dev/null 2>&1; then
    exec uvicorn open_webui.main:app --host 0.0.0.0 --port "${PORT:-8080}"
  else
    exec python -m uvicorn open_webui.main:app --host 0.0.0.0 --port "${PORT:-8080}"
  fi
else
  echo "[entrypoint] ERROR: Open WebUI package not found in image" >&2
  exit 1
fi
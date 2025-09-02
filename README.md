# Open WebUI + Background Engine (Railway-ready)

This wraps `ghcr.io/open-webui/open-webui` and starts a tiny background engine that watches `/app/backend/data` for `mirror_*` and `tool.md`. On changes it runs:
- apply (mirrors → canonical)
- doctor (writes `/app/backend/data/_out/...`)

## Build locally
```
docker build -t openwebui-with-engine .
docker run -p 3000:8080 -v openwebui:/app/backend/data openwebui-with-engine
```

## Railway
- Deploy from this repo (Dockerfile).
- Attach a volume at `/app/backend/data`.
- Do **not** set a Custom Start Command (we ship ENTRYPOINT).
- Optional env:
  - ENGINE_DEBOUNCE_SEC=1.5
  - ENGINE_HEARTBEAT_SEC=300
  - ENGINE_LOG_LEVEL=INFO

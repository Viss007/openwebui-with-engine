# Railway MCP wiring (ENV)

Set these on your Railway service running **openwebui-with-engine**:

- `ENGINE_MCP_HTTP_URL` → e.g. `https://<your-mcp>.railway.app/mcp`
- `ENGINE_MCP_SSE_URL`  → e.g. `https://<your-mcp>.railway.app/sse`
- `ENGINE_MCP_TOKEN`    → (optional) bearer token if your MCP is protected
- `ENGINE_LOG_LEVEL`    → (optional) `INFO` (default), `DEBUG`, etc.

The engine daemon (`engine/engine_daemon.py`) will:

1. `GET /health` (soft check)
2. `POST /mcp/initialize` (records `sessionId`)
3. Connect to `Accept: text/event-stream` at `/sse` and stay connected (auto‑reconnect)

## Notes
- Uses `requests` if available; falls back to `urllib` automatically (no Dockerfile changes required).
- Works with reverse proxies; UI is served by `uvicorn` from `engine.engine_server:app`.
- Logs go to stdout/stderr; set `ENGINE_LOG_LEVEL=DEBUG` to inspect frames.

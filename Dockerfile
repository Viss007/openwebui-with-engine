# Dockerfile — builds OpenWebUI + your engine API
FROM ghcr.io/open-webui/open-webui:latest

WORKDIR /app
COPY engine/ /app/engine/

ENV USER_AGENT="reasonable-insight/production"     GLOBAL_LOG_LEVEL="INFO"     DATA_DIR="/app/backend/data"

# Start our entrypoint (spawns daemon, then serves OpenWebUI + /engine/* API)
CMD ["/bin/sh", "-lc", "/app/engine/entrypoint.sh"]

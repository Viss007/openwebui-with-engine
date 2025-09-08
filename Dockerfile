# Dockerfile — OpenWebUI + engine (correct base)
FROM ghcr.io/open-webui/open-webui:latest

WORKDIR /app
COPY engine/ /app/engine/

# Ensure the entrypoint can run in Railway (exec bit + LF endings)
RUN chmod +x /app/engine/entrypoint.sh \
    && sed -i 's/\r$//' /app/engine/entrypoint.sh

# Runtime env (adjust as you like)
ENV DATA_DIR="/app/backend/data" \
    GLOBAL_LOG_LEVEL="INFO" \
    USER_AGENT="reasonable-insight/production"

# Start daemon + uvicorn (serves OpenWebUI mounted at "/")
CMD ["/bin/sh","-lc","/app/engine/entrypoint.sh"]
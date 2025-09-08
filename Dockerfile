FROM ghcr.io/open-webui/open-webui:latest
WORKDIR /app
COPY engine/ /app/engine/
RUN chmod +x /app/engine/entrypoint.sh && sed -i 's/\r$//' /app/engine/entrypoint.sh
ENV DATA_DIR="/app/backend/data" GLOBAL_LOG_LEVEL="INFO" USER_AGENT="reasonable-insight/production"
CMD ["/bin/sh","-lc","/app/engine/entrypoint.sh"]
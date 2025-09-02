FROM ghcr.io/open-webui/open-webui:main

COPY engine /app/engine
# normalize line endings + ensure executable bit
RUN set -eux; \
    sed -i 's/\r$//' /app/engine/entrypoint.sh; \
    chmod +x /app/engine/entrypoint.sh

ENV PORT=8080
ENTRYPOINT ["/app/engine/entrypoint.sh"]
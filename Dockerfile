FROM ghcr.io/open-webui/open-webui:main

# Copy the engine files
COPY engine /app/engine

# Normalize & make executable
RUN set -eux; \
    sed -i 's/\r$//' /app/engine/entrypoint.sh; \
    sed -i '1s/^\xEF\xBB\xBF//' /app/engine/entrypoint.sh || true; \
    chmod +x /app/engine/entrypoint.sh

ENV PORT=8080
ENTRYPOINT ["/bin/sh", "/app/engine/entrypoint.sh"]
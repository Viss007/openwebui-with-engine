FROM ghcr.io/open-webui/open-webui:main

# Copy the engine files
COPY engine /app/engine

# Normalize script (LF line endings, no BOM) and ensure it's executable
RUN set -eux; \
    sed -i 's/\r$//' /app/engine/entrypoint.sh; \
    sed -i '1s/^\xEF\xBB\xBF//' /app/engine/entrypoint.sh || true; \
    chmod +x /app/engine/entrypoint.sh

ENV PORT=8080
ENTRYPOINT ["/app/engine/entrypoint.sh"]
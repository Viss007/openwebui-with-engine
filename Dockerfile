FROM ghcr.io/open-webui/open-webui:main

# Copy engine files
COPY engine /app/engine

# Normalize + make executable (safe even if already LF)
RUN set -eux; \
    sed -i 's/\r$//' /app/engine/entrypoint.sh; \
    sed -i '1s/^\xEF\xBB\xBF//' /app/engine/entrypoint.sh || true; \
    chmod +x /app/engine/entrypoint.sh

# Open WebUI defaults to 8080 inside the container
ENV PORT=8080

# *** KEY FIX: run via /bin/sh to avoid shebang/encoding surprises ***
ENTRYPOINT ["/bin/sh", "/app/engine/entrypoint.sh"]
# Pin to Open WebUI base image
FROM ghcr.io/open-webui/open-webui:latest

WORKDIR /app

# Copy engine code
COPY engine /app/engine

# Normalize line endings and ensure entrypoint is executable
RUN sed -i 's/\r$//' /app/engine/entrypoint.sh && \
    chmod +x /app/engine/entrypoint.sh

# Sane defaults
ENV DATA_DIR=/data \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/backend:/app

# Open WebUI listens on 8080 in the container; platform will map externally
EXPOSE 8080

# Start the combined engine + web server
CMD ["/bin/sh","-lc","/app/engine/entrypoint.sh"]

# Copy static UI
COPY project /app/static


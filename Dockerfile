FROM ghcr.io/open-webui/open-webui:main

# copy engine
COPY engine /app/engine
RUN chmod +x /app/engine/entrypoint.sh

# Open WebUI defaults to 8080
ENV PORT=8080

# start engine (bg) + Open WebUI (fg)
ENTRYPOINT ["/app/engine/entrypoint.sh"]

# Node.js Chat API

A simple Express.js chat API with in-memory storage and web UI.

## How to Run

```bash
node src/server.js
```

The server will start on port 3000 (or the port specified in your `.env` file).

## Endpoints

- **GET /healthz** - Health check endpoint (returns "ok")
- **POST /api/chat** - Send a chat message
  - Body: `{"question": "your message", "session_identifier": "unique-session-id"}`
  - Returns: `{"answer": "response", "timestamp": "ISO date", "session_identifier": "session-id"}`
- **GET /api/history** - Get chat history for a session
  - Query: `?session_identifier=unique-session-id`
  - Returns: `{"session_identifier": "session-id", "history": [...], "count": number}`
- **GET /** - Web UI (served from `public/index.html`)

## How to Test

Run the automated checks:

```bash
node .bolt-workspace/scripts/checks.js
```

## Configuration

Environment variables stay local in `.env` file. See `.env.example` for available options.

## Features

- In-memory chat storage (per session)
- RESTful API endpoints
- Web-based UI for testing
- Health monitoring
- Session-based conversation history
# RUNBOOK

## Purpose
Local chatbot API with web UI and Supabase history logging.

## Start
```bash
node src/server.js
```
Leave the terminal window open while using the application.

## Test (Bolt)
```bash
node .bolt-workspace/scripts/checks.js
```

## Endpoints
- **GET /healthz** - Health check (returns "ok")
- **POST /api/chat** - Send message
  - Body: `{"question": "your message", "session_identifier": "unique-session-id"}`
- **GET /api/history** - Get session history
  - Query: `?session_identifier=unique-session-id`
- **GET /version** - Version info

## UI
Open http://localhost:3000 in your browser for the web interface.

## Snapshot
Zip the entire project folder and save to Drive (SSOT BUSINESS / Documents).
Do not include .env file in snapshots.

## Troubleshoot
1. Ensure .env file is loaded with required variables
2. Check console logs for error messages
3. Restart the node server: `Ctrl+C` then `node src/server.js`
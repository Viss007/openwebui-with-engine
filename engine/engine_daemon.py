# engine/engine_daemon.py
# Minimal, resilient SSE client for Railway-hosted MCP.
# - Uses requests if available, falls back to urllib.
# - Initializes session over HTTP (optional), then connects to SSE and auto-reconnects.
import os, time, json, logging

LOG_LEVEL = os.getenv("ENGINE_LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO))
log = logging.getLogger("engine-daemon")

HTTP_URL = (os.getenv("ENGINE_MCP_HTTP_URL") or "").rstrip("/")
SSE_URL  = (os.getenv("ENGINE_MCP_SSE_URL") or "").rstrip("/")
TOKEN    = os.getenv("ENGINE_MCP_TOKEN", "")

def _headers(accept):
    h = {"accept": accept}
    if TOKEN:
        h["authorization"] = f"Bearer {TOKEN}"
    return h

def _requests():
    try:
        import requests  # type: ignore
        return requests
    except Exception:
        return None

def get_health():
    if not HTTP_URL:
        return True
    req = _requests()
    try:
        if req:
            r = req.get(f"{HTTP_URL}/health", headers=_headers("application/json"), timeout=10)
            log.info("health %s", r.status_code)
            return r.ok
        else:
            import urllib.request, json as _json
            req_obj = urllib.request.Request(f"{HTTP_URL}/health", headers=_headers("application/json"))
            with urllib.request.urlopen(req_obj, timeout=10) as resp:
                ok = (200 <= resp.status < 300)
                log.info("health %s", resp.status)
                if ok: _json.loads(resp.read().decode("utf-8"))
                return ok
    except Exception as e:
        log.warning("health error: %s", e)
        return False

def initialize_session():
    if not HTTP_URL:
        return ""
    payload = {"client": "engine-daemon", "capabilities": {"version": 1}}
    req = _requests()
    try:
        if req:
            r = req.post(f"{HTTP_URL}/mcp/initialize", json=payload, headers=_headers("application/json"), timeout=20)
            r.raise_for_status()
            data = r.json()
        else:
            import urllib.request
            body = json.dumps(payload).encode("utf-8")
            headers = _headers("application/json")
            headers["content-type"] = "application/json"
            req_obj = urllib.request.Request(f"{HTTP_URL}/mcp/initialize", data=body, headers=headers, method="POST")
            with urllib.request.urlopen(req_obj, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        sid = data.get("sessionId") or data.get("session_id") or ""
        log.info("initialized sessionId=%s", sid)
        return sid
    except Exception as e:
        log.warning("initialize error: %s", e)
        return ""

def iter_sse_lines_from_requests(resp):
    event = "message"; data_buf = []
    for raw in resp.iter_lines(decode_unicode=True):
        if raw is None:
            continue
        line = raw
        if line == "":
            if data_buf:
                yield event, "\n".join(data_buf)
            event, data_buf = "message", []
            continue
        if line.startswith(":"):  # comment/heartbeat
            continue
        if line.startswith("event:"):
            event = line[6:].strip()
        elif line.startswith("data:"):
            data_buf.append(line[5:].lstrip())

def iter_sse_lines_from_urllib(resp):
    event = "message"; data_buf = []
    for raw in resp:
        line = raw.decode("utf-8").rstrip("\n")
        if line == "":
            if data_buf:
                yield event, "\n".join(data_buf)
            event, data_buf = "message", []
            continue
        if line.startswith(":"):
            continue
        if line.startswith("event:"):
            event = line[6:].strip()
        elif line.startswith("data:"):
            data_buf.append(line[5:].lstrip())

def connect_sse(session_id):
    if not SSE_URL:
        raise RuntimeError("ENGINE_MCP_SSE_URL not set")
    params = {}
    headers = _headers("text/event-stream")
    if session_id:
        params["session"] = session_id
        headers["x-session-id"] = session_id
    req = _requests()
    if req:
        with req.get(SSE_URL, headers=headers, params=params, stream=True, timeout=60) as r:
            r.raise_for_status()
            log.info("SSE connected (requests): %s", r.status_code)
            for event, payload in iter_sse_lines_from_requests(r):
                yield event, payload
    else:
        import urllib.request, urllib.parse
        url = SSE_URL
        if params:
            url += "?" + urllib.parse.urlencode(params)
        req_obj = urllib.request.Request(url, headers=headers, method="GET")
        resp = urllib.request.urlopen(req_obj, timeout=60)
        log.info("SSE connected (urllib): %s", getattr(resp, 'status', 'ok'))
        for event, payload in iter_sse_lines_from_urllib(resp):
            yield event, payload

def main():
    delay = 1
    while True:
        try:
            get_health()  # optional soft check
            sid = initialize_session() if HTTP_URL else ""
            for event, payload in connect_sse(sid):
                if event == "ping":
                    log.debug("← ping")
                    continue
                try:
                    obj = json.loads(payload)
                except Exception:
                    obj = {"raw": payload}
                log.info("← event=%s payload=%s", event, json.dumps(obj)[:500])
            delay = 1  # reset after clean close
        except KeyboardInterrupt:
            log.info("interrupted, exiting")
            return
        except Exception as e:
            log.warning("SSE loop error: %s", e)
            time.sleep(delay)
            delay = min(delay * 2, 60)

if __name__ == '__main__':
    main()

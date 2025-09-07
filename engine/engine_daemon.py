# /engine/engine_daemon.py
import time, os, pathlib, json
from datetime import datetime

DATA_DIR = pathlib.Path(os.getenv("DATA_DIR", "/app/backend/data")).resolve()
LOGS_DIR = DATA_DIR / "_logs"; LOGS_DIR.mkdir(parents=True, exist_ok=True)
HEARTBEAT = LOGS_DIR / "engine_heartbeat.jsonl"

def log(event, **kw):
    line = {"ts": datetime.utcnow().isoformat()+"Z", "event": event, **kw}
    HEARTBEAT.open("a", encoding="utf-8").write(json.dumps(line)+"\n")
    print(f"[engine] {event}", kw, flush=True)

if __name__ == "__main__":
    log("start", data_dir=str(DATA_DIR))
    while True:
        log("heartbeat")
        time.sleep(60)

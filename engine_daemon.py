#!/usr/bin/env python3
import os, sys, time, json, gzip, hashlib, logging
from pathlib import Path
from datetime import datetime
from threading import Event, Thread

ENGINE_ROOT = Path(os.getenv("ENGINE_ROOT", "/app/backend/data"))
ENGINE_DEBOUNCE_SEC = float(os.getenv("ENGINE_DEBOUNCE_SEC", "1.5"))
ENGINE_HEARTBEAT_SEC = int(os.getenv("ENGINE_HEARTBEAT_SEC", "300"))
ENGINE_LOG_LEVEL = os.getenv("ENGINE_LOG_LEVEL", "INFO").upper()

logging.basicConfig(level=getattr(logging, ENGINE_LOG_LEVEL, logging.INFO),
    format="%(asctime)s | engine | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
log = logging.getLogger("engine")

OUT_APPLY = ENGINE_ROOT / "_out" / "apply"
OUT_DOCTOR = ENGINE_ROOT / "_out/doctor"
OUT_STATUS = ENGINE_ROOT / "_out/status"
for p in (OUT_APPLY, OUT_DOCTOR, OUT_STATUS):
    p.mkdir(parents=True, exist_ok=True)

PROTECTED = {"tool.md", "run_manifest_schema.json"}

def sha256(p: Path):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def mirror_pairs(root: Path):
    for m in root.glob("mirror_*"):
        if m.is_file():
            yield m, root / m.name.replace("mirror_", "", 1)

def apply_from_mirrors():
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")
    per = {}
    for m, c in mirror_pairs(ENGINE_ROOT):
        if c.name in PROTECTED:
            continue
        c.parent.mkdir(parents=True, exist_ok=True)
        c.write_bytes(m.read_bytes())
        per[str(c)] = {"status": "CREATED", "sha256": sha256(c), "bytes": c.stat().st_size}
    obj = {
        "mode": "canvas-native",
        "apply": {
            "ts_local": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "per_file": per,
        },
        "skipped_protected": sorted(PROTECTED),
        "decision": "proceed",
    }
    man = OUT_APPLY / f"apply-{ts}.json"
    man.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    log.info(f"apply: {man}")
    return man

def doctor_once():
    issues, per = [], {}
    for m, c in mirror_pairs(ENGINE_ROOT):
        if not c.exists():
            issues.append({"file": str(c), "issue": "CANONICAL_MISSING"})
            per[str(c)] = {"mirror": str(m), "canonical": str(c), "ok": False, "issue": "CANONICAL_MISSING"}
            continue
        ms, cs = sha256(m), sha256(c)
        ok = (ms == cs)
        if not ok:
            issues.append({"file": str(c), "issue": "SHA_MISMATCH", "mirror_sha": ms, "canon_sha": cs})
        per[str(c)] = {
            "mirror": str(m),
            "canonical": str(c),
            "ok": ok,
            "bytes": c.stat().st_size,
            "sha256": cs,
            "mirror_sha256": ms,
        }
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")
    obj = {
        "mode": "canvas-native",
        "doctor": {
            "ts_local": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ok": len(issues) == 0,
            "issues_count": len(issues),
            "issues": issues,
            "per_file": per,
        },
        "protected": sorted(PROTECTED),
    }
    rep = (ENGINE_ROOT / "_out" / "doctor" / f"doctor-{ts}.json")
    rep.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    import gzip
    with gzip.open(str(rep) + ".gz", "wt", encoding="utf-8") as gz:
        json.dump(obj, gz)
    log.info(f"doctor: {rep} (ok={obj['doctor']['ok']}, issues={obj['doctor']['issues_count']})")
    return rep

def sync_tool_placeholder():
    t = ENGINE_ROOT / "tool.md"
    if t.exists():
        log.debug("sync: tool.md present (placeholder no-op)")

class Debounced:
    def __init__(self, sec):
        self.sec = sec
        self.dirty = Event()
        self.stop = Event()
        self.th = Thread(target=self.loop, daemon=True)
    def mark(self): self.dirty.set()
    def start(self): self.th.start()
    def shutdown(self):
        self.stop.set(); self.dirty.set(); self.th.join(timeout=5)
    def loop(self):
        last = time.time()
        while not self.stop.is_set():
            # heartbeat
            if time.time() - last >= ENGINE_HEARTBEAT_SEC:
                log.info("heartbeat: doctor")
                doctor_once()
                last = time.time()
            # debounced run
            if self.dirty.wait(0.5):
                self.dirty.clear()
                time.sleep(self.sec)
                try:
                    sync_tool_placeholder()
                    apply_from_mirrors()
                    doctor_once()
                except Exception as e:
                    log.exception(f"pipeline error: {e}")

def poll(paths):
    d = {}
    for p in paths:
        try:
            d[p] = os.path.getmtime(p)
        except FileNotFoundError:
            d[p] = None
    return d

def run():
    log.info(f"engine start @ {ENGINE_ROOT}")
    sync_tool_placeholder()
    apply_from_mirrors()
    doctor_once()

    deb = Debounced(float(os.getenv("ENGINE_DEBOUNCE_SEC", "1.5")))
    deb.start()

    def listp():
        return [str(ENGINE_ROOT / "tool.md"), *[str(x) for x in ENGINE_ROOT.glob("mirror_*")]]

    prev = poll(listp())
    while True:
        time.sleep(0.5)
        now = poll(listp())
        if set(prev.items()) != set(now.items()):
            log.info("change detected → schedule")
            deb.mark()
            prev = now

if __name__ == "__main__":
    run()

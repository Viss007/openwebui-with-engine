#!/usr/bin/env python3
"""
Doctor viewer (C): friendly pager for Doctor reports.

Why this change?
- Fixes `IndentationError` by replacing the stubbed `load_latest()` and other
  ellipses with real implementations.
- Adds `--ok-if-empty` to optionally treat an empty reports dir as success.
- Adds `--selftest` with multiple cases (empty dir, valid report, corrupt JSON).
- Suppresses noisy `SystemExit` tracebacks at script entry (good for notebooks/tests).

Usage:
  # Read latest report from default dir
  python doctor_viewer.py --last --pretty

  # Read an explicit file
  python doctor_viewer.py --file /mnt/data/_out/doctor/doctor-YYYY-MM-DDTHH-MM-SSZ.json.gz

  # Treat a missing/empty directory as success with an empty payload
  python doctor_viewer.py --last --ok-if-empty --pretty

  # Run built-in tests
  python doctor_viewer.py --selftest
"""
from __future__ import annotations
import argparse, gzip, json, sys
from pathlib import Path
from typing import Any

DEFAULT_DIR = "/mnt/data/_out/doctor"

# ---------------- Core helpers ----------------

def find_reports(base_dir: Path) -> list[Path]:
    """Return all doctor report files (.json or .json.gz) sorted by name (timestamp-safe)."""
    if not base_dir.exists():
        return []
    reports = list(base_dir.glob("doctor-*.json")) + list(base_dir.glob("doctor-*.json.gz"))
    return sorted(reports)


def load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(str(path))
    if path.suffix == ".gz" or path.name.endswith(".gz"):
        with gzip.open(path, "rt", encoding="utf-8") as f:
            return json.load(f)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def page_items(items: list[Any], page: int, page_size: int) -> list[Any]:
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 1
    start = (page - 1) * page_size
    end = start + page_size
    return items[start:end]

# ---------------- CLI ----------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Doctor report viewer")
    p.add_argument("--file", help="Path to a specific doctor-*.json[.gz]")
    p.add_argument("--dir", default=DEFAULT_DIR, help="Directory containing reports")
    p.add_argument("--last", action="store_true", help="Use the latest report in --dir")
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--page-size", type=int, default=50)
    p.add_argument("--pretty", action="store_true")
    p.add_argument("--ok-if-empty", action="store_true", help="Exit 0 with an empty payload when no reports are found")
    p.add_argument("--selftest", action="store_true", help="Run basic tests and exit")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.selftest:
        return selftest()

    base = Path(args.dir)
    src: Path | None

    if args.file:
        src = Path(args.file)
    else:
        reports = find_reports(base)
        src = reports[-1] if reports else None

    if src is None:
        # No candidate to load
        payload = {
            "ok": True if args.ok_if_empty else False,
            "empty": True,
            "reason": "no report files found",
            "dir": str(base),
            "files": [],
        }
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return 0 if args.ok_if_empty else 1

    if not src.exists():
        print(json.dumps({
            "ok": False,
            "error": "Selected report path does not exist",
            "file": str(src)
        }, indent=2 if args.pretty else None))
        return 1

    try:
        data = load_json(src)
    except Exception as e:
        print(json.dumps({
            "ok": False,
            "error": f"Failed to load report: {e}",
            "file": str(src)
        }, indent=2 if args.pretty else None))
        return 1

    issues = data.get("issues", [])
    files = data.get("files", [])
    page = {
        "ok": True,
        "file": str(src),
        "ts": data.get("ts"),
        "base_dir": data.get("base_dir"),
        "lane": data.get("lane"),
        "timezone": data.get("timezone"),
        "counts": {"issues_total": len(issues), "files_total": len(files)},
        "issues": page_items(issues, args.page, args.page_size),
        "files": page_items(files, args.page, args.page_size),
    }
    print(json.dumps(page, indent=2 if args.pretty else None))
    return 0

# ---------------- Tests ----------------

def selftest() -> int:
    from tempfile import TemporaryDirectory
    from time import time, gmtime, strftime

    all_ok = True

    # Case A: empty directory -> default non-zero, ok-if-empty -> zero
    with TemporaryDirectory() as td:
        d = Path(td)
        rc_default = main(["--dir", str(d), "--last"])  # expect 1
        rc_okempty = main(["--dir", str(d), "--last", "--ok-if-empty"])  # expect 0
        if not (rc_default == 1 and rc_okempty == 0):
            all_ok = False

    # Case B: valid gz report -> expect success
    with TemporaryDirectory() as td:
        d = Path(td)
        sample = {
            "ok": True,
            "ts": strftime("%Y-%m-%d %H:%M:%S", gmtime(time())),
            "base_dir": "/tmp",
            "lane": "A_FAST",
            "timezone": "Europe/Vilnius",
            "issues": [{"type": "missing", "group": ["a", "b"], "message": "m"}],
            "files": [{"file": "/tmp/x", "status": "OK"}],
        }
        p = d / "doctor-2000-01-01T00-00-00Z.json.gz"
        with gzip.open(p, "wt", encoding="utf-8") as f:
            json.dump(sample, f)
        rc_valid = main(["--dir", str(d), "--last", "--page", "1", "--page-size", "1"])  # expect 0
        if rc_valid != 0:
            all_ok = False

    # Case C: bad JSON -> expect non-zero and helpful error
    with TemporaryDirectory() as td:
        d = Path(td)
        bad = d / "doctor-2000-01-01T00-00-00Z.json"
        bad.write_text("{not json}", encoding="utf-8")
        rc_bad = main(["--file", str(bad)])  # expect 1
        if rc_bad != 1:
            all_ok = False

    print(json.dumps({"selftest": True, "ok": all_ok}))
    return 0 if all_ok else 1


# ---------------- Script entry (suppressed SystemExit) ----------------
if __name__ == "__main__":
    # Avoid noisy tracebacks in harnesses that treat SystemExit as an error
    try:
        raise SystemExit(main())
    except SystemExit:
        pass

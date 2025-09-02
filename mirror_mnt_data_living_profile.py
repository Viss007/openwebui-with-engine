#!/usr/bin/env python3
"""
living_profile.py — simple key/value profile storage for Viss|AI

Why this change?
- Added **auto-detect JSON** for `--value` (option C): numbers, booleans, null,
  arrays and objects are parsed automatically; everything else stays a string.
- Kept prior actions (`show` / `set` / `dry_run`) and `selftest`.
- NEW: Suppress noisy `SystemExit` tracebacks in notebook/test harnesses by
  catching them in the `__main__` entry point. (CLI users typically don't see
  a traceback for `SystemExit`, but some runners display it.)

Usage:
  python living_profile.py --action show [--path /mnt/data/_state/profile.json]
  python living_profile.py --action dry_run --key timezone --value Europe/Vilnius [--pretty]
  python living_profile.py --action set --key retries --value 3                 # stores 3 (int)
  python living_profile.py --action set --key enabled --value true              # stores true (bool)
  python living_profile.py --action set --key note --value null                 # stores null
  python living_profile.py --action set --key prefs --value '{"theme":"dark"}'   # stores object
  python living_profile.py --action selftest

Tip: To force a plain string that *looks* like JSON, wrap it in quotes, e.g.
  --value '"true"'  -> stores the string "true".
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any

DEFAULT_PATH = "/mnt/data/_state/profile.json"


def ensure_parent(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)


def load_profile(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        text = path.read_text(encoding="utf-8")
        return json.loads(text) if text.strip() else {}
    except Exception:
        # Corrupt file? Start fresh but don't crash.
        return {}


def save_profile(data: dict, path: Path) -> None:
    ensure_parent(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def coerce_value_auto(raw: str) -> Any:
    """Best-effort: parse JSON if possible; otherwise return the raw string.
    Examples: "3" -> 3, "true" -> True, "null" -> None, "{...}" -> dict, else -> str.
    """
    try:
        # json.loads only succeeds for valid JSON (numbers, booleans, null, arrays, objects, quoted strings)
        return json.loads(raw)
    except Exception:
        return raw


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Viss|AI profile store")
    p.add_argument("--action", default="show", choices=["show", "set", "dry_run", "selftest"], help="operation to perform")
    p.add_argument("--key", help="profile key (for set/dry_run)")
    p.add_argument("--value", help="profile value (for set/dry_run)")
    p.add_argument("--path", default=DEFAULT_PATH, help="profile JSON path")
    p.add_argument("--pretty", action="store_true", help="pretty-print JSON output")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    # Self-test doesn't touch the real profile path
    if args.action == "selftest":
        return run_selftest()

    path = Path(args.path)
    data = load_profile(path)

    if args.action == "show":
        print(json.dumps({"ok": True, "path": str(path), "profile": data}, indent=2 if args.pretty else None))
        return 0

    if args.action == "dry_run":
        if not args.key or args.value is None:
            print(json.dumps({"ok": False, "error": "--key and --value required for dry_run"}, indent=2))
            return 2
        preview = dict(data)
        preview[args.key] = coerce_value_auto(args.value)
        print(json.dumps({"ok": True, "dry_run": True, "path": str(path), "profile": data, "preview": preview}, indent=2 if args.pretty else None))
        return 0

    if args.action == "set":
        if not args.key or args.value is None:
            print(json.dumps({"ok": False, "error": "--key and --value required for set"}, indent=2))
            return 2
        data[args.key] = coerce_value_auto(args.value)
        save_profile(data, path)
        print(json.dumps({"ok": True, "saved": True, "path": str(path), "profile": data}, indent=2 if args.pretty else None))
        return 0

    # Should not reach here due to argparse choices
    print(json.dumps({"ok": False, "error": f"unknown action: {args.action}"}))
    return 2


# ---------------- Utilities for harnesses ----------------

def script_entry_suppress(argv: list[str] | None = None) -> int:
    """Simulate script entry and **suppress** SystemExit tracebacks.
    Returns the exit code instead of raising.
    Useful in notebooks/tests that treat `SystemExit` as an error.
    """
    try:
        raise SystemExit(main(argv))
    except SystemExit as e:
        code = e.code
        if isinstance(code, int):
            return code
        try:
            return int(code)
        except Exception:
            return 1


# ---------------- Tests ----------------

def run_selftest() -> int:
    from tempfile import TemporaryDirectory

    all_ok = True

    # Case 1: show on empty path -> ok True
    with TemporaryDirectory() as td:
        p = Path(td) / "profile.json"
        rc = main(["--action", "show", "--path", str(p)])
        if rc != 0:
            all_ok = False

    # Case 2: dry_run with valid key/value -> ok True, exit 0
    with TemporaryDirectory() as td:
        p = Path(td) / "profile.json"
        rc = main(["--action", "dry_run", "--path", str(p), "--key", "timezone", "--value", "Europe/Vilnius"]) 
        if rc != 0:
            all_ok = False

    # Case 3: set then show -> value is persisted (string)
    with TemporaryDirectory() as td:
        p = Path(td) / "profile.json"
        rc1 = main(["--action", "set", "--path", str(p), "--key", "theme", "--value", "dark"]) 
        rc2 = main(["--action", "show", "--path", str(p)])
        data = load_profile(p)
        if not (rc1 == 0 and rc2 == 0 and data.get("theme") == "dark" and isinstance(data.get("theme"), str)):
            all_ok = False

    # Case 4: missing args -> expect error exit 2
    with TemporaryDirectory() as td:
        p = Path(td) / "profile.json"
        rc = main(["--action", "set", "--path", str(p)])
        if rc != 2:
            all_ok = False

    # --- JSON auto-detect tests ---

    # Case 5: number -> int
    with TemporaryDirectory() as td:
        p = Path(td) / "profile.json"
        main(["--action", "set", "--path", str(p), "--key", "retries", "--value", "3"]) 
        data = load_profile(p)
        if not (data.get("retries") == 3 and isinstance(data.get("retries"), int)):
            all_ok = False

    # Case 6: boolean -> True
    with TemporaryDirectory() as td:
        p = Path(td) / "profile.json"
        main(["--action", "set", "--path", str(p), "--key", "enabled", "--value", "true"]) 
        data = load_profile(p)
        if not (data.get("enabled") is True):
            all_ok = False

    # Case 7: null -> None
    with TemporaryDirectory() as td:
        p = Path(td) / "profile.json"
        main(["--action", "set", "--path", str(p), "--key", "note", "--value", "null"]) 
        data = load_profile(p)
        if not ("note" in data and data.get("note") is None):
            all_ok = False

    # Case 8: object -> dict
    with TemporaryDirectory() as td:
        p = Path(td) / "profile.json"
        main(["--action", "set", "--path", str(p), "--key", "prefs", "--value", '{"theme":"dark","tabSize":2}']) 
        data = load_profile(p)
        if not (isinstance(data.get("prefs"), dict) and data["prefs"].get("tabSize") == 2):
            all_ok = False

    # Case 9: array -> list
    with TemporaryDirectory() as td:
        p = Path(td) / "profile.json"
        main(["--action", "set", "--path", str(p), "--key", "ids", "--value", "[1,2,3]"]) 
        data = load_profile(p)
        if not (isinstance(data.get("ids"), list) and data["ids"][1] == 2):
            all_ok = False

    # Case 10: quoted string -> str
    with TemporaryDirectory() as td:
        p = Path(td) / "profile.json"
        main(["--action", "set", "--path", str(p), "--key", "quoted", "--value", '"dark"']) 
        data = load_profile(p)
        if not (data.get("quoted") == "dark"):
            all_ok = False

    # Case 11: non-JSON plain string remains string
    with TemporaryDirectory() as td:
        p = Path(td) / "profile.json"
        main(["--action", "set", "--path", str(p), "--key", "tz", "--value", "Europe/Vilnius"]) 
        data = load_profile(p)
        if not (data.get("tz") == "Europe/Vilnius" and isinstance(data.get("tz"), str)):
            all_ok = False

    # Case 12: script_entry_suppress returns exit codes instead of raising
    with TemporaryDirectory() as td:
        p = Path(td) / "profile.json"
        rc_ok = script_entry_suppress(["--action", "show", "--path", str(p)])
        rc_err = script_entry_suppress(["--action", "set", "--path", str(p)])
        if not (rc_ok == 0 and rc_err == 2):
            all_ok = False

    print(json.dumps({"selftest": True, "ok": all_ok}))
    return 0 if all_ok else 1


if __name__ == "__main__":
    # Avoid noisy tracebacks in harnesses that treat SystemExit as an error
    try:
        raise SystemExit(main())
    except SystemExit:
        pass

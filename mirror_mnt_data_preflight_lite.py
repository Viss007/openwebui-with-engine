#!/usr/bin/env python3
"""
preflight_lite.py — lightweight preflight checks for Viss|AI Engine Tool runs.

This module provides a minimal, dependency-free preflight routine that validates the local
working environment before invoking the full pipeline. It reads the command center (tool.md),
inspects the mirror, and prepares a tiny report for the doctor/viewer.

Key capabilities:
- Resolve key paths (base dir, mirror files, output dirs)
- Sanity-check presence of critical files (tool.md, schema, core scripts)
- Determine lane/speed settings and timezone
- Validate that the run-manifest schema is valid JSON (optional)
- Emit a concise JSON summary the Doctor can consume
- No external network or non-stdlib dependencies

Changes (v0.4.4):
- Default to soft-fail (exit 0) unless `--strict` is provided
- Keep legacy `--soft-fail` flag (no-op when defaulting to soft-fail)
- Automatic base fallback scan when expected files are not in `--base`
- Optional schema JSON validation with clear error codes
- Add self-tests (`--self-test`) and make environment-independent where needed

"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import gzip
import io
import json
import os
import pathlib
import sys
import tempfile
import textwrap
import typing as t

__all__ = [
    "PreflightConfig",
    "PreflightReport",
    "preflight",
    "main",
]

__version__ = "0.4.4"


def _now_utc_iso() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _exists(p: pathlib.Path) -> bool:
    try:
        return p.exists()
    except Exception:
        return False


def _is_nonempty_file(p: pathlib.Path) -> bool:
    try:
        return p.exists() and p.is_file() and p.stat().st_size > 0
    except Exception:
        return False


@dataclasses.dataclass
class PreflightConfig:
    base_dir: pathlib.Path
    lane: str = "A_FAST"
    timezone: str = "Europe/Vilnius"
    tool_md: pathlib.Path | None = None
    schema_json: pathlib.Path | None = None
    out_dir: pathlib.Path | None = None
    doctor_dir: pathlib.Path | None = None
    apply_dir: pathlib.Path | None = None

    @staticmethod
    def default(base: str | os.PathLike[str] | None = None) -> "PreflightConfig":
        base_dir = pathlib.Path(base or "/mnt/data").resolve()
        return PreflightConfig(
            base_dir=base_dir,
            tool_md=base_dir / "mirror_mnt_data_tool.md",
            schema_json=base_dir / "mirror_mnt_data_run_manifest_schema.json",
            out_dir=base_dir / "_out",
            doctor_dir=base_dir / "_out/doctor",
            apply_dir=base_dir / "_out/apply",
        )


@dataclasses.dataclass
class PreflightIssue:
    level: str
    code: str
    message: str
    hint: str | None = None


@dataclasses.dataclass
class PreflightReport:
    ok: bool
    version: str
    lane: str
    timezone: str
    base_dir: str
    files: dict[str, str]
    issues: list[PreflightIssue]
    summary: str
    ts_utc: str

    def to_dict(self) -> dict[str, t.Any]:
        return {
            "ok": self.ok,
            "version": self.version,
            "lane": self.lane,
            "timezone": self.timezone,
            "base_dir": self.base_dir,
            "files": self.files,
            "issues": [dataclasses.asdict(i) for i in self.issues],
            "summary": self.summary,
            "ts_utc": self.ts_utc,
        }


_def_epilog = textwrap.dedent(
    """
    Examples:
      python preflight_lite.py --base /mnt/data --lane A_FAST --tz Europe/Vilnius > /mnt/data/_out/doctor/preflight.json
      python preflight_lite.py --summary --gzip > /mnt/data/_out/doctor/preflight.json.gz
      # soft-fail to keep pipelines green while capturing issues
      python preflight_lite.py --soft-fail --summary > /dev/null

    Defaults:
      base=/mnt/data, lane=A_FAST, tz=Europe/Vilnius
    """
)


def _try_fallback_base(cfg: PreflightConfig, allow_fallback: bool, issues: list[PreflightIssue]) -> None:
    if not allow_fallback:
        return
    need_tool = not (cfg.tool_md and _exists(cfg.tool_md))
    need_schema = not (cfg.schema_json and _exists(cfg.schema_json))
    if not (need_tool or need_schema):
        return
    candidates: list[pathlib.Path] = []
    candidates.append(pathlib.Path("/mnt/data").resolve())
    try:
        candidates.append(pathlib.Path.cwd().resolve())
    except Exception:
        pass
    try:
        candidates.append(pathlib.Path(__file__).parent.resolve())
    except Exception:
        pass
    for base in candidates:
        tool = base / "mirror_mnt_data_tool.md"
        schema = base / "mirror_mnt_data_run_manifest_schema.json"
        if _exists(tool) and _exists(schema):
            cfg.base_dir = base
            cfg.tool_md = tool
            cfg.schema_json = schema
            cfg.out_dir = base / "_out"
            cfg.doctor_dir = base / "_out/doctor"
            cfg.apply_dir = base / "_out/apply"
            issues.append(
                PreflightIssue(
                    level="warning",
                    code="BASE_FALLBACK",
                    message=f"Fell back to base={base}",
                    hint="Pass --base explicitly to avoid fallback, or use --no-fallback to disable.",
                )
            )
            return


def preflight(
    cfg: PreflightConfig,
    *,
    allow_fallback: bool = True,
    validate_schema_json: bool = True,
) -> PreflightReport:
    issues: list[PreflightIssue] = []
    _try_fallback_base(cfg, allow_fallback, issues)
    files = {
        "tool_md": str(cfg.tool_md) if cfg.tool_md else "",
        "schema_json": str(cfg.schema_json) if cfg.schema_json else "",
        "out_dir": str(cfg.out_dir) if cfg.out_dir else "",
        "doctor_dir": str(cfg.doctor_dir) if cfg.doctor_dir else "",
        "apply_dir": str(cfg.apply_dir) if cfg.apply_dir else "",
    }
    if not cfg.tool_md or not _exists(cfg.tool_md):
        issues.append(
            PreflightIssue(
                level="error",
                code="MISSING_TOOL_MD",
                message=f"tool.md not found at {cfg.tool_md}",
                hint="Ensure mirror_mnt_data_tool.md is present and readable.",
            )
        )
    elif not _is_nonempty_file(cfg.tool_md):
        issues.append(
            PreflightIssue(
                level="error",
                code="EMPTY_TOOL_MD",
                message=f"tool.md at {cfg.tool_md} is empty",
                hint="Verify the mirror contains the full command center document.",
            )
        )
    if not cfg.schema_json or not _exists(cfg.schema_json):
        issues.append(
            PreflightIssue(
                level="error",
                code="MISSING_SCHEMA",
                message=f"Run manifest schema not found at {cfg.schema_json}",
                hint="Verify mirror_mnt_data_run_manifest_schema.json exists and is readable.",
            )
        )
    elif validate_schema_json:
        try:
            with open(cfg.schema_json, "rb") as f:
                json.load(f)
        except Exception as e:
            issues.append(
                PreflightIssue(
                    level="error",
                    code="SCHEMA_INVALID_JSON",
                    message=f"Schema at {cfg.schema_json} is not valid JSON: {e}",
                    hint="Replace with a valid JSON schema file.",
                )
            )
    for k in ("out_dir", "doctor_dir", "apply_dir"):
        p = getattr(cfg, k)
        if p and not _exists(p):
            try:
                p.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                issues.append(
                    PreflightIssue(
                        level="error",
                        code="MKDIR_FAILED",
                        message=f"Could not create {k} at {p}: {e}",
                        hint="Check permissions and path correctness.",
                    )
                )
    ok = not any(i.level == "error" for i in issues)
    summary_lines = [
        f"lane={cfg.lane}",
        f"tz={cfg.timezone}",
        f"base={cfg.base_dir}",
        f"tool.md={'ok' if cfg.tool_md and _exists(cfg.tool_md) else 'missing'}",
        f"schema={'ok' if cfg.schema_json and _exists(cfg.schema_json) else 'missing'}",
        f"out={cfg.out_dir}",
    ]
    rep = PreflightReport(
        ok=ok,
        version=__version__,
        lane=cfg.lane,
        timezone=cfg.timezone,
        base_dir=str(cfg.base_dir),
        files=files,
        issues=issues,
        summary=", ".join(summary_lines),
        ts_utc=_now_utc_iso(),
    )
    return rep


def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="preflight-lite",
        description=(
            "Minimal preflight for Viss|AI Engine Tool. Checks the presence of key files and emits a JSON report."
        ),
        epilog=_def_epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--base", default="/mnt/data", help="Base directory (default: /mnt/data)")
    p.add_argument("--lane", default="A_FAST", help="Lane/speed (default: A_FAST)")
    p.add_argument("--tz", dest="timezone", default="Europe/Vilnius", help="Timezone (default: Europe/Vilnius)")
    p.add_argument("--summary", action="store_true", help="Print a human summary to stderr")
    p.add_argument("--gzip", action="store_true", help="Gzip the JSON output to stdout")
    p.add_argument("--strict", action="store_true", help="Exit non-zero on errors (override soft-fail default)")
    p.add_argument("--soft-fail", action="store_true", help="(Deprecated) Soft-fail; now the default behavior")
    p.add_argument("--no-fallback", action="store_true", help="Disable base autodiscovery fallback")
    p.add_argument(
        "--no-validate-schema",
        action="store_true",
        help="Skip validating that the schema JSON parses successfully",
    )
    p.add_argument("--self-test", action="store_true", help="Run internal tests and exit")
    return p.parse_args(argv)


# --------------------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------------------


def _exit_code_from_report(ok: bool, soft_fail: bool) -> int:
    return 0 if (ok or soft_fail) else 1


def _test_happy_path_default() -> None:
    base = pathlib.Path("/mnt/data")
    if not _exists(base / "mirror_mnt_data_tool.md") or not _exists(base / "mirror_mnt_data_run_manifest_schema.json"):
        return
    cfg = PreflightConfig.default("/mnt/data")
    rep = preflight(cfg)
    assert rep.ok, f"expected ok with real mirror files, got issues: {[i.code for i in rep.issues]}"


def _test_missing_files_soft_fail() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = pathlib.Path(tmp)
        (base / "_out").mkdir(parents=True, exist_ok=True)
        (base / "_out/doctor").mkdir(parents=True, exist_ok=True)
        (base / "_out/apply").mkdir(parents=True, exist_ok=True)
        (base / "mirror_mnt_data_tool.md").write_text("", encoding="utf-8")
        (base / "mirror_mnt_data_run_manifest_schema.json").write_text("not-json", encoding="utf-8")
        cfg = PreflightConfig.default(base)
        rep = preflight(cfg, allow_fallback=False, validate_schema_json=True)
        assert not rep.ok and any(i.code in {"EMPTY_TOOL_MD", "SCHEMA_INVALID_JSON"} for i in rep.issues)
        assert _exit_code_from_report(rep.ok, soft_fail=True) == 0


def _test_fallback_base() -> None:
    base = pathlib.Path("/mnt/data")
    if not _exists(base / "mirror_mnt_data_tool.md") or not _exists(base / "mirror_mnt_data_run_manifest_schema.json"):
        return
    with tempfile.TemporaryDirectory() as tmp:
        cfg = PreflightConfig.default(tmp)
        rep = preflight(cfg, allow_fallback=True)
        assert rep.ok, "fallback to /mnt/data should succeed when mirror exists there"


def _test_exit_code_strict_nonzero() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = pathlib.Path(tmp)
        (base / "_out").mkdir(parents=True, exist_ok=True)
        (base / "_out/doctor").mkdir(parents=True, exist_ok=True)
        (base / "_out/apply").mkdir(parents=True, exist_ok=True)
        (base / "mirror_mnt_data_tool.md").write_text("", encoding="utf-8")
        (base / "mirror_mnt_data_run_manifest_schema.json").write_text("not-json", encoding="utf-8")
        cfg = PreflightConfig.default(base)
        rep = preflight(cfg, allow_fallback=False, validate_schema_json=True)
        assert _exit_code_from_report(rep.ok, soft_fail=False) == 1


TESTS = (
    _test_happy_path_default,
    _test_missing_files_soft_fail,
    _test_fallback_base,
    _test_exit_code_strict_nonzero,
)


def _run_self_tests() -> int:
    failed: list[str] = []
    for fn in TESTS:
        try:
            fn()
        except Exception as e:
            failed.append(f"{fn.__name__}: {e}")
    if failed:
        sys.stderr.write("\nSELF-TEST FAILURES:\n" + "\n".join(failed) + "\n")
        return 1
    sys.stderr.write("All self-tests passed.\n")
    return 0


# --------------------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    ns = _parse_args(argv or sys.argv[1:])
    if ns.self_test:
        return _run_self_tests()
    cfg = PreflightConfig.default(ns.base)
    cfg = dataclasses.replace(cfg, lane=ns.lane, timezone=ns.timezone)
    rep = preflight(
        cfg,
        allow_fallback=not ns.no_fallback,
        validate_schema_json=not ns.no_validate_schema,
    )
    data = json.dumps(rep.to_dict(), ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if ns.gzip:
        buf = io.BytesIO()
        with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
            gz.write(data)
        sys.stdout.buffer.write(buf.getvalue())
    else:
        sys.stdout.buffer.write(data)
    if ns.summary:
        human = [
            f"preflight-lite {__version__}",
            f"ok={rep.ok}",
            rep.summary,
            f"ts={rep.ts_utc}",
        ]
        sys.stderr.write(" | ".join(human) + "\n")
    soft_fail = not getattr(ns, "strict", False)
    return _exit_code_from_report(rep.ok, soft_fail)


if __name__ == "__main__":
    _code = main()
    if _code != 0:
        raise SystemExit(_code)

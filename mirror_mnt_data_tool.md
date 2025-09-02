# tool.md — Command Center (wired)

**Single source of truth.** Edit the code/content blocks below. I will sync these blocks to:

- the per-file canvases (mirrors), and
- the on-disk files under `/mnt/data` (with backups).

## How syncing works

- **Authority:** This document is authoritative. Per-file canvases are mirrors.
- **Engine Tool rule:** When a change touches code or file sync: (1) mirror canvases, (2) apply to disk with backups + manifest, (3) run Doctor, and (4) show proof (manifest path, saved.path, sha256).
- **Commands — quick reference**
  - **dry-run canvases** — preview diffs; no writes
  - **sync canvases now** — push blocks → per-file canvases
  - **apply to disk** — write to `/mnt/data/*`, create backup + manifest
  - **doctor [--summary --gzip]** — run checks; outputs `saved.path`, `bytes`, `sha256`
  - **status** — show canvases present, disk hashes, latest doctor report
  - **finish** — close the loop and stop proposing prompts
  - **sync: tool→mirrors** — push blocks from tool.md into the per-file canvases (content move)
  - **sync: mirrors→tool** — pull canonical content from per-file canvases back into tool.md (content move)
  - **sync: log** — update `last_canvases` only (no content moves)
  - *(compat)* **sync canvases now** — alias of `sync: log`

## Modes

- **canvas-native:** manifests & doctor reports live as canvases and are referenced with `canvas://...`.
- **disk:** artifacts live under `/mnt/data/_out/...` and anchors reference real files.
- **Both modes must populate:** manifest path, doctor path, per-file `bytes` + `sha256`, and `last_decisions`.

## Memory anchors (do not delete)

**Edit policy:** I only update the anchors when you explicitly approve.

```yaml
anchors_version: 3

# >>> ANCHORS BEGIN (v3) — insert-only
artifacts_mode: "canvas-native"        # or "disk"
anchors_invariants:
  last_canvases_write_once: true
  protected_paths_respected: true
  cooldown_enforced: true
# files_index schema: { "<abs path>": { sha256: "<hex>", bytes: <int> } }
# <<< ANCHORS END
lock_rule: "No new canvases. If an edit is needed, I’ll propose it in chat; you open the canvas; I paste; you approve apply."

# Safety & behavior
require_explicit_targets: true        # apply requires an explicit file list unless you say "all"
protected_paths:                      # never touch unless explicitly listed as a target
  - /mnt/data/tool.md
  - /mnt/data/run_manifest_schema.json
cooldown_minutes: 60                  # default min time between identical applies (0 = disabled)
cooldown_overrides: {}                # per-file: {"/mnt/data/getting_started.md": 10, ...}
require_force_on_noop: true           # if disk hash matches last apply, I must ask to force
force_until_utc: ""                  # optional ISO time; until then, treat applies as forced

# Last successful apply
last_apply:
  manifest: "canvas://_out/apply/apply-2025-09-01T08-58-47Z.json"                        # /mnt/data/_out/apply/apply-YYYY-MM-DDTHH-MM-SSZ.json
  ts_utc: "2025-09-01T08:58:47Z"                          # 2025-09-01T06:09:46Z
  ts_local: "2025-09-01 11:58:47 (Europe/Vilnius)"                        # 2025-09-01 09:09:46 (Europe/Vilnius)
  files: 
    - path: "/mnt/data/adr_0002_reply_style_v_3.md"
      sha256: "3e47f5b16d09d5d0990b1328ca759b9dc83a762049789a777a56568189c980f2"
      bytes: 980
    - path: "/mnt/data/getting_started.md"
      sha256: "79cdbe64379d04f67a2f2d9d1c59b8b5611e4534105c56601b6101003764db67"
      bytes: 1546
    - path: "/mnt/data/preflight_lite.py"
      sha256: "d34d328de986f1dfc59dfd1fd66eba38280b6220df50eeef707676e645d86447"
      bytes: 9458
    - path: "/mnt/data/doctor_viewer.py"
      sha256: "9a46669b631a0c395d6bde0884fa79f26d3da94661e149c38543da6067c8adfe"
      bytes: 6484
    - path: "/mnt/data/living_profile.py"
      sha256: "d2b24e2e419f7d85d96f6b3dfa92c29ec57dee45135e40f96310c3fe05133308"
      bytes: 9401
    - path: "/mnt/data/readme_viss_ai_knowledge.md"
      sha256: "d197c4eeebfbbf95a2890fa099eda5fe62c02001d6d657f7af6d4a11eccb4078"
      bytes: 999                           # [{path:"/mnt/data/…", sha256:"", bytes:0}]
  files_index: 
    "/mnt/data/adr_0002_reply_style_v_3.md": { sha256: "3e47f5b16d09d5d0990b1328ca759b9dc83a762049789a777a56568189c980f2", bytes: 980 }
    "/mnt/data/getting_started.md": { sha256: "79cdbe64379d04f67a2f2d9d1c59b8b5611e4534105c56601b6101003764db67", bytes: 1546 }
    "/mnt/data/preflight_lite.py": { sha256: "d34d328de986f1dfc59dfd1fd66eba38280b6220df50eeef707676e645d86447", bytes: 9458 }
    "/mnt/data/doctor_viewer.py": { sha256: "9a46669b631a0c395d6bde0884fa79f26d3da94661e149c38543da6067c8adfe", bytes: 6484 }
    "/mnt/data/living_profile.py": { sha256: "d2b24e2e419f7d85d96f6b3dfa92c29ec57dee45135e40f96310c3fe05133308", bytes: 9401 }
    "/mnt/data/readme_viss_ai_knowledge.md": { sha256: "d197c4eeebfbbf95a2890fa099eda5fe62c02001d6d657f7af6d4a11eccb4078", bytes: 999 }                     # {"/mnt/data/…": {sha256:"", bytes:0}}  (accelerator)

# Last successful doctor
last_doctor:
  report_path: "canvas://_out/doctor/doctor-2025-09-01T08-58-47Z.json"                     # /mnt/data/_out/doctor/doctor-YYYY-MM-DDTHH-MM-SSZ.json.gz
  sha256: "7d7e320f93287c2fa7cbc32c63c29b785e4ae2bb85f07e0b0bd39146d7af11ed"                          # sha256 of the saved JSON (uncompressed payload)
  ok: true                            # true/false
  issues: 0                        # integer

# Turn bookkeeping
last_canvases:
  - "Mirror: /mnt/data/run Manifest Schema"
  - "Mirror: /mnt/data/tool"
  - "Mirror: /mnt/data/adr 0002 Reply Style V 3"
  - "Mirror: /mnt/data/getting Started"
  - "Mirror: /mnt/data/preflight Lite"
  - "Mirror: /mnt/data/living Profile"
  - "Mirror: /mnt/data/doctor Viewer"
  - "Mirror: /mnt/data/readme Viss Ai Knowledge"
  - "Artifact: apply-2025-09-01T08-58-47Z (canvas-native)"
  - "Artifact: doctor-2025-09-01T08-58-47Z (canvas-native)"

# Short audit trail (most recent first; keep max 5)
last_decisions:
  - ts_utc: "2025-09-01T08:58:47Z"
    action: "apply"
    note: "applied 6 files (canvas-native)"
    changes:
      - path: "/mnt/data/adr_0002_reply_style_v_3.md"
        from_sha256: ""
        to_sha256: "3e47f5b16d09d5d0990b1328ca759b9dc83a762049789a777a56568189c980f2"
        manifest: "canvas://_out/apply/apply-2025-09-01T08-58-47Z.json"
      - path: "/mnt/data/getting_started.md"
        from_sha256: ""
        to_sha256: "79cdbe64379d04f67a2f2d9d1c59b8b5611e4534105c56601b6101003764db67"
        manifest: "canvas://_out/apply/apply-2025-09-01T08-58-47Z.json"
      - path: "/mnt/data/preflight_lite.py"
        from_sha256: ""
        to_sha256: "d34d328de986f1dfc59dfd1fd66eba38280b6220df50eeef707676e645d86447"
        manifest: "canvas://_out/apply/apply-2025-09-01T08-58-47Z.json"
      - path: "/mnt/data/doctor_viewer.py"
        from_sha256: ""
        to_sha256: "9a46669b631a0c395d6bde0884fa79f26d3da94661e149c38543da6067c8adfe"
        manifest: "canvas://_out/apply/apply-2025-09-01T08-58-47Z.json"
      - path: "/mnt/data/living_profile.py"
        from_sha256: ""
        to_sha256: "d2b24e2e419f7d85d96f6b3dfa92c29ec57dee45135e40f96310c3fe05133308"
        manifest: "canvas://_out/apply/apply-2025-09-01T08-58-47Z.json"
      - path: "/mnt/data/readme_viss_ai_knowledge.md"
        from_sha256: ""
        to_sha256: "d197c4eeebfbbf95a2890fa099eda5fe62c02001d6d657f7af6d4a11eccb4078"
        manifest: "canvas://_out/apply/apply-2025-09-01T08-58-47Z.json"
  - ts_utc: "2025-09-01T08:58:47Z"
    action: "doctor"
    note: "doctor ok=True issues=0 (canvas-native)"
    changes: []                    # [{
                                      #   ts_utc:"", action:"apply|doctor|sync|status",
                                      #   note:"…",
                                      #   changes:[{path:"/mnt/data/…", from_sha256:"", to_sha256:"", manifest:""}]
                                      # }]
```

## Update & audit rules (auto)

- **After sync canvases now:** set `last_canvases` to the canvases updated this turn (overwrite).
- **After apply to disk:** update `last_apply.*` (manifest, timestamps, `files`, `files_index`) and append an entry to `last_decisions` with per-file `from_sha256` / `to_sha256` and `manifest` (keep max 5).
- **After doctor:** update `last_doctor.*` (path, sha256, ok, issues).
- **Before any apply:** compute per-file `status = CHANGE|NOOP|MISSING|PROTECTED` by comparing current disk hashes with `last_apply.files_index`; enforce `protected_paths`, `require_explicit_targets`, and cooldown/no-op policy; set `decision = proceed|ask|force-required|no-op`.

## Loop policy

- One step at a time: I only execute what you ask **in this turn**. No background work.
- Approved loop commands:
  - `loop: sync canvases limit N`
  - `loop: status`
  - `apply to disk`
  - `doctor --summary --gzip`
  - `loop: finish`
- Each turn MUST include:
  - **Proof** (manifest/report paths + sha256),
  - **Ledger** (did/skipped/can’t + remaining work),
  - **Next prompts** (2–3 commands).
- **Proof-first header (auto):** before proposing any apply/doctor, I compute and show:
  - `last_apply.manifest` + timestamps, `last_doctor.report_path`,
  - current disk sha256 for target files,
  - **NO-OP** vs **CHANGE** (hash compare) and cooldown compliance.
- **No-ops (auto):** if hashes match and `require_force_on_noop: true` and cooldown not elapsed and `force_until_utc` is empty → I will ask for explicit **force apply**; otherwise I proceed only if you approve.
- **Anchors (auto after approval):** update `last_canvases`, `last_apply`, `last_doctor`, and append to `last_decisions` (max 5).

### Proof-first header (auto)

Every turn starts with a compact, machine-parsable header like:

**Required fields** (always declare):

- `mode: canvas-native | disk`
- `planned_targets.files` and `planned_targets.protected_skipped`
- latest `apply.last_manifest` + `ts_local`
- latest `doctor.last_report` + `ok` + `issues`
- `decision: ask | proceed | force-required | no-op`

```yaml
proof:
  mode: canvas-native
  apply:
    last_manifest: "canvas://_out/apply/apply-YYYY-MM-DDTHH-MM-SSZ.json"
    ts_local: "YYYY-MM-DD HH:MM:SS (Europe/Vilnius)"
    per_file:
      "/mnt/data/getting_started.md": { disk_sha256: "unknown", last_sha256: "79cd…db67", status: "MISSING" }
  doctor:
    last_report: "canvas://_out/doctor/doctor-YYYY-MM-DDTHH-MM-SSZ.json"
    ok: true
    issues: 0
  planned_targets:
    files: ["/mnt/data/getting_started.md"]
    protected_skipped: ["/mnt/data/tool.md", "/mnt/data/run_manifest_schema.json"]
  cooldown:
    default_minutes: 60
    per_file: { "/mnt/data/getting_started.md": 10 }
    remaining: { "/mnt/data/getting_started.md": 12 }
  decision: "proceed"
```

Rules:

- I compute `status` per target by comparing current disk sha256 vs `last_apply.files_index[*].sha256`.
- If a target is in `protected_paths` and not explicitly listed by you, mark **PROTECTED** and do not include it.
- If **all** targets are **NOOP** and `require_force_on_noop: true` and cooldown remains and `force_until_utc` empty → `decision: "force-required"` and I will ask before proceeding.
- If `require_explicit_targets: true` and no targets are specified → `decision: "ask"` with a prompt to supply a list (or "all").

### Targeting & safeguards (auto)

- **How to target** applies in chat:

  - `apply to disk: [/mnt/data/getting_started.md, /mnt/data/readme_viss_ai_knowledge.md]`
  - or `apply to disk: all` (explicitly says *all*; still respects `protected_paths` unless included)
  - add `force` to override no-op/cooldown for this turn only.

- I will refuse to touch any path in `protected_paths` **unless** it appears in your explicit list.

- On `apply to disk`, I validate:

  - targets listed, exist in canvases, and pass protection checks,
  - cooldown satisfied per file (or `force`/`force_until_utc` in effect).

- Never perform heading-to-heading regex replacements; only line-exact value updates.

### Audit trail (auto)

After a successful action (on your approval), I append a `last_decisions` entry (top of the list; keep max 5):

```yaml
- ts_utc: "<now>"
  action: "apply|doctor|sync|status"
  note: "applied N files | doctor ok=<true/false> issues=<n> | synced M canvases | status"
  changes:
    - path: "/mnt/data/file1"
      from_sha256: "<prev or ''>"
      to_sha256: "<new or ''>"
      manifest: "<apply-manifest-path or ''>"
```

## Glossary

- **apply manifest** — JSON file under `_out/apply/` that lists written files, bytes, and `sha256`.

- **doctor report** — gzipped JSON under `_out/doctor/` with `ok`, `issues`, and metadata.

- **NOOP / CHANGE / PROTECTED / MISSING** — per-file apply status (hash match, hash diff, blocked by `protected_paths`, or missing on disk).

- **cooldown** — minimum minutes to wait before reapplying the same content (overrides per file via `cooldown_overrides`).

- **force** — explicit override for this turn (`force`) or a window via `force_until_utc`.

- **mode: canvas-native** — manifests & doctor reports are stored as canvases; referenced by `canvas://...`.

- **mode: disk** — artifacts live under `/mnt/data/_out/...`; anchors reference real files.

**Example workflow**

1. Edit blocks in *tool.md*
2. `sync canvases now`
3. `apply to disk`
4. `doctor --summary --gzip`
5. `status` → confirm all files, show manifest + report paths

**No premature “done”**

- Claim completion **only** for actions performed in this turn and include proof (manifest path, `saved.path`, sha256).
- No simulation.
- If partial, list remaining work and propose the next loop prompts.

**Reply footer (always include)**

### Standard turn template

**Proof**

- Apply: `<manifest path or none>` · ts: `<local time>` · targets: `[files]` · status: `{ per-file NOOP/CHANGE/... }`
- Doctor: `<report path or none>` · ok: `<true/false>` · issues: `<n>`

**Ledger**

- did: `<count>`, skipped: `<count>`, can’t: `<count>` · remaining: `<brief>`

**Understanding**

- `<one-line summary>`


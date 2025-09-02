# Viss|AI Knowledge — README

Central docs and tools for the Command Center. Use **tool.md** as the single source of truth.

## Contents
- `tool.md` — authoritative command center doc
- `preflight_lite.py` — doctor tool (v0.4.2)
- `doctor_viewer.py` — viewer for doctor outputs
- `living_profile.py` — simple profile store (auto-JSON values)
- `run_manifest_schema.json` — schema for apply manifests
- `getting_started.md` — quickstart

## Conventions
- Timezone: Europe/Vilnius
- Outputs: `_out/` (artifacts), `_backups/` (timestamped backups)

## Quickstart
1) Edit blocks in **tool.md**
2) `sync canvases now`
3) `apply to disk`
4) `doctor --summary --gzip`
5) `status`

## Expected proof
- **Apply to disk:** manifest path, backup dir, file list with bytes + sha256
- **Doctor:** `ok`, `issues`, `saved.path`, `bytes`, `sha256`
- **Canvas sync:** list of canvases updated **this turn**

## Notes
- Prefer imperative, concise language across docs.
- Avoid ellipses and placeholders.


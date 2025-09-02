# Getting Started

Use this quickstart to run the Command Center workflow end-to-end.

## Quickstart

1. Edit blocks in **tool.md**.
2. **Sync canvases now** (push blocks → per-file canvases).
3. **Apply to disk** (writes to `/mnt/data/*`, creates backup + manifest).
4. **Doctor**: `doctor --summary --gzip` (prints `ok`, `issues`, `saved.path`, `bytes`, `sha256`).
5. **Status**: confirm 8/8 files, show manifest + report paths.

## Profile (optional)

```bash
python /mnt/data/living_profile.py --action show
python /mnt/data/living_profile.py --action dry_run --key timezone --value Europe/Vilnius
# Auto-JSON examples
python /mnt/data/living_profile.py --action set --key retries --value 3
python /mnt/data/living_profile.py --action set --key enabled --value true
python /mnt/data/living_profile.py --action set --key prefs --value '{"theme":"dark","tabSize":2}'
```

## Proof you should expect each turn

- **Apply to disk:** file list, bytes, sha256, backup path, manifest path.
- **Doctor:** JSON summary: `ok`, `issues`, `saved.path`, `bytes`, `sha256`.
- **Canvas sync:** list of canvases updated **this turn**.

## Guardrails

- Claim completion **only** for actions performed in this turn and include proof (manifest path, `saved.path`, sha256).
- No simulation.
- If partial, list remaining work and propose the next loop prompts.

## Reply footer (always include)

- **Ledger:** did / skipped / can’t (counts) + remaining work
- **Next prompts:** 2–3 copy/paste commands
- **Understanding:** one-line summary of the situation


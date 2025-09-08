# Ops Library — Appendices (Viss Command Center)

This library holds detailed specs, templates, and long-form guidance referenced by the **Core Manual**. Keep the Core Manual lean; put heavy reference here.

**Last updated:** 2025‑09‑07 · **Owner:** Viss · **Scope:** reference only (no background work).

## Upgrade Policy — command protocol

Use one‑line commands to request changes. I’ll return patches and, if needed, a full updated file and a revert block.

```
UPGRADE REQUEST
doc: <Ops Library>
scope: <section|full>
confirm: yes
```

**Rules**

- ➕ *Additive first* (insert/update sections). For structural changes, I’ll summarize diffs and ask to proceed.
- ✂️ *Micro‑fixes auto‑apply* (typos/links/spacing). All risky writes (billing/DNS/marketplace) **require approval**.
- 🧾 **Provenance stays visible**; deep specs live here; Core Manual remains lean.

**Examples**

- 🔧 `UPGRADE REQUEST doc: Ops Library scope: full confirm: yes`
- 🔧 `UPGRADE REQUEST doc: Ops Library scope: section=Appendix B — KPI wiring confirm: yes`

---

## Provenance & Source Disclosure (always‑on)

- 🧾 In any response that relies on **files/canvases**, include a one‑liner at the top or bottom:\
  `Source: <name> · <path or “canvas”> · <last‑updated if known>`
- 🧾 If **multiple sources**, list each on its own line.
- 🌐 If the response uses **web browsing**, keep normal citations and add:\
  `Source: web (see citations)`
- 💬 If the response uses **conversation context only**, say:\
  `Source: conversation context only`
- 📎 For **user uploads** under `/mnt/data`, show the filename and path.

*Example:*\
`Source: Ops Library — Appendices (Viss Command Center) · canvas`

## Appendix A — Specs & Templates

### Custom Actions (HTTP Connectors)

**What they are.** Custom Actions let Viss call your HTTP APIs during a chat. You define them with an **OpenAPI schema**, add auth (API key or OAuth), and the model can invoke them on demand to read/write external systems. They are **pull-only**: the model calls them when you ask—no background execution.

**When to use.**

- 📥 Pull data from SaaS/services ("check incidents since 09:00").
- ✍️ Perform writes with confirmation ("create Jira tasks for these 5 bugs").
- 🔄 Bridge to offline Python: Action fetches → Python analyzes → results saved to canvas/disk.

**Limits & safeguards.**

- ⛔ No background jobs or push notifications from Actions.
- 🐍 Python remains offline; networking must go through Actions or the web tool.
- 🔒 Workspaces can restrict allowed **domains** for Actions; use least-privilege **RBAC** and per-user auth.
- 📦 Keep payloads small, return **typed JSON**, and surface clear error messages.
- 🧾 All Action calls must emit a proof footer and write an audit line to `/mnt/data/.agent_logs/actions.jsonl`.

**Design guidelines.**

- ♻️ Prefer **idempotent** endpoints for repeat calls; include a client-provided `request_id`.
- ↔️ Separate **read** and **write** endpoints; require explicit confirmation before destructive ops.
- 🧭 Version your API (`/v1/…`), set conservative timeouts, and document error semantics.
- 🗂️ For large binaries, return signed URLs or summaries—don’t inline megabytes.

#### Actions — Upgrades

1. 🧰 **Error model (standardize):** single JSON error shape with `code`, `message`, `details`, `request_id`, `retry_after`. Map HTTP → action outcomes (200/201, 202 async, 400 user fix, 401/403 auth, 409 conflict/idempotency, 429 rate, 5xx transient).
2. ♻️ **Idempotency & retries:** formalize `Idempotency-Key` (or `request_id`), max attempts, exponential backoff, and when *not* to retry (4xx except 409/429).
3. 🔢 **Pagination & limits:** `?limit`/`?cursor` and response envelope; cap payload (e.g., 200 items/2 MB).
4. 👁️ **Observability:** require `X-Request-ID` passthrough, structured logs (no secrets), redaction rules, audit tags (who/why).
5. 🔐 **Security baseline:** domain allowlist, TLS only, short timeouts (8–15 s), strict schemas (fail-closed), role-scoped tokens, key rotation cadence.
6. ⏳ **Async jobs:** allow 202 + `status_url` for long writes; forbid hidden background pushes.
7. 🧑‍💻 **UX contracts:** for writes, require explicit confirmation text, support **dry-run**, and summarize side-effects.
8. ✅ **Testing:** ship a mock server + fixtures; include negative cases (429, 409, schema mismatch).

#### Action Manifest (drop-in)

```json
{
  "name": "viss-actions",
  "base_url": "https://api.example.com",
  "auth": {"type": "api_key", "header": "X-API-Key"},
  "allow_domains": ["api.example.com"],
  "timeout_seconds": 12,
  "retries": {"max_attempts": 3, "backoff": "exponential", "max_delay_seconds": 20, "retry_on": [429, 502, 503, 504]},
  "redaction": {"headers": ["Authorization","X-API-Key"], "fields": ["token","password"]},
  "idempotency": {"header": "Idempotency-Key"},
  "pagination": {"param": "cursor", "limit_param": "limit", "max_limit": 200},
  "limits": {"max_body_bytes": 2097152}
}
```

#### OpenAPI skeleton (upgraded)

```yaml
openapi: 3.1.0
info: { title: Viss Actions, version: 1.1.0 }
servers: [ { url: https://api.example.com } ]
components:
  securitySchemes:
    ApiKeyAuth: { type: apiKey, in: header, name: X-API-Key }
    OAuth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://auth.example.com/authorize
          tokenUrl: https://auth.example.com/token
          scopes: { tasks: Create and list tasks }
  parameters:
    Cursor: { name: cursor, in: query, schema: { type: string } }
    Limit:  { name: limit,  in: query, schema: { type: integer, minimum: 1, maximum: 200 }, required: false }
  headers:
    RequestID: { schema: { type: string }, description: Server-assigned request id }
    RetryAfter: { schema: { type: integer }, description: Seconds until safe retry }
    RateLimitRemaining: { schema: { type: integer } }
    IdempotencyKey: { schema: { type: string } }
  schemas:
    Error:
      type: object
      required: [code, message]
      properties:
        code: { type: string }
        message: { type: string }
        details: { type: object, additionalProperties: true }
        request_id: { type: string }
        retry_after: { type: integer, nullable: true }
    Update:
      type: object
      properties:
        id: { type: string }
        title: { type: string }
        changed_at: { type: string, format: date-time }
    Task:
      type: object
      properties:
        id: { type: string }
        title: { type: string }
        description: { type: string }
paths:
  /updates:
    get:
      summary: List updates since timestamp
      security: [ { ApiKeyAuth: [] } ]
      parameters:
        - { name: since, in: query, schema: { type: string, format: date-time } }
        - $ref: '#/components/parameters/Cursor'
        - $ref: '#/components/parameters/Limit'
      responses:
        '200':
          description: OK
          headers:
            Request-ID: { $ref: '#/components/headers/RequestID' }
            RateLimit-Remaining: { $ref: '#/components/headers/RateLimitRemaining' }
          content:
            application/json:
              schema:
                type: object
                properties:
                  ok: { type: boolean }
                  next_cursor: { type: string, nullable: true }
                  data: { type: array, items: { $ref: '#/components/schemas/Update' } }
        '429':
          description: Too Many Requests
          headers: { Retry-After: { $ref: '#/components/headers/RetryAfter' } }
          content: { application/json: { schema: { $ref: '#/components/schemas/Error' } } }
        '4XX':
          description: Client Error
          content: { application/json: { schema: { $ref: '#/components/schemas/Error' } } }
        '5XX':
          description: Server Error
          content: { application/json: { schema: { $ref: '#/components/schemas/Error' } } }
  /tasks:
    post:
      summary: Create a task (idempotent)
      security: [ { OAuth2: [tasks] } ]
      parameters:
        - in: header
          name: Idempotency-Key
          required: true
          schema: { type: string }
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [title]
              properties:
                title: { type: string }
                description: { type: string }
      responses:
        '201':
          description: Created
          content: { application/json: { schema: { type: object, properties: { ok: {type: boolean}, task: { $ref: '#/components/schemas/Task' } } } } }
        '202':
          description: Accepted (async)
          content: { application/json: { schema: { type: object, properties: { ok: {type: boolean}, status_url: { type: string, format: uri } } } } }
        '409':
          description: Conflict (duplicate idempotency key)
          content: { application/json: { schema: { $ref: '#/components/schemas/Error' } } }
        '4XX':
          description: Client Error
          content: { application/json: { schema: { $ref: '#/components/schemas/Error' } } }
        '5XX':
          description: Server Error
          content: { application/json: { schema: { $ref: '#/components/schemas/Error' } } }
```

#### Jobs endpoint (async)

```yaml
/jobs/{id}:
  get:
    summary: Get job status
    responses:
      '200':
        content:
          application/json:
            schema:
              type: object
              required: [id, status]
              properties:
                id: { type: string }
                status: { type: string, enum: [queued, running, succeeded, failed] }
                last_error: { type: string, nullable: true }
```

### Recipe — Web → Python handoff (short)

*Pointer:* Mirrors **Core Manual → Buttons & Actions → Web → Python handoff** (v1.3.5).

**Default filename:** `<slug>_<YYYY-MM-DD>.<ext>` (date in **Europe/Vilnius**).\
**Directories:** ingest → `/mnt/data/web_ingest/` · outputs → `/mnt/data/processed/`

**Exact steps**

1. 📥 **Fetch** the URL and save as `/mnt/data/web_ingest/<slug>_<YYYY-MM-DD>.<ext>`.
2. 🧮 **Process** offline:
   ```bash
   python /mnt/data/tools/process_web_ingest.py --input /mnt/data/web_ingest --output /mnt/data/processed
   ```
3. 🔍 **Review** artifacts: `<stem>_clean.csv`, `<stem>_summary.csv` under `/mnt/data/processed/`.
4. 🛡️ **(If exporting to spreadsheets)** guard against CSV formulas when opening.

**One‑liner chat trigger**

> Fetch  as . → Run recipe

---

### JSON variant examples

```python
from pathlib import Path
import json, pandas as pd
p = Path('/mnt/data/web_ingest/example_2025-09-05.json')

# 1) Array‑of‑objects JSON
try:
    df = pd.read_json(p)
except ValueError:
    # 2) {"meta": ..., "data": [...]} shape
    obj = json.loads(p.read_text(encoding='utf-8'))
    df = pd.json_normalize(obj, record_path='data',
                           meta=[["meta","source"], ["meta","fetched_at"]],
                           errors='ignore')

# 3) Deeper nesting with list record_path
# e.g., {"responses": [{"question_id": 1, "choices": [...]}, ...]}
# meta can be a list of dotted paths or list-of-lists
# df = pd.json_normalize(obj, record_path=['responses','choices'],
#                        meta=[["responses","question_id"], ["meta","source"]],
#                        errors='ignore')

# Write a clean CSV
# df.to_csv('/mnt/data/processed/example_2025-09-05_clean.csv', index=False)
```

**Slug rules (quick):** lowercase, digits, dashes only; no spaces; keep under 40 chars. Examples: `outages`, `statuspage_log`, `market-prices`.

---

### Agent Spec (template)

```
### Agent Spec
- Name:
- Command: Agent: <verb phrase>
- Schedule (iCal VEVENT):
- Inputs (data / tools):
- Steps (≤7, each ≤1 line):
- Outputs (files/notes):
- Guardrails: max 300 s, ask-before-write, read-only unless approved.
- Log target: /mnt/data/.agent_logs/<name>.jsonl
```

### Example Commands (reference)

```
Sync: tool→mirrors
Sync: mirrors→tool
Apply --dry-run /mnt/data/getting_started.md
Apply to disk /mnt/data/getting_started.md
Doctor --summary --gzip
Status
# Enforcement
python /mnt/data/tools/pre_apply_lint.py --target /mnt/data/mirror_mnt_data_tool.md --json
python /mnt/data/tools/rotate_artifacts.py --dry-run
# KPIs
python /mnt/data/tools/compute_kpis.py --write
# Agent
python /mnt/data/agents/kpi_ping.py --run-now
# Token estimator
python /mnt/data/tools/token_estimator.py /mnt/data/somefile.txt --window 196000 --output 2000 --headroom 0.10
# Token estimator (JSON, multi-file)
python /mnt/data/tools/token_estimator.py /mnt/data/file1.txt /mnt/data/file2.txt --json
# Web → Python handoff
python /mnt/data/tools/process_web_ingest.py -i /mnt/data/web_ingest -o /mnt/data/processed --guard-csv-injection -v
# Web → Python handoff (JSON deep paths)
python /mnt/data/tools/process_web_ingest.py -i /mnt/data/web_ingest -o /mnt/data/processed \
  --record-path responses.choices --meta responses.question_id --meta meta.source
```

---

## Appendix B — KPI wiring & alerts

### Wiring KPIs

- 🔧 **Script:** `/mnt/data/tools/compute_kpis.py`
- 📥 **Inputs (expected in ****\`\`****):**
  - 📄 `billing.csv` — columns: `date, amount, status` (EUR; status is one of {active, canceled}).
  - 📄 `ads_spend.csv` — columns: `date, spend`.
  - 📄 `new_customers.csv` — columns: `date, new_customers`.
  - 📄 `cohorts.csv` (optional) — cohort retention table.

**Examples:**

```
# billing.csv
2025-09-04,50.00,active
# ads_spend.csv
2025-09-04,120.00
# new_customers.csv
2025-09-04,3
```

**Pre‑validation (ingest)**

- 🧪 Reject files with **non‑ISO dates** or non‑numeric amounts; log row numbers.
- 🧰 Run `pre_apply_lint` with expected new size; abort on protected‑path violations.
- 🧾 Emit a short `ingest_summary.json` (rows accepted/rejected; reasons).

**Sampling windows & retention**

- ⏱️ **FRT:** daily **median** by date (Europe/Vilnius). Exclude auto‑responders/spam.
- 📆 **D30 resolution:** percent of tickets resolved within **30 calendar days**; compute on rolling 30‑day cohorts.
- 🗃️ **Retention:** keep raw daily aggregates **12 months**; keep monthly rollups **indefinitely**.

**Data quality rules**

- 📅 Dates are ISO `YYYY‑MM‑DD`; amounts are numeric (EUR); `status` ∈ {active, canceled}.
- 🔁 No duplicate dates within a file; missing days are allowed.
- 📝 D30 retention is measured on cohort end‑of‑window; note any method change in the changelog.

**Outputs**

- 🗓️ Daily metrics: `/mnt/data/metrics/<YYYY‑MM‑DD>.md`.
- 📈 Optional chart: `/mnt/data/metrics/<YYYY‑MM‑DD>_mrr.png` (if billing data present).
- 📁 Templates: installed at `/mnt/data/templates/`.

### Alerts & Quiet Hours

- ⚙️ **Config:** `/mnt/data/config/alerts.json`
  - `quiet_hours`: `{ start:"22:00", end:"07:00", tz:"Europe/Vilnius" }`
  - `channels`: `{ webhook_url:null, email:null }` (set one or both to enable push; with no network, alerts are queued locally).
- 📨 **Queue:** alerts are written to `/mnt/data/alerts/outbox.jsonl`.
- 📤 **Dispatch:** `python /mnt/data/tools/alert_dispatch.py --flush` prints `curl` commands (for webhook) or a plaintext email body you can copy into your mail client.
- 📊 **Thresholds:** CAC or D30 swing **>20%** (configurable in `alerts.json`).
- 🌙 **Quiet hours:** during quiet hours, alerts are queued, not flushed; use `--override-quiet-hours` to force.

### Dashboard (HTML)

- 🏗️ **Builder:** `/mnt/data/tools/build_dashboard.py`
- 🖥️ **Output:** `/mnt/data/dashboard/index.html`
- 📊 **Contents:** latest KPIs, last Doctor summary, last Apply manifest snippet, and (if available) the latest MRR chart image.
- ▶️ **Run:** `python /mnt/data/tools/build_dashboard.py`

---

## Appendix C — Agent Mode & Deep Research

### Agent Mode — quick‑start & quotas (card)

**Start:** Open **Agent mode** from the tools menu (or type `/agent`). State the **goal**, any **must‑use sources**, and **constraints** (time window, budget, accounts).\
**During run:** A visible browser executes steps. You can **approve/deny** actions, **pause/stop**, or **Take over browser** for sensitive inputs.\
**Deliverables:** Summary + any artifacts (docs, sheets, code). Agent may use **Code Interpreter** and **Connectors (read‑only)**.\
**Repeat/schedule:** After completion, choose daily/weekly/monthly; manage runs at **chatgpt.com/schedules**.

**Quotas (typical today):**

| Plan                      | Monthly agent requests                                                        | Notes                                                         |
| ------------------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------------- |
| **Plus**                  | **40**                                                                        | Only the initial agent request counts; follow‑ups/auth don’t. |
| **Pro**                   | **400**                                                                       | Same rule as Plus.                                            |
| **Business / Enterprise** | **40** *(or org‑configured; some flexible pricing list \~30 credits/message)* | Check your admin settings.                                    |

> Limits can change. Re‑verify in OpenAI help center and update this card during monthly link audits.

---

#### Operating rules (workspace)

- 🔀 **Agent vs plain chat:** Use Agent for multi‑step web+action workflows; otherwise plain chat or Deep Research.
- 🛡️ **Agent safety — 3 checks:** (1) Sensitive step? **Take over browser**. (2) Consequential write? **ask & log**. (3) Weird prompts? **pause and confirm**.
- 🤖 **Model picker:** Default **GPT‑5**; **o3** for heavy reasoning; **o4‑mini** for speed. *Note:* Canvas/images aren’t available in **GPT‑5 Pro**.
- 🌐 **Browse vs Deep Research:** ≤60 s quick browse for stable facts; Deep Research for volatile/high‑stakes topics.
- 🛑 **When to stop:** at **T+300 s**, on **Doctor/Status critical**, or when **preconditions fail** → return partial + next steps, stop.

### Deep Research Mode

**Use when**

- 🧭 The topic is uncertain, niche, or fast‑moving; decisions involve spend or time impact; any claim needs citations.

**Inputs (minimum)**

- 🧩 Topic/question; scope/time window; constraints (what to include/exclude); must‑use sources (optional).

**Process (≤7 steps)**

1. 🎯 Refine the objective into 2–3 concrete questions; set scope and time window.
2. 🔎 Draft 4–8 search queries; browse breadth with high‑quality sources first.
3. 🌐 Collect 8–12 **diverse, authoritative** sources; skip low‑quality or paywalled summaries.
4. 📌 Extract 5–10 key facts; label **stable** vs **volatile** and note disagreements.
5. 🧠 Synthesize a **Research Brief**: TL;DR, What’s Known, What’s Uncertain, and Implications/Next Steps.
6. 📚 Cite the 5 most load‑bearing facts with sources; avoid over‑quoting.
7. 💾 Save artifacts and stop (no background work).

**Outputs**

- 📄 `/mnt/data/research/<slug>/<ts>/brief.md` (the brief)
- 🔗 `/mnt/data/research/<slug>/<ts>/sources.json` (URLs and metadata)
- 🧾 `/mnt/data/research/<slug>/<ts>/evidence.csv` (claims ↔ citations)
- 🌐 `/mnt/data/research/website/<ts>/…` (website‑focused capture for SEO/IA tasks)

**Quality guardrails**

- 🧭 Relevance · Diversity · Trustworthiness · Accurate representation; show disagreements when present.
- ⏳ 300 s/turn limit; if it won’t fit, do a safe partial and stop.

**Commands**

- 🧠 `Deep Research: <topic> scope:<days> max-sources:<n>`
- 💾 `Save Research to disk`

**Pre‑code web pass (pointer):** Before any Python, do a ≤60s quick doc check (official sources). See **Core Manual → Boot Checklist 2a**.

### Query pack (template)

- 🔎 `<topic>` site\:docs.\* OR site:\*.org file\:pdf

- 🔎 `<topic>` "changelog" OR "release notes" site:\*.com

- 🔎 `<topic>` overview OR comparison (last 30 days)

- 🔎 `<topic>` standard OR guideline site:.gov OR site\:who.int

- 🔎 `<topic>` site\:docs.\* OR site:\*.org file\:pdf

- 🔎 `<topic>` "changelog" OR "release notes" site:\*.com

- 🔎 `<topic>` overview OR comparison (last 30 days)

- 🔎 `<topic>` standard OR guideline site:.gov OR site\:who.int

---

## Appendix D — Tools & Utilities

### Pre‑apply lint

- 📍 **Path:** `/mnt/data/tools/pre_apply_lint.py`
- 💻 **CLI:** `python /mnt/data/tools/pre_apply_lint.py --target <path> [--new-size <bytes>] [--json]`
- 🔍 **Checks:** target existence (optional), protected‑path violations, size‑delta warnings.

### Rotate artifacts

- 📍 **Path:** `/mnt/data/tools/rotate_artifacts.py`
- 💻 **CLI:** `python /mnt/data/tools/rotate_artifacts.py [--dry-run]`
- 🎯 **Purpose:** Enforce **Retention & Rotation** policy.

### Self‑Check

- 📜 **Script:** `/mnt/data/tools/self_check.py`
- 📝 **What it does:** runs `pre_apply_lint` (on a target you pass), `rotate_artifacts --dry-run`, and writes a short report to `/mnt/data/.doctor/self_check_<ts>.md`.
- ▶️ **Run:** `python /mnt/data/tools/self_check.py --target /mnt/data/mirror_mnt_data_tool.md`



### process\_web\_ingest.py (Web → Python handoff utility)

- 📍 **Path:** `/mnt/data/tools/process_web_ingest.py`
- 🎯 **Purpose:** Scan `/mnt/data/web_ingest/` for new files (**CSV/JSON/NDJSON**), produce `<stem>_clean.csv` + `<stem>_summary.csv` in `/mnt/data/processed/`.
- 💻 **CLI:**
  ```bash
  python /mnt/data/tools/process_web_ingest.py --input /mnt/data/web_ingest --output /mnt/data/processed \
    --guard-csv-injection --verbose
  # Deep JSON paths
  python /mnt/data/tools/process_web_ingest.py -i /mnt/data/web_ingest -o /mnt/data/processed \
    --record-path responses.choices --meta responses.question_id --meta meta.source
  ```
- **Options:**
  - 📌 `--record-path <dot.path>` (repeatable) — JSON array path (e.g., `responses.choices`).
  - 🧾 `--meta <dot.path>` (repeatable) — keep JSON meta fields (e.g., `meta.source`).
  - 🛡️ `--guard-csv-injection` — prefixes risky cells starting with `= + - @` or TAB.
  - 📦 `--chunksize N` — stream large CSVs in chunks.
  - 🔍 `--glob` — include patterns (default: `*.csv,*.json,*.ndjson,*.jsonl`).
  - 🗣️ `--verbose` — progress logs to stderr.
- **Outputs:**
  - 🧹 `*_clean.csv` — trimmed strings, deduped rows, optional CSV‑injection guard applied.
  - 📋 `*_summary.csv` — rows, columns, column names, dtype/nonnull/null%, basic min/max for numeric/datetime‑ish columns.

## Appendix E — ChatGPT Pro (workspace)

*Anchor: #appendix-e-chatgpt-pro · Last updated: 2025-09-05*

### At a glance

- 💡 **What you get:** unlimited access to **GPT‑5** and select legacy models, advanced voice, prioritized traffic.
- 🧰 **Guardrails:** "Unlimited" is usage‑policed by OpenAI Terms; **no account sharing**, **no scraping/abusive automation**.
- 🔌 **API is separate:** OpenAI API is billed separately (different quotas/billing).

### Model picker (Pro)

- 🤖 Default **GPT‑5**; switch to **o3** for heavy reasoning; **o4‑mini** for speed.
- 🛠️ **Tools note:** Canvas & image generation aren’t available with **GPT‑5 Pro**; use **GPT‑5 Thinking** (or another model) when you need Canvas/images.

### 90‑second setup checklist

1. ⚙️ Settings → Personalization → enable what you need (Memory optional).
2. 🔐 Data controls → set training opt‑out as desired.
3. 📌 Pin **Thinking**, **o3**, **o4‑mini** to the model picker.
4. 🗂️ Create a **Project** for persistent files.

### Setup → Smoke test (quick)

Prompt: "Summarize this page in 7 bullets and export a CSV with 5 key facts." Confirm: model choice sensible; CSV downloads.

### How we use Pro here

- 🤖 Default **GPT‑5**; **Thinking** for long context; **o3** for tough reasoning; **o4‑mini** for speed checks.
- 🚦 Avoid **GPT‑5 Pro** when working in **Canvas** or generating images.

### Quick comparison

| Mode            | Best for                        | Context        | Notes                              |
| --------------- | ------------------------------- | -------------- | ---------------------------------- |
| GPT‑5 (default) | General tasks                   | tier‑dependent | Auto‑router may switch to Thinking |
| GPT‑5 Thinking  | Long context, careful reasoning | 196K           | Full tool access incl. Canvas      |
| GPT‑5 Pro       | Research‑grade accuracy         | 196K           | No Canvas/images                   |
| o3              | Heavy reasoning                 | large          | Slower, higher accuracy            |
| o4‑mini         | Speed                           | smaller        | Very fast for drafts               |

### Review cadence

- 🔁 Re‑check plan limits monthly; update this appendix when OpenAI changes quotas or tools.

### References

- 🔗 See Core **Document Conventions → Plan context (Pro)**.

## Appendix H — Memory templates

> **Audit status:** **ENABLED** — logging approved saves/forgets to `/mnt/data/.agent_logs/memory_log.jsonl`.

### Purpose

Ready-to-paste phrases and checklists for using ChatGPT Memory under the **Native Memory Policy**.

### Gating phrases

- 🗳️ Propose memory from this message
- 💾 Save A, B / Save all / No
- ❓ What do you remember about me?
- 🧹 Forget  / Forget last / Forget everything
- 🧾 enable memory audit / disable memory audit

### Starter memory pack (paste one per line)

Remember this: Call me **Viss**. My timezone is **Europe/Vilnius**. Remember this: My 2025 goal is **€3,200 MRR by 2025-10-31**. Remember this: Track **MRR, CAC/LTV, D30 retention** as primary KPIs. Remember this: Writing style **concise/straight**; **ask before any write**; browse for fresh info. Remember this: Default currency **EUR**; dates **YYYY‑MM‑DD**. Remember this: Use separate canvases per file; **Auto‑apply (100%) OFF** unless I enable it.

### Allowed vs never save (quick card)

- ✅ **Allowed:** stable identity/preferences, long-term goals, non-sensitive defaults.
- ⛔ **Never:** secrets, credentials, client PII, one-time codes, regulated/sensitive data.

### Audit log (optional)

When audit is enabled, saves/forgets append JSON lines to: `/mnt/data/.agent_logs/memory_log.jsonl` Schema (example):

```json
{"ts":"2025-09-05T12:34:56+03:00","action":"save","items":["Viss","EUR","Europe/Vilnius"],"who":"Viss"}
```

*Built from Core v1.3.5*



---

## Appendix F — Brave + ChatGPT performance checklist (browser tuning)

- 🔄 Keep Brave up to date; restart after updates.
- 🧩 Limit heavy extensions on ChatGPT tabs; test with a clean profile if laggy.
- 🖥️ Toggle hardware acceleration if you see rendering glitches.
- 🗑️ Clear cached images/files when debugging UI oddities.
- 🗂️ For long sessions with many files, split into **Projects**; rotate canvases when they grow large.

## Appendix G — Context, Tokens & Limits

**Scope:** ChatGPT product (UI) + Projects + Canvas; brief note on API.\
**Last verified:** 2025-09-05.\
**Applies to our plan:** **Pro** (unless noted).

### A) Context windows — ChatGPT (UI)

- 🔄 **Thinking / Pro:** **196K tokens** max context.
- ⚡ **Instant:** **32K tokens** max context.
- ℹ️ **Note:** Context window = input **+** output. Hitting the cap can silently truncate earlier turns.

### B) File uploads — ChatGPT (UI)

- 💾 **Per‑file size (all types):** **512 MB**.
- 🧮 **Text & document token cap (per file):** **2,000,000 tokens**. *(Spreadsheets/CSVs: token cap doesn’t apply; instead ****\~50 MB**** size ceiling depending on row size.)*
- 🖼️ **Images:** **≤20 MB each**.
- 💽 **User storage quota:** **10 GB** per end‑user.
- 📁 **Projects — files per project:** **Pro/Business/Enterprise: 40** · **Go/Plus/Edu: 25** · **Free: 5**.
- ⚙️ **Projects — concurrency:** upload **≤10 files at once**.
- 🧰 **Projects — count:** you can create **unlimited** projects.

### C) Canvas specifics

- 📝 Canvas is an editing surface; **no separate published length limit** beyond the model’s context window and UI practicalities.
- 🧠 **Model caveat:** **Canvas is not available with GPT‑5 Pro.** If you need Canvas, switch to another model (e.g., Thinking, 4.1, 4o).
- 🗂️ Version history lets you restore prior edits; prefer **one doc per canvas** and rotate when large.

### D) API context (developer note)

- 🔭 The **OpenAI API** (separate from ChatGPT UI) offers **longer contexts** on certain models, e.g., **GPT‑4.1 up to \~1,000,000 tokens**. This does **not** change ChatGPT UI limits.

### E) Token math — quick conversions (English)

- 📏 **Rule of thumb:** **1 token ≈ 4 chars ≈ ¾ word**.
- 📚 **196K tokens ≈ \~147K words** (≈ 800–1,000 kB of plain text).
- 📦 **2M tokens ≈ \~1.5M words** (\~8–10 MB plain text), varies by language/whitespace.

### F) How to avoid limits (our practice)

1. 🧠 **Pick the right mode:** use **Thinking/Pro** for long context; keep **Instant** for short tasks.
2. ✂️ **Chunk big docs:** split by section; for PDFs, prefer extracted text over image‑heavy scans.
3. 🗂️ **Stage in Projects + Canvas:** keep one large file per canvas; when it grows, **start a new canvas** and link back.
4. 🧮 **Estimate before pasting:** apply the 1-token≈¾-word rule; keep total (history + files + reply) under the window.
5. 🧾 **Summarize & link:** replace long history with a short recap; keep raw source files attached.
6. 🧰 **Avoid giant tool schemas:** (API) keep any single schema **<\~300K tokens**; split tools.
7. 🩺 **Monitor symptoms:** model forgetting early turns, refused replies, or truncated outputs → reduce context or rotate canvases.

### G) Maintenance

- 🔁 Limits **change**. Re‑verify monthly; update this appendix when OpenAI revises plan/model limits.

### H) Token estimator — rule‑of‑thumb

- 🔢 **Conversions:** 1 token ≈ 4 chars ≈ ¾ word (English). Non‑English and code may differ.
- 🧮 **Formulas:**
  - `tokens_from_words ≈ round(words / 0.75)`
  - `tokens_from_chars ≈ round(chars / 4)`
  - `safe_input_budget(window, desired_output, headroom=0.10) ≈ floor(window×(1−headroom) − desired_output)`
- 🧪 **Quick check (shell):** `wc -w file.txt` → words → divide by 0.75. Or `wc -m file.txt` → chars → divide by 4.
- 🧾 **Examples:**
  - 2,500‑word draft → ≈ **3,333 tokens**.
  - 196K window with a 2,000‑token reply → safe input ≈ **floor(196000×0.9 − 2000) = 174,400 tokens** (≈ **131k words**).

### I) Tools — local helpers

- 💻 **CLI:** `/mnt/data/tools/token_estimator.py`
  - 🧪 Example:
    ```bash
    python /mnt/data/tools/token_estimator.py /mnt/data/somefile.txt --window 196000 --output 2000 --headroom 0.10
    ```
- 📊 **Spreadsheet (import to Google Sheets):** `/mnt/data/tools/Token Estimator (Import to Google Sheets).xlsx`

*Built from Core v1.3.5*



---

## Appendix I — Intercom App (Unlisted → Listed)

**Purpose:** pilot installs fast via **Unlisted** app, then graduate to **Listed** for App Store distribution.

**Pre‑reqs**\
• 🛠️ Intercom Developer Hub access • 🖼️ App icon (512×512) • 📧 Company support email • 🔐 OAuth redirect URL(s).

**Scopes (typical)**\
`read/write:conversations`, `read:users`, `read:admin.conversations`, `write:admin.conversations`, `write:conversations/replies` (adjust to minimum needed).

**Unlisted flow (pilot)**

1. 🚀 Create **Public app → Unlisted** in Developer Hub.
2. 🔐 Configure **OAuth** (client id/secret, redirects).
3. 🧪 Install to our workspace → smoke test (read thread, post reply).
4. 🔗 Share **direct install URL** with pilot customers; keep a 1‑pager with steps/permissions.

**Prep to List (App Store)**

- 🧭 **Start Guide** (post‑install): setup steps (connect KB, toggle assist vs auto, quality checks).
- 📝 **Listing copy**: value prop, features, required permissions (plain language).
- 🖼️ **Assets**: 2–5 images **≥1600×1000 (8:5)**, PNG, <21 MB (messenger reply, dashboard, settings).
- 🔗 **Support links**: website, privacy, support email.
- 🎬 **Demo video** (optional): OAuth install → first answer → how to disable.

**Submit for review**\
Fill all required fields; upload images; provide install URL; submit. Track status in Dev Hub.

**How to verify**

- ✅ A pilot customer installs via **Unlisted** link and we can post replies.
- 🧪 Draft listing passes field validation; images render correctly.
- 🧭 Start Guide opens post‑install.
- 🔗 Drive assets folder: [https://drive.google.com/drive/folders/1RvewW11H0yDmtHrqgLIb3Q8SIyg-oe3E?usp=drive\_link](https://drive.google.com/drive/folders/1RvewW11H0yDmtHrqgLIb3Q8SIyg-oe3E?usp=drive_link)

*Source: Growth Plan — 90‑Day Path to €3,200 MRR (Executive Summary) · 2025‑09‑06.*

---

## Appendix J — Zendesk Marketplace Submission

**Purpose:** package autopilot for Zendesk; start **Preview (private)**, then **Public** listing.

**Choices**\
• 🧰 **Support App (agent UI)** via Zendesk Apps Framework • 🔌 **Background integration** (server API calls).\
**Dev tools**: 🧪 ZAT (Zendesk Apps Tools) for scaffold & validation.

**Platform requirements**

- 🔐 **OAuth (mandatory)**: register a **global OAuth client**; **no API tokens/basic auth** for public apps (**block submission if present**).
- 🧾 **Request headers**: include **required** Marketplace headers when calling Zendesk APIs.
- 📦 **Packaging**: `manifest.json`, icon (≥256×256), bundle ZIP; README as needed.
- 💳 **Pricing/trials**: optional paid plan via Stripe; set free trial (e.g., 14 days).
- 👀 **Preview mode**: enable to share private install link with design partners.
- ⏳ **Review window**: expect \~1–3 weeks for new apps; \~1–2 weeks for updates.

**Submission checklist**

1. 📝 Register developer org; create app in portal.
2. ⬆️ Upload ZIP → fix validator errors/warnings.
3. 🗂️ Select **categories**, write short + long description.
4. 💰 Configure pricing (free/paid) + trial cooldown if used.
5. ➕ Provide “additional fees” link if using outcome pricing externally.
6. 📤 Submit; monitor dashboard; respond to reviewer notes.

- 🔗 Drive assets folder: [https://drive.google.com/drive/folders/1RvewW11H0yDmtHrqgLIb3Q8SIyg-oe3E?usp=drive\_link](https://drive.google.com/drive/folders/1RvewW11H0yDmtHrqgLIb3Q8SIyg-oe3E?usp=drive_link)

**How to verify**

- ✅ Preview link installs successfully in a sandbox account.
- ✅ ZIP passes validator; listing fields complete; Stripe connected (if paid).
- ✅ Post‑install card renders (if agent UI).

*Source: Growth Plan — 90‑Day Path to €3,200 MRR (Executive Summary) · 2025‑09‑06.*

---

## Appendix K — Notion Template “Support Autopilot Kit”

**Purpose:** capture organic demand via Notion’s Template Gallery; provide immediate value.

**Quality bar**\
Useful, differentiated, scalable; clear **in‑template instructions**; no private data.

**Build & polish**

- 🗃️ Databases: Tickets/FAQs/Macros/Automation Log; dashboard page.
- 📣 Add callouts: “Duplicate this template then follow Setup.”
- 🖼️ Consistent icons/cover; remove placeholders.

**Enable duplication**\
Share top page to web → **Allow duplicate as template**. Copy public link.

**Submission pack**

- 🏷️ Name, 1–2 sentence description, category.
- 🖼️ 2–3 tasteful screenshots; avoid sensitive content.
- 🔗 Optional: concise note that it pairs with an AI autopilot (non‑promotional).
- 📬 Submit via Notion’s template form; keep a copy of text here.

**How to verify**

- ✅ Public link opens; “Duplicate” works.
- ✅ Submission text/images stored in this appendix.
- ✅ Listing visible in category once approved.

*Source: Growth Plan — 90‑Day Path to €3,200 MRR (Executive Summary) · 2025‑09‑06.*

---

## Appendix L — Outcome‑Based Pricing & ROI

**Pricing table**

| Plan                   | Includes                                          | Pricing                                | Notes                           |
| ---------------------- | ------------------------------------------------- | -------------------------------------- | ------------------------------- |
| Pilot (14 days)        | 1 KPI target, full autopilot                      | **Free if KPI missed**                 | Converts to paid on success     |
| Outcome — Standard     | AI resolutions; monthly KPI report; email support | **€0.90 / AI resolution** (min 50/mo)  | Outcome = ticket resolved by AI |
| Outcome — Premium      | Std + on‑call human QA; quarterly review          | **€1.20 / AI resolution** (min 100/mo) | Higher‑touch service            |
| Add‑on: Human takeover | Live agent fallback pool                          | **€300/mo + €0.50/handoff**            | Optional safety valve           |

**ROI inputs**\
Tickets/month, agent cost, share automated (%), baseline FRT/resolution rate, CSAT impact.

**ROI sketch**\
`Monthly AI cost = (AI_resolutions × €/resolution)` vs `human capacity cost`. Use dashboard to show FRT ↓ and % resolved by AI.

**Invoice copy blocks**

- 🧾 “Billed per **AI resolution**; non‑resolutions are **not charged**.”
- 🧾 “Includes monthly **KPI impact report**.”

**How to verify**

- 🧪 Pricing renders in site/pricing deck; calculators produce sane results on two customer scenarios.
- 🔗 Invoices show resolution counts + link to KPI report.

*Source: Growth Plan — 90‑Day Path to €3,200 MRR (Executive Summary) · 2025‑09‑06.*

---

## Appendix M — Evaluator Loop (LangSmith, TruLens, OpenAI Evals)

**Goal:** keep answers accurate, safe, and helpful; make quality visible.

**Instrumentation (daily)**

- 🧵 **LangSmith traces**: log every AI reply; run **LLM‑as‑judge** on correctness/helpfulness; flag < threshold.
- 📊 **Dash summary**: total AI replies, pass‑rate %, flagged count.

**Metrics & thresholds**

- ✅ **Pass‑rate** ≥ **95%** (auto‑checks).
- 📚 **Groundedness** (TruLens) ≥ **80%** avg; track Context relevance, Toxicity = 0%.
- 🙂 **Sentiment/CSAT proxy** if available.

**Weekly QA cadence**

- 🔎 Review flagged traces; add FAQs; adjust prompts/retrieval.
- 🧪 Compare model/prompt variants on a held‑out set.

**CI gate (before deploy)**

- 🧪 Run **OpenAI Evals** suite on regression scenarios; block deploy on critical failures.
- 📁 Store eval reports; link from release notes.

**Client‑visible card**\
“**Autopilot Quality** — This week: **{pass\_rate}%** pass (auto‑checks), **{flagged}** flagged and corrected. Trend: {sparkline}.”

**How to verify**

- 📈 Dash shows pass‑rate tile and flagged list; weekly QA notes filed.
- ✅ CI blocks on a seeded failure; green after fix.

*Source: Growth Plan — 90‑Day Path to €3,200 MRR (Executive Summary) · 2025‑09‑06.*

---

## Appendix N — EU AI Act: Transparency & Labeling

**What to do (deployers)**

- 🏷️ **Label agent:** in chat UIs, name + badge “AI Assistant”; start message “You’re chatting with an AI assistant.”
- 📨 **Mark AI outputs:** add hidden or footer markers in AI‑generated replies/emails; maintain consistency.
- 🔎 **Disclose** in privacy page how AI is used; provide contact for issues.
- 📅 **Dates to track:** **Aug 2025** (provider duties upstream) • **Aug 2026** (deployer transparency/labeling fully in scope).

**Widget notes**

- 💬 **Intercom:** bot avatar/name conveys AI; include first message disclosure; allow human handoff.
- 🏷️ **Zendesk:** macros for AI footer; tag AI replies; add “AI” badge if custom UI.

**How to verify**

- 👀 Visual audit: disclosures visible in chat/email; privacy page updated.
- 🔍 Spot‑check: a random AI email includes the marker/footer.

*Source: Growth Plan — 90‑Day Path to €3,200 MRR (Executive Summary) · 2025‑09‑06.*

---

## Appendix O — Evidence Pack (Index)

**Files**

- 📄 Evidence table CSV → `/evidence/best_moves_evidence_<YYYY‑MM‑DD>.csv`
- 📚 Source pack (top‑12 sources) → link list in this appendix.

**Process**

- 🔁 Update monthly (link audit).
- 🏷️ Mark items **Stable** vs **Volatile**.

**How to verify**

- ✅ CSV opens; at least 12 sources listed; next audit date set.

*Source: Growth Plan — 90‑Day Path to €3,200 MRR (Executive Summary) · 2025‑09‑06.*

---

## Appendix P — Accessibility & Performance (moved)

(See Launch Sweep for Accessibility & Performance specifics.)

- 🧭 **Performance key metric:** **INP ≤200 ms @ p75** (replaces FID).
- ♿ **Accessibility baseline:** **WCAG 2.2 AA**, incl. 2.5.7 Dragging Movements, 2.5.8 Target Size (Minimum), 3.3.8 Accessible Authentication (Minimum).
- 🔎 **SEO/JSON‑LD pointer:** Prefer **Organization** (Home) and **Product/FAQ** (Pricing). Do **not** require **WebSite → SearchAction** (deprecated sitelinks). See Launch Sweep → **E) Website — SEO/JSON‑LD & Publishing**.



## Appendix Index

- 📑 A — Specs & Templates
- 📑 B — KPI wiring & alerts
- 📑 C — Agent Mode & Deep Research
- 📑 D — Tools & Utilities
- 📑 E — ChatGPT Pro (workspace)
- 📑 F — Brave + ChatGPT performance checklist (browser tuning)
- 📑 G — Context, Tokens & Limits
- 📑 H — Memory templates
- 📑 I — Intercom App (Unlisted → Listed)
- 📑 J — Zendesk Marketplace Submission
- 📑 K — Notion Template “Support Autopilot Kit”
- 📑 L — Outcome‑Based Pricing & ROI
- 📑 M — Evaluator Loop (LangSmith, TruLens, OpenAI Evals)
- 📑 N — EU AI Act: Transparency & Labeling
- 📑 O — Evidence Pack (Index)
- 📑 P — Accessibility & Performance (moved)



Source: Ops Library — Appendices · canvas


# Project — Support Autopilot KPI Pilot Kit (Sandbox Build v1)

**Goal.** Ship a self‑contained KPI pack (daily metrics, dashboard, alerts) and two agents (KPI Ping, Competitor Sweep) that run safely inside this sandbox.

---

## 1) Scope

- **In:** Offline Python runs (≤300 s), local files in `/mnt/data`, Canvas docs, Agent mode with guardrails, light web research (citations) when invoked.
- **Out:** External services, background daemons, networked Python, secrets/PII.

## 2) Deliverables

1. **Daily metrics file:** `/mnt/data/metrics/<YYYY-MM-DD>.md`
2. **HTML dashboard:** `/mnt/data/dashboard/index.html`
3. **Alerts queue:** `/mnt/data/alerts/outbox.jsonl`
4. **Agent specs:** saved in this canvas (KPI Ping, Competitor Sweep)
5. **Runbook commands:** copy‑paste ready (below)
6. **Verification evidence:** short checklist + doctor/status summary

## 3) Directory & file map

```
/mnt/data/
  metrics/                 # daily KPI .md + optional charts
  dashboard/               # index.html (lightweight)
  alerts/
    outbox.jsonl           # queued alerts (quiet hours)
  config/
    alerts.json            # thresholds, quiet hours, channels
  templates/               # report/dashboard templates (optional)
  tools/                   # helper scripts (if present)
```

## 4) Agents (ready to use)

### Agent Spec — KPI Ping (daily)

- **Name:** KPI Ping
- **Command:** Agent: KPI Ping — compute and write today’s metrics, update dashboard, queue alerts
- **Schedule (iCal VEVENT):**
  ```
  BEGIN:VEVENT
  RRULE:FREQ=DAILY;BYHOUR=9;BYMINUTE=0;BYSECOND=0
  END:VEVENT
  ```
- **Inputs:** `/mnt/data/billing.csv`, `/mnt/data/ads_spend.csv`, `/mnt/data/new_customers.csv` (optional `/mnt/data/cohorts.csv`), `/mnt/data/config/alerts.json`
- **Steps (≤7):**
  1. Validate CSVs (ISO dates, numeric amounts)
  2. Compute MRR, CAC, D30 retention
  3. Write `/mnt/data/metrics/<today>.md`
  4. Build/update `/mnt/data/dashboard/index.html`
  5. Evaluate thresholds; write alert line(s) to `/mnt/data/alerts/outbox.jsonl`
  6. Summarize run (rows, metrics) in the day’s .md
  7. Stop (no background work)
- **Outputs:** the three deliverables above
- **Guardrails:** max 300 s; read/write only to listed paths; ask before any new writes
- **Log target:** `/mnt/data/.agent_logs/kpi_ping.jsonl` (optional)

### Agent Spec — Competitor Sweep (ad‑hoc / weekly)

- **Name:** Launch Sweep — Agencies & Platforms
- **Command:** Agent: Launch Sweep v2 — collect 3–5 EU Notion/automation agencies (entry pricing, 2 differentiators) + 3–5 platforms (free plan + entry price); save brief
- **Schedule:** optional weekly; start on demand first
- **Inputs:** web pages (pricing/directories); this canvas for copy blocks
- **Steps (≤7):**
  1. Draft search queries; collect 6–10 reputable sources
  2. Extract prices, plans, differentiators
  3. Write brief `/mnt/data/research/vissai/agencies_<YYYY-MM-DD>.md`
  4. Write brief `/mnt/data/research/vissai/platforms_<YYYY-MM-DD>.md`
  5. Add citations list (max 10)
  6. Save and stop
  7. (Optional) append 3 DM/email copy blocks
- **Outputs:** two markdown briefs (+ sources JSON if desired)
- **Guardrails:** read‑only browsing; no background work; ≤300 s/turn
- **Log target:** `/mnt/data/.agent_logs/launch_sweep.jsonl` (optional)

---

## 5) Configuration (defaults)

- **Quiet hours:** 22:00–07:00 Europe/Vilnius (alerts are queued)
- **Alert thresholds:** 20% swing for CAC or D30 retention (adjustable)
- **Currency:** EUR; **date format:** `YYYY-MM-DD`

Sample `/mnt/data/config/alerts.json`:

```json
{
  "quiet_hours": {"start": "22:00", "end": "07:00", "tz": "Europe/Vilnius"},
  "thresholds": {"cac_pct_swing": 20, "d30_pct_swing": 20},
  "channels": {"webhook_url": null, "email": null}
}
```

---

## 6) Runbook — copy‑paste commands

> Use these if the helper scripts already exist; otherwise skip to “Manual run (fallback).”

**Compute KPIs & write outputs**

```
python /mnt/data/tools/compute_kpis.py --write
```

**Build dashboard**

```
python /mnt/data/tools/build_dashboard.py
```

**Dispatch queued alerts (outside quiet hours)**

```
python /mnt/data/tools/alert_dispatch.py --flush
```

**Doctor (health check) & Status**

```
Doctor --summary --gzip
Status
```

### Manual run (fallback)

1. Create `/mnt/data/metrics/<today>.md`; include MRR, CAC, D30 retention
2. Create/refresh `/mnt/data/dashboard/index.html` with latest KPIs
3. If thresholds exceeded, append a JSON line to `/mnt/data/alerts/outbox.jsonl`

---

## 7) Data quality rules (strict)

- Dates are ISO `YYYY-MM-DD`; amounts are numeric (EUR)
- `billing.csv` status ∈ {`active`, `canceled`}
- No duplicate dates within a file; missing days allowed

---

## 8) Verification checklist (DoD)

- `Apply --dry-run` shows **CHANGE** for today’s metrics file
- Today’s metrics file exists and is non‑empty
- Dashboard renders latest KPIs
- Synthetic alert test appends a line to `alerts/outbox.jsonl`
- Latest **Doctor → Status** report is clean (crit=0, err=0, warn=0 allowed only if acknowledged)

---

## 9) Risks & mitigations

- **Missing CSVs** → create stub rows; run with sample data; document assumptions
- **Long runs (>300 s)** → chunk work, skip charting, write partial then stop
- **Protected paths** → confirm before any new writes; keep changes reversible

---

## 10) Definition of done

- Metrics for today written; dashboard updated; at least one alert can queue; verification passes; next steps listed

---

## 11) Next steps / extensions

- Add small MRR chart image `/mnt/data/metrics/<YYYY-MM-DD>_mrr.png`
- Enable weekly competitor sweep (auto‑save briefs)
- Add evaluator pass‑rate tile to the dashboard when traces exist

---

## Appendix — Quick copy blocks

**DM opener (LinkedIn/Email)**

> We run a 14‑day pilot that cuts **First Response Time \~30%** with an AI support autopilot. If we don’t hit the KPI, it’s free. Worth a 20‑min call?

**Email subject**

> Cut FRT \~30% in 14 days (quick idea)

---

## Appendix — Paths & filenames (canonical)

- Daily metrics: `/mnt/data/metrics/<YYYY-MM-DD>.md`
- Dashboard: `/mnt/data/dashboard/index.html`
- Alerts queue: `/mnt/data/alerts/outbox.jsonl`
- Config: `/mnt/data/config/alerts.json`
- Research briefs: `/mnt/data/research/vissai/*`

---

**Owner:** Viss\
**Timezone:** Europe/Vilnius\
**Session rules:** no background work; ask before protected writes; keep diffs reversible.


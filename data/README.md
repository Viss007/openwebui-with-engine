# Workspace Data Directory

This directory contains the KPI monitoring workspace implementation as specified in `support_autopilot_kpi_pilot.md`.

## Directory Structure

```
data/
├── metrics/              # Daily KPI markdown reports
├── dashboard/            # Generated HTML dashboard
├── alerts/               # Alert queue (outbox.jsonl)
├── config/               # Configuration files
├── templates/            # Report/dashboard templates (optional)
├── tools/                # Helper scripts
├── .agent_logs/          # Agent execution logs (optional)
└── research/             # Research briefs and competitive analysis
    └── vissai/          # Viss AI specific research
```

## Tools

### compute_kpis.py

Computes KPIs (MRR, CAC, D30 Retention) from CSV files.

**Usage:**
```bash
# Compute and display KPIs
python data/tools/compute_kpis.py

# Compute and write to metrics file
python data/tools/compute_kpis.py --write

# With verbose output
python data/tools/compute_kpis.py --write --verbose
```

**Required CSV files:**
- `billing.csv`: date, amount, status (active/canceled)
- `ads_spend.csv`: date, spend
- `new_customers.csv`: date, new_customers
- `cohorts.csv` (optional): cohort retention data

**Output:**
- `metrics/<YYYY-MM-DD>.md`: Daily metrics report

### build_dashboard.py

Generates an HTML dashboard from metrics files.

**Usage:**
```bash
# Build dashboard
python data/tools/build_dashboard.py

# With verbose output
python data/tools/build_dashboard.py --verbose

# Include more days in charts
python data/tools/build_dashboard.py --days 14
```

**Output:**
- `dashboard/index.html`: Interactive HTML dashboard

### alert_dispatch.py

Manages alert queue with quiet hours support.

**Usage:**
```bash
# Check and dispatch alerts (respects quiet hours)
python data/tools/alert_dispatch.py

# Dispatch all alerts regardless of quiet hours
python data/tools/alert_dispatch.py --flush

# Dry run (show what would be dispatched)
python data/tools/alert_dispatch.py --dry-run --verbose
```

**Configuration:**
- `config/alerts.json`: Alert thresholds, quiet hours, notification channels

## Configuration

### alerts.json

```json
{
  "quiet_hours": {
    "start": "22:00",
    "end": "07:00",
    "tz": "Europe/Vilnius"
  },
  "thresholds": {
    "cac_pct_swing": 20,
    "d30_pct_swing": 20
  },
  "channels": {
    "webhook_url": null,
    "email": null
  }
}
```

## Quick Start

1. **Prepare CSV data files** with your billing, ads spend, and customer data
2. **Compute KPIs**: `python data/tools/compute_kpis.py --write`
3. **Build dashboard**: `python data/tools/build_dashboard.py`
4. **View dashboard**: Open `data/dashboard/index.html` in a browser

## Running Daily

You can set up a cron job or scheduled task to run these tools daily:

```bash
#!/bin/bash
cd /path/to/openwebui-with-engine
python data/tools/compute_kpis.py --write
python data/tools/build_dashboard.py
python data/tools/alert_dispatch.py
```

## Data Format

All dates should be in ISO format: `YYYY-MM-DD`
All amounts should be numeric (EUR by default)

### billing.csv
```csv
date,amount,status
2025-09-01,800.00,active
2025-09-02,850.00,active
```

### ads_spend.csv
```csv
date,spend
2025-09-01,100.00
2025-09-02,120.00
```

### new_customers.csv
```csv
date,new_customers
2025-09-01,3
2025-09-02,4
```

## Integration with Engine

These tools can be integrated with the task runner system in `engine/task_runner.py` for automated execution.

## References

- `support_autopilot_kpi_pilot.md`: Full specification
- `business_canvas_raw.md`: Business context and KPI targets
- `ops_library_appendices_raw.md`: Detailed operational procedures

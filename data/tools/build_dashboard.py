#!/usr/bin/env python3
"""
Build HTML dashboard from metrics files.

Reads daily metrics markdown files and generates a dashboard HTML page.
"""

import argparse
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


def parse_metrics_file(filepath: Path) -> Optional[Dict]:
    """Parse metrics from markdown file."""
    if not filepath.exists():
        return None
    
    content = filepath.read_text()
    metrics = {}
    
    # Extract date from filename
    metrics['date'] = filepath.stem
    
    # Parse MRR
    mrr_match = re.search(r'\*\*MRR[^:]*:\*\*\s*€?([\d,]+\.?\d*)', content)
    if mrr_match:
        metrics['mrr'] = float(mrr_match.group(1).replace(',', ''))
    
    # Parse CAC
    cac_match = re.search(r'\*\*CAC[^:]*:\*\*\s*€?([\d,]+\.?\d*)', content)
    if cac_match:
        metrics['cac'] = float(cac_match.group(1).replace(',', ''))
    
    # Parse D30 Retention
    d30_match = re.search(r'\*\*D30 Retention[^:]*:\*\*\s*([\d,]+\.?\d*)%?', content)
    if d30_match:
        metrics['d30_retention'] = float(d30_match.group(1).replace(',', ''))
    
    return metrics if len(metrics) > 1 else None


def load_recent_metrics(metrics_dir: Path, days: int = 7) -> List[Dict]:
    """Load recent metrics files."""
    metrics_list = []
    
    for i in range(days):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        metrics_file = metrics_dir / f'{date}.md'
        metrics = parse_metrics_file(metrics_file)
        if metrics:
            metrics_list.append(metrics)
    
    return list(reversed(metrics_list))


def generate_dashboard_html(metrics_list: List[Dict], output_path: Path) -> None:
    """Generate dashboard HTML from metrics data."""
    
    # Get latest metrics
    latest = metrics_list[-1] if metrics_list else {}
    
    # Calculate trends
    trend_mrr = ''
    trend_cac = ''
    trend_d30 = ''
    
    if len(metrics_list) >= 2:
        prev = metrics_list[-2]
        
        if 'mrr' in latest and 'mrr' in prev:
            mrr_change = ((latest['mrr'] - prev['mrr']) / prev['mrr']) * 100 if prev['mrr'] > 0 else 0
            trend_mrr = f"<span class='trend {'up' if mrr_change > 0 else 'down'}'>{mrr_change:+.1f}%</span>"
        
        if 'cac' in latest and 'cac' in prev:
            cac_change = ((latest['cac'] - prev['cac']) / prev['cac']) * 100 if prev['cac'] > 0 else 0
            trend_cac = f"<span class='trend {'down' if cac_change < 0 else 'up'}'>{cac_change:+.1f}%</span>"
        
        if 'd30_retention' in latest and 'd30_retention' in prev:
            d30_change = ((latest['d30_retention'] - prev['d30_retention']) / 
                         prev['d30_retention']) * 100 if prev['d30_retention'] > 0 else 0
            trend_d30 = f"<span class='trend {'up' if d30_change > 0 else 'down'}'>{d30_change:+.1f}%</span>"
    
    # Build data for charts (last 7 days)
    dates = [m['date'] for m in metrics_list[-7:]]
    mrr_values = [m.get('mrr', 0) for m in metrics_list[-7:]]
    cac_values = [m.get('cac', 0) for m in metrics_list[-7:]]
    d30_values = [m.get('d30_retention', 0) for m in metrics_list[-7:]]
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KPI Dashboard - Viss AI</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        header {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        h1 {{
            color: #333;
            font-size: 2rem;
            margin-bottom: 5px;
        }}
        
        .subtitle {{
            color: #666;
            font-size: 0.9rem;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .metric-card {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s;
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }}
        
        .metric-label {{
            color: #666;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 10px;
        }}
        
        .metric-value {{
            font-size: 2.5rem;
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }}
        
        .metric-trend {{
            font-size: 0.875rem;
        }}
        
        .trend {{
            padding: 2px 8px;
            border-radius: 4px;
            font-weight: 600;
        }}
        
        .trend.up {{
            background: #d4edda;
            color: #155724;
        }}
        
        .trend.down {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .chart-container {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }}
        
        .chart-title {{
            font-size: 1.2rem;
            font-weight: 600;
            color: #333;
            margin-bottom: 15px;
        }}
        
        .simple-chart {{
            display: flex;
            align-items: flex-end;
            justify-content: space-around;
            height: 200px;
            border-bottom: 2px solid #e0e0e0;
            border-left: 2px solid #e0e0e0;
            padding: 10px 0;
        }}
        
        .bar {{
            flex: 1;
            margin: 0 5px;
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
            border-radius: 4px 4px 0 0;
            position: relative;
            transition: all 0.3s;
        }}
        
        .bar:hover {{
            opacity: 0.8;
        }}
        
        .bar-label {{
            position: absolute;
            bottom: -25px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 0.7rem;
            color: #666;
            white-space: nowrap;
        }}
        
        .bar-value {{
            position: absolute;
            top: -25px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 0.75rem;
            font-weight: 600;
            color: #333;
            white-space: nowrap;
        }}
        
        footer {{
            text-align: center;
            color: white;
            margin-top: 30px;
            font-size: 0.875rem;
        }}
        
        .timestamp {{
            background: white;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            color: #666;
            font-size: 0.875rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 KPI Dashboard</h1>
            <p class="subtitle">Viss AI - Support Autopilot Performance</p>
        </header>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Monthly Recurring Revenue</div>
                <div class="metric-value">€{latest.get('mrr', 0):.2f}</div>
                <div class="metric-trend">{trend_mrr}</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Customer Acquisition Cost</div>
                <div class="metric-value">€{latest.get('cac', 0):.2f}</div>
                <div class="metric-trend">{trend_cac}</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">D30 Retention Rate</div>
                <div class="metric-value">{latest.get('d30_retention', 0):.1f}%</div>
                <div class="metric-trend">{trend_d30}</div>
            </div>
        </div>
        
        <div class="chart-container">
            <div class="chart-title">MRR Trend (Last 7 Days)</div>
            <div class="simple-chart">
                {generate_bars(dates, mrr_values, '€')}
            </div>
        </div>
        
        <div class="chart-container">
            <div class="chart-title">CAC Trend (Last 7 Days)</div>
            <div class="simple-chart">
                {generate_bars(dates, cac_values, '€')}
            </div>
        </div>
        
        <div class="timestamp">
            Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
        
        <footer>
            <p>Generated by build_dashboard.py | Viss Command Center</p>
        </footer>
    </div>
</body>
</html>"""
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(html)


def generate_bars(dates: List[str], values: List[float], prefix: str = '') -> str:
    """Generate HTML for chart bars."""
    if not values:
        return '<p style="color: #999;">No data available</p>'
    
    max_val = max(values) if values else 1
    bars_html = []
    
    for date, value in zip(dates, values):
        height_pct = (value / max_val * 100) if max_val > 0 else 0
        date_short = date[-5:] if len(date) >= 5 else date  # MM-DD
        bars_html.append(f"""
                <div class="bar" style="height: {height_pct}%;">
                    <span class="bar-value">{prefix}{value:.0f}</span>
                    <span class="bar-label">{date_short}</span>
                </div>""")
    
    return ''.join(bars_html)


def main():
    parser = argparse.ArgumentParser(description='Build KPI dashboard HTML')
    parser.add_argument('--data-dir', type=str, default='data',
                        help='Data directory path (default: data)')
    parser.add_argument('--days', type=int, default=7,
                        help='Number of days to include in charts (default: 7)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')
    
    args = parser.parse_args()
    
    # Setup paths
    data_dir = Path(args.data_dir)
    metrics_dir = data_dir / 'metrics'
    output_path = data_dir / 'dashboard' / 'index.html'
    
    # Load metrics
    if args.verbose:
        print(f"Loading metrics from {metrics_dir}...")
    
    if not metrics_dir.exists():
        print(f"Error: Metrics directory not found: {metrics_dir}")
        sys.exit(1)
    
    metrics_list = load_recent_metrics(metrics_dir, args.days)
    
    if not metrics_list:
        print("Warning: No metrics files found. Creating dashboard with placeholder data.")
    
    if args.verbose:
        print(f"Loaded {len(metrics_list)} metrics files")
    
    # Generate dashboard
    if args.verbose:
        print("Generating dashboard HTML...")
    
    generate_dashboard_html(metrics_list, output_path)
    
    print(f"✓ Dashboard written to {output_path}")
    print(f"  Open in browser: file://{output_path.absolute()}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

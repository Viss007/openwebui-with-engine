#!/usr/bin/env python3
"""
Quick setup script for the KPI workspace.

Generates sample data and initial metrics/dashboard.
"""

import sys
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import csv


def create_sample_data(data_dir: Path, days: int = 7):
    """Create sample CSV data files."""
    print(f"Generating {days} days of sample data...")
    
    base_date = datetime.now() - timedelta(days=days-1)
    
    # billing.csv - growing MRR
    billing_file = data_dir / 'billing.csv'
    with open(billing_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['date', 'amount', 'status'])
        for i in range(days):
            date = (base_date + timedelta(days=i)).strftime('%Y-%m-%d')
            amount = 800 + (i * 150)
            writer.writerow([date, f'{amount:.2f}', 'active'])
    
    print(f"  ✓ Created {billing_file}")
    
    # ads_spend.csv - varying spend
    ads_file = data_dir / 'ads_spend.csv'
    with open(ads_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['date', 'spend'])
        spends = [100, 120, 110, 130, 115, 125, 105]
        for i in range(days):
            date = (base_date + timedelta(days=i)).strftime('%Y-%m-%d')
            spend = spends[i % len(spends)]
            writer.writerow([date, f'{spend:.2f}'])
    
    print(f"  ✓ Created {ads_file}")
    
    # new_customers.csv - varying customer acquisition
    customers_file = data_dir / 'new_customers.csv'
    with open(customers_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['date', 'new_customers'])
        customers = [3, 4, 2, 5, 3, 4, 3]
        for i in range(days):
            date = (base_date + timedelta(days=i)).strftime('%Y-%m-%d')
            count = customers[i % len(customers)]
            writer.writerow([date, count])
    
    print(f"  ✓ Created {customers_file}")


def generate_metrics(data_dir: Path, days: int = 7):
    """Generate metrics for each day."""
    print(f"\nGenerating metrics for {days} days...")
    
    base_date = datetime.now() - timedelta(days=days-1)
    
    for i in range(days):
        date = (base_date + timedelta(days=i)).strftime('%Y-%m-%d')
        result = subprocess.run(
            [sys.executable, str(data_dir / 'tools' / 'compute_kpis.py'),
             '--write', '--date', date, '--data-dir', str(data_dir)],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"  ✓ Generated metrics for {date}")
        else:
            print(f"  ✗ Failed for {date}: {result.stderr}")
            return False
    
    return True


def build_dashboard(data_dir: Path):
    """Build the HTML dashboard."""
    print("\nBuilding dashboard...")
    
    result = subprocess.run(
        [sys.executable, str(data_dir / 'tools' / 'build_dashboard.py'),
         '--data-dir', str(data_dir)],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        dashboard_path = data_dir / 'dashboard' / 'index.html'
        print(f"  ✓ Dashboard created: {dashboard_path}")
        print(f"\n  Open in browser: file://{dashboard_path.absolute()}")
        return True
    else:
        print(f"  ✗ Failed: {result.stderr}")
        return False


def main():
    """Run the setup."""
    print("="*60)
    print("KPI Workspace Quick Setup")
    print("="*60)
    
    # Get data directory
    repo_root = Path(__file__).parent
    data_dir = repo_root / 'data'
    
    if not data_dir.exists():
        print(f"Error: Data directory not found: {data_dir}")
        return 1
    
    # Create sample data
    create_sample_data(data_dir, days=7)
    
    # Generate metrics
    if not generate_metrics(data_dir, days=7):
        return 1
    
    # Build dashboard
    if not build_dashboard(data_dir):
        return 1
    
    print("\n" + "="*60)
    print("✅ Setup complete!")
    print("="*60)
    print("\nNext steps:")
    print("  1. Open data/dashboard/index.html in your browser")
    print("  2. Update data/billing.csv, data/ads_spend.csv, data/new_customers.csv")
    print("  3. Run: python data/tools/compute_kpis.py --write")
    print("  4. Run: python data/tools/build_dashboard.py")
    print("\nOr use the task API:")
    print("  curl -X POST http://localhost:8080/engine/tasks/submit \\")
    print("    -H 'Content-Type: application/json' \\")
    print("    -d '{\"name\":\"compute_kpis\",\"args\":{\"write\":true}}'")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

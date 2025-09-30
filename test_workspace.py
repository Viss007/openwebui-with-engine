#!/usr/bin/env python3
"""
Integration test for workspace KPI tools.

Tests the complete workflow:
1. Compute KPIs from CSV data
2. Build HTML dashboard
3. Dispatch alerts (dry run)
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(cmd, description):
    """Run a command and check for success."""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode != 0:
        print(f"❌ FAILED with exit code {result.returncode}")
        return False
    
    print(f"✅ SUCCESS")
    return True


def check_file_exists(filepath, description):
    """Check if a file exists."""
    print(f"\nChecking: {description}")
    if not filepath.exists():
        print(f"❌ File not found: {filepath}")
        return False
    
    size = filepath.stat().st_size
    print(f"✅ Found: {filepath} ({size} bytes)")
    return True


def main():
    """Run integration tests."""
    print("\n" + "="*60)
    print("Workspace KPI Tools - Integration Test")
    print("="*60)
    
    # Setup paths
    repo_root = Path(__file__).parent
    data_dir = repo_root / 'data'
    
    # Change to repo directory
    os.chdir(repo_root)
    
    success = True
    
    # Test 1: Compute KPIs
    if not run_command(
        [sys.executable, 'data/tools/compute_kpis.py', '--write', '--verbose'],
        "Compute KPIs"
    ):
        success = False
    
    # Test 2: Check metrics file was created
    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')
    metrics_file = data_dir / 'metrics' / f'{today}.md'
    if not check_file_exists(metrics_file, f"Metrics file for {today}"):
        success = False
    
    # Test 3: Build dashboard
    if not run_command(
        [sys.executable, 'data/tools/build_dashboard.py', '--verbose'],
        "Build Dashboard"
    ):
        success = False
    
    # Test 4: Check dashboard file was created
    dashboard_file = data_dir / 'dashboard' / 'index.html'
    if not check_file_exists(dashboard_file, "Dashboard HTML"):
        success = False
    
    # Test 5: Dispatch alerts (dry run)
    if not run_command(
        [sys.executable, 'data/tools/alert_dispatch.py', '--flush', '--dry-run', '--verbose'],
        "Dispatch Alerts (Dry Run)"
    ):
        success = False
    
    # Test 6: Check task registration
    print(f"\n{'='*60}")
    print("Testing: Task Registration")
    print('='*60)
    try:
        from engine import task_runner
        tasks = sorted(task_runner._TASKS.keys())
        print(f"Registered tasks: {tasks}")
        
        required_tasks = ['compute_kpis', 'build_dashboard', 'dispatch_alerts']
        for task in required_tasks:
            if task not in tasks:
                print(f"❌ Missing task: {task}")
                success = False
            else:
                print(f"✅ Found task: {task}")
    except Exception as e:
        print(f"❌ Error checking tasks: {e}")
        success = False
    
    # Summary
    print(f"\n{'='*60}")
    if success:
        print("✅ ALL TESTS PASSED")
        print('='*60)
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print('='*60)
        return 1


if __name__ == '__main__':
    sys.exit(main())

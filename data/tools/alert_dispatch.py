#!/usr/bin/env python3
"""
Alert dispatch system with quiet hours support.

Processes alerts from outbox.jsonl and dispatches them outside quiet hours.
"""

import argparse
import json
import sys
from datetime import datetime, time
from pathlib import Path
from typing import Dict, List
import pytz


def load_config(config_path: Path) -> Dict:
    """Load configuration from JSON file."""
    if not config_path.exists():
        return {
            'quiet_hours': {'start': '22:00', 'end': '07:00', 'tz': 'Europe/Vilnius'},
            'channels': {}
        }
    
    with open(config_path, 'r') as f:
        return json.load(f)


def is_quiet_hours(config: Dict) -> bool:
    """Check if current time is within quiet hours."""
    quiet = config.get('quiet_hours', {})
    tz_name = quiet.get('tz', 'Europe/Vilnius')
    start_str = quiet.get('start', '22:00')
    end_str = quiet.get('end', '07:00')
    
    try:
        tz = pytz.timezone(tz_name)
        now = datetime.now(tz)
        current_time = now.time()
        
        start_time = time.fromisoformat(start_str)
        end_time = time.fromisoformat(end_str)
        
        # Handle overnight quiet hours (e.g., 22:00 to 07:00)
        if start_time > end_time:
            return current_time >= start_time or current_time < end_time
        else:
            return start_time <= current_time < end_time
    except Exception as e:
        print(f"Error checking quiet hours: {e}")
        return False


def load_alerts(alerts_path: Path) -> List[Dict]:
    """Load alerts from JSONL file."""
    if not alerts_path.exists():
        return []
    
    alerts = []
    with open(alerts_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    alerts.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Warning: Invalid JSON in alerts: {e}")
    
    return alerts


def dispatch_alert(alert: Dict, config: Dict, dry_run: bool = False) -> bool:
    """
    Dispatch a single alert.
    
    For now, this is a placeholder that prints the alert.
    In production, this would send to webhook, email, etc.
    """
    channels = config.get('channels', {})
    webhook_url = channels.get('webhook_url')
    email = channels.get('email')
    
    print(f"\n📢 Alert: {alert.get('metric', 'Unknown')}")
    print(f"   Message: {alert.get('message', 'No message')}")
    print(f"   Value: {alert.get('value', 'N/A')}")
    print(f"   Change: {alert.get('change_pct', 0):.1f}%")
    
    if dry_run:
        print("   [DRY RUN - Not actually dispatched]")
        return True
    
    # Placeholder for actual dispatch logic
    if webhook_url:
        print(f"   Would send to webhook: {webhook_url}")
    
    if email:
        print(f"   Would send to email: {email}")
    
    if not webhook_url and not email:
        print("   No dispatch channels configured")
    
    return True


def clear_alerts_file(alerts_path: Path) -> None:
    """Clear the alerts outbox file."""
    if alerts_path.exists():
        alerts_path.unlink()


def main():
    parser = argparse.ArgumentParser(description='Dispatch alerts from queue')
    parser.add_argument('--data-dir', type=str, default='data',
                        help='Data directory path (default: data)')
    parser.add_argument('--flush', action='store_true',
                        help='Flush all alerts regardless of quiet hours')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be dispatched without actually dispatching')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')
    
    args = parser.parse_args()
    
    # Setup paths
    data_dir = Path(args.data_dir)
    config_path = data_dir / 'config' / 'alerts.json'
    alerts_path = data_dir / 'alerts' / 'outbox.jsonl'
    
    # Load config
    config = load_config(config_path)
    
    # Check quiet hours
    if not args.flush:
        if is_quiet_hours(config):
            print("⏰ Currently in quiet hours. Alerts will remain queued.")
            print("   Use --flush to dispatch anyway.")
            return 0
    
    # Load alerts
    if args.verbose:
        print(f"Loading alerts from {alerts_path}...")
    
    alerts = load_alerts(alerts_path)
    
    if not alerts:
        print("✓ No alerts in queue.")
        return 0
    
    print(f"Found {len(alerts)} alert(s) to dispatch.")
    
    # Dispatch alerts
    dispatched = 0
    for alert in alerts:
        if dispatch_alert(alert, config, args.dry_run):
            dispatched += 1
    
    # Clear alerts file if not dry run
    if not args.dry_run and dispatched > 0:
        clear_alerts_file(alerts_path)
        print(f"\n✓ Dispatched {dispatched} alert(s) and cleared queue.")
    elif args.dry_run:
        print(f"\n[DRY RUN] Would have dispatched {dispatched} alert(s).")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

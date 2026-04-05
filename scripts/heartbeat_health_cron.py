#!/usr/bin/env python3
"""
Heartbeat Health Monitor - Cron Job
Runs independently of the heartbeat to verify state is being updated.
Alerts if heartbeat state becomes stale.

This should run as a cron job (recommended: every 1 hour).
If heartbeat state is stale, it will DM Nemesis with the alert.

Usage:
    python3 heartbeat_health_cron.py [--dry-run]
"""

import json
import subprocess
import sys
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.parent
STATE_FILE = SCRIPT_DIR / "memory" / "heartbeat-state.json"
NEMESIS_ID = "7924461837"

THRESHOLDS = {
    "heartbeat_run": {"warning": 45, "critical": 60},
    "group_message": {"warning": 240, "critical": 360},
    "nemesis_ping": {"warning": 360, "critical": 480},
    "git_push": {"warning": 180, "critical": 360},
    "memory_review": {"warning": 1560, "critical": 1800},
}


def load_state():
    if not STATE_FILE.exists():
        return {"lastChecks": {}}
    with open(STATE_FILE, "r") as f:
        return json.load(f)


def minutes_ago(timestamp_str):
    if not timestamp_str:
        return None
    try:
        last_time = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        return (now - last_time).total_seconds() / 60
    except:
        return None


def check_health():
    state = load_state()
    last_checks = state.get("lastChecks", {})

    critical = []
    warnings = []

    for field, thresholds in THRESHOLDS.items():
        value = last_checks.get(field)
        minutes = minutes_ago(value)

        if minutes is None:
            critical.append(f"{field}: Never run")
        elif minutes >= thresholds["critical"]:
            critical.append(
                f"{field}: CRITICAL - {round(minutes)} min since last run (threshold: {thresholds['critical']} min)"
            )
        elif minutes >= thresholds["warning"]:
            warnings.append(
                f"{field}: WARNING - {round(minutes)} min since last run (threshold: {thresholds['warning']} min)"
            )

    return critical, warnings


def send_alert(critical, warnings, dry_run=False):
    """Send alert to Nemesis via message tool."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    message = f"⚠️ **Heartbeat Health Alert** `{timestamp}`\n\n"

    if critical:
        message += "**CRITICAL:**\n"
        for item in critical:
            message += f"• {item}\n"
        message += "\n"

    if warnings:
        message += "**Warnings:**\n"
        for item in warnings:
            message += f"• {item}\n"

    message += "\n_Script: scripts/heartbeat_health_cron.py_"

    if dry_run:
        print("DRY RUN - Would send:")
        print(message)
        return

    cmd = [
        "openclaw",
        "gateway",
        "call",
        "message.send",
        "--params",
        f'{{"channel": "telegram", "target": "{NEMESIS_ID}", "text": {json.dumps(message)}}}',
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"Alert sent to {NEMESIS_ID}")
        else:
            print(f"Failed to send alert: {result.stderr}")
            sys.exit(1)
    except Exception as e:
        print(f"Error sending alert: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Heartbeat Health Monitor Cron")
    parser.add_argument(
        "--dry-run", action="store_true", help="Don't send alerts, just print"
    )
    args = parser.parse_args()

    critical, warnings = check_health()

    if critical or warnings:
        print(f"Issues found - Critical: {len(critical)}, Warnings: {len(warnings)}")
        for item in critical:
            print(f"  ✗ {item}")
        for item in warnings:
            print(f"  ⚠ {item}")

        if critical:
            send_alert(critical, warnings, dry_run=args.dry_run)
            sys.exit(2)
    else:
        print("Heartbeat state healthy")
        sys.exit(0)


if __name__ == "__main__":
    main()

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
import re
import urllib.error
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

ACTIVE_HOURS = {"start": 7, "end": 23}


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


def is_active_hours():
    """Check if current IST time is within active hours (7 AM - 11 PM)."""
    now_utc = datetime.now(timezone.utc)
    ist_offset = timedelta(hours=5, minutes=30)
    now_ist = now_utc.astimezone(timezone(timedelta(hours=5, minutes=30)))
    hour = now_ist.hour
    return ACTIVE_HOURS["start"] <= hour < ACTIVE_HOURS["end"]


def check_health():
    state = load_state()
    last_checks = state.get("lastChecks", {})

    critical = []
    warnings = []
    active = is_active_hours()

    for field, thresholds in THRESHOLDS.items():
        value = last_checks.get(field)
        minutes = minutes_ago(value)

        if minutes is None:
            if field == "heartbeat_run" and not active:
                continue
            critical.append(f"{field}: Never run")
        elif minutes >= thresholds["critical"]:
            if field == "heartbeat_run" and not active:
                continue
            critical.append(
                f"{field}: CRITICAL - {round(minutes)} min since last run (threshold: {thresholds['critical']} min)"
            )
        elif minutes >= thresholds["warning"]:
            warnings.append(
                f"{field}: WARNING - {round(minutes)} min since last run (threshold: {thresholds['warning']} min)"
            )

    return critical, warnings


def keepalive_state():
    """Update heartbeat_run state during inactive hours to prevent stale alerts."""
    state = load_state()
    now = datetime.now(timezone.utc).isoformat()
    state.setdefault("lastChecks", {})
    state["lastChecks"]["heartbeat_run"] = now

    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

    print("Heartbeat keepalive: state updated (inactive hours)")


def get_bot_token():
    """Get Telegram bot token from openclaw config."""
    try:
        result = subprocess.run(
            ["openclaw", "config", "get", "channels.telegram.botToken"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            token = result.stdout.strip()
            # Remove any potential quoting or extra characters
            token = token.strip('"\'')
            if token and token != "__OPENCLAW_REDACTED__" and token != "undefined" and token != "null":
                return token
    except Exception as e:
        print(f"DEBUG: Error getting bot token: {e}")
    return None


def send_telegram_message(bot_token, chat_id, text):
    """Send message directly via Telegram Bot API using curl."""
    import urllib.request
    import urllib.parse

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = json.dumps(
        {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "disable_notification": False,
        }
    ).encode("utf-8")

    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")
        print(f"URL: {url}")
        print(f"Data: {data}")
        raise
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}")
        raise


def format_alert_message(critical, warnings):
    """Build the alert message text."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"⚠️ **Heartbeat Health Alert** `{timestamp}`",
        "",
    ]

    if critical:
        lines.append("**CRITICAL:**")
        for item in critical:
            lines.append(f"• {item}")
        lines.append("")

    if warnings:
        lines.append("**Warnings:**")
        for item in warnings:
            lines.append(f"• {item}")
        lines.append("")

    lines.append("_Script: scripts/heartbeat_health_cron.py_")
    return "\n".join(lines)


def send_alert(critical, warnings, dry_run=False):
    """Send alert to Nemesis via Telegram Bot API."""
    message = format_alert_message(critical, warnings)

    if dry_run:
        print("DRY RUN - Would send:")
        print(message)
        return

    bot_token = get_bot_token()
    if not bot_token:
        print("ERROR: Could not get Telegram bot token from config")
        print("Falling back to openclaw system event...")
        fallback_alert(critical, warnings)
        return

    try:
        result = send_telegram_message(bot_token, NEMESIS_ID, message)
        if result.get("ok"):
            print(f"Alert sent to {NEMESIS_ID}")
        else:
            print(f"Telegram API error: {result.get('description', 'unknown')}")
            sys.exit(1)
    except Exception as e:
        print(f"Error sending Telegram message: {e}")
        fallback_alert(critical, warnings)


def fallback_alert(critical, warnings):
    """Fallback: use openclaw system event to alert (will go to default channels)."""
    message = format_alert_message(critical, warnings)
    message = message.replace("*", "").replace("_", "").replace("`", "")
    try:
        result = subprocess.run(
            [
                "openclaw",
                "system",
                "event",
                "--mode",
                "now",
                "--text",
                message,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            print("Alert sent via system event")
        else:
            print(f"System event fallback also failed: {result.stderr}")
            sys.exit(1)
    except Exception as e:
        print(f"Fallback failed: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Heartbeat Health Monitor Cron")
    parser.add_argument(
        "--dry-run", action="store_true", help="Don't send alerts, just print"
    )
    args = parser.parse_args()

    active = is_active_hours()

    if not active:
        keepalive_state()
        print("Outside active hours (11 PM - 7 AM IST), state kept alive. Exiting.")
        sys.exit(0)

    critical, warnings = check_health()

    if critical or warnings:
        print(f"Issues found - Critical: {len(critical)}, Warnings: {len(warnings)}")
        for item in critical:
            print(f"  ✗ {item}")
        for item in warnings:
            print(f"  ⚠ {item}")

        if critical:
            if args.dry_run:
                send_alert(critical, warnings, dry_run=True)
            # Return the alert message for the cron job to handle
            alert_message = format_alert_message(critical, warnings)
            print(f"ALERT_MESSAGE::{alert_message}")
            sys.exit(2)
    else:
        print("Heartbeat state healthy")
        sys.exit(0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Health check for heartbeat state - reports staleness
"""

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

THRESHOLDS = {
    "heartbeat_run": {"warning": 45, "critical": 60},
    "group_message": {"warning": 240, "critical": 360},
    "nemesis_ping": {"warning": 360, "critical": 480},
    "git_push": {"warning": 180, "critical": 360},
    "memory_review": {"warning": 1560, "critical": 1800},
}


def get_state():
    state_file = Path(__file__).parent.parent.parent / "memory" / "heartbeat-state.json"

    if not state_file.exists():
        return {"lastChecks": {}}

    with open(state_file, "r") as f:
        return json.load(f)


def minutes_ago(timestamp_str):
    if not timestamp_str:
        return None

    try:
        last_time = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        # Ensure last_time is timezone aware
        if last_time.tzinfo is None:
            last_time = last_time.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        return (now - last_time).total_seconds() / 60
    except:
        return None


def check_health():
    state = get_state()
    last_checks = state.get("lastChecks", {})

    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "overall": "healthy",
        "checks": [],
    }

    for field, thresholds in THRESHOLDS.items():
        value = last_checks.get(field)
        minutes = minutes_ago(value)

        check_result = {
            "field": field,
            "last_run": value,
            "minutes_ago": round(minutes) if minutes is not None else None,
            "status": "unknown",
        }

        if minutes is None:
            check_result["status"] = "never_run"
            check_result["message"] = "Never executed"
        elif minutes >= thresholds["critical"]:
            check_result["status"] = "critical"
            check_result["message"] = (
                f"CRITICAL: {round(minutes)} min since last run (threshold: {thresholds['critical']} min)"
            )
        elif minutes >= thresholds["warning"]:
            check_result["status"] = "warning"
            check_result["message"] = (
                f"WARNING: {round(minutes)} min since last run (threshold: {thresholds['warning']} min)"
            )
        else:
            check_result["status"] = "healthy"
            check_result["message"] = f"OK: {round(minutes)} min ago"

        results["checks"].append(check_result)

        if check_result["status"] in ["critical", "never_run"]:
            results["overall"] = "critical"
        elif check_result["status"] == "warning" and results["overall"] == "healthy":
            results["overall"] = "warning"

    return results


def main():
    results = check_health()

    print("=" * 60)
    print("HEARTBEAT STATE HEALTH CHECK")
    print("=" * 60)
    print(f"\nOverall: {results['overall'].upper()}\n")

    for check in results["checks"]:
        icon = {"healthy": "✓", "warning": "⚠", "critical": "✗", "unknown": "?"}[
            check["status"]
        ]
        print(f"{icon} {check['field']}: {check['message']}")

    print("\n" + "=" * 60)

    exit_code = {"healthy": 0, "warning": 1, "critical": 2}[results["overall"]]
    exit(exit_code)


if __name__ == "__main__":
    main()

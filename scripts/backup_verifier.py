#!/usr/bin/env python3
"""
Backup Verifier - Ensures memory files are properly backed up to GitHub

Checks:
1. Git status for uncommitted memory changes
2. Verifies push succeeded (not just commit)
3. Reports if memory files are >24h uncommitted

Exit codes:
  0 = All OK
  1 = Warning (memory changes pending but <24h)
  2 = Critical (memory files uncommitted >24h or push failed)
"""

import json
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

MEMORY_FILES = [
    "MEMORY.md",
    "GROUP.md",
    "AGENTS.md",
    "SOUL.md",
    "USER.md",
    "HEARTBEAT.md",
    "CRON-CONTEXT.md",
    "IDENTITY.md",
    "TOOLS.md",
]

MEMORY_DIR = Path(__file__).parent.parent / "memory"
WORKSPACE_DIR = Path(__file__).parent.parent


def get_file_modified_time(filepath):
    """Get last modification time of a file."""
    try:
        mtime = filepath.stat().st_mtime
        return datetime.fromtimestamp(mtime, tz=timezone.utc)
    except:
        return None


def check_uncommitted_changes():
    """Check for uncommitted changes in memory files."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=WORKSPACE_DIR,
            capture_output=True,
            text=True,
        )

        uncommitted = []
        for line in result.stdout.strip().split("\n"):
            if line:
                filepath = line[3:].strip().strip('"')
                for mf in MEMORY_FILES:
                    if mf in filepath or "memory/" in filepath:
                        uncommitted.append(filepath)
                        break

        return list(set(uncommitted))
    except Exception as e:
        return None


def get_last_commit_time():
    """Get the time of the last commit for memory files."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--"] + MEMORY_FILES,
            cwd=WORKSPACE_DIR,
            capture_output=True,
            text=True,
        )
        if result.stdout.strip():
            timestamp = int(result.stdout.strip())
            return datetime.fromtimestamp(timestamp, tz=timezone.utc)
    except:
        pass
    return None


def check_remote_tracking():
    """Check if local branch is up-to-date with remote."""
    try:
        result = subprocess.run(
            ["git", "status", "-sb"], cwd=WORKSPACE_DIR, capture_output=True, text=True
        )

        status_line = result.stdout.strip().split("\n")[0] if result.stdout else ""

        if "ahead" in status_line and "behind" in status_line:
            return "diverged"
        elif "ahead" in status_line:
            return "ahead"
        elif "behind" in status_line:
            return "behind"
        else:
            return "up_to_date"
    except:
        return "unknown"


def verify_backup():
    """Main verification function."""
    now = datetime.now(timezone.utc)
    results = {
        "timestamp": now.isoformat(),
        "status": "healthy",
        "issues": [],
        "warnings": [],
        "details": {},
    }

    uncommitted = check_uncommitted_changes()
    last_commit = get_last_commit_time()
    remote_status = check_remote_tracking()

    results["details"]["uncommitted_memory_files"] = uncommitted or []
    results["details"]["remote_status"] = remote_status

    if uncommitted:
        results["warnings"].append(
            f"{len(uncommitted)} memory-related file(s) uncommitted"
        )

        if last_commit:
            hours_since_commit = (now - last_commit).total_seconds() / 3600
            results["details"]["hours_since_last_memory_commit"] = round(
                hours_since_commit, 1
            )

            if hours_since_commit > 24:
                results["status"] = "critical"
                results["issues"].append(
                    f"CRITICAL: Memory files uncommitted for {round(hours_since_commit, 1)} hours (>24h threshold)"
                )
            else:
                results["status"] = "warning"
                results["warnings"].append(
                    f"Memory files pending commit for {round(hours_since_commit, 1)} hours"
                )

    if remote_status == "ahead":
        results["status"] = "critical"
        results["issues"].append("CRITICAL: Local commits not pushed to remote")
    elif remote_status == "diverged":
        results["status"] = "critical"
        results["issues"].append("CRITICAL: Local and remote have diverged")
    elif remote_status == "unknown":
        results["status"] = "warning"
        results["warnings"].append("Could not verify remote status")

    results["details"]["last_memory_commit"] = (
        last_commit.isoformat() if last_commit else None
    )

    return results


def main():
    results = verify_backup()

    print("=" * 60)
    print("MEMORY BACKUP VERIFICATION")
    print("=" * 60)
    print(f"\nStatus: {results['status'].upper()}\n")

    if results["issues"]:
        print("ISSUES:")
        for issue in results["issues"]:
            print(f"  ✗ {issue}")
        print()

    if results["warnings"]:
        print("WARNINGS:")
        for warning in results["warnings"]:
            print(f"  ⚠ {warning}")
        print()

    if results["status"] == "healthy":
        print("✓ Memory backup verified")
        if results["details"]["last_memory_commit"]:
            print(f"  Last commit: {results['details']['last_memory_commit']}")
        print(f"  Remote status: {results['details']['remote_status']}")

    print("\n" + "=" * 60)

    exit_code = {"healthy": 0, "warning": 1, "critical": 2}[results["status"]]
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

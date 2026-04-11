#!/usr/bin/env python3
"""
Memory Archive - Archives daily memory files older than 180 days
Location: memory/archived/YYYY-MM/
Never deletes - only archives
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent
MEMORY_DIR = WORKSPACE / "memory"
ARCHIVE_DIR = MEMORY_DIR / "archived"
RETENTION_DAYS = 180

PROTECTED_FILES = {
    "wotd-history.json",
    "tips-history.json",
    "jokes-history.json",
    "stories-history.json",
    "heartbeat-state.json",
    "scheduler_state.json",
    ".sync_state.json",
    "target_channels.json",
}


def main():
    ARCHIVE_DIR.mkdir(exist_ok=True)
    cutoff = datetime.now() - timedelta(days=RETENTION_DAYS)

    archived_count = 0

    for f in MEMORY_DIR.glob("*.md"):
        if f.name in PROTECTED_FILES:
            continue

        try:
            file_date = datetime.strptime(f.stem, "%Y-%m-%d")
            if file_date < cutoff:
                month_dir = ARCHIVE_DIR / file_date.strftime("%Y-%m")
                month_dir.mkdir(exist_ok=True)
                dest = month_dir / f.name

                if dest.exists():
                    dest.unlink()

                f.rename(dest)
                archived_count += 1
        except ValueError:
            continue

    print(f"Archived {archived_count} old memory files")


if __name__ == "__main__":
    main()

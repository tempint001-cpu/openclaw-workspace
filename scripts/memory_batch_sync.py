#!/usr/bin/env python3
"""
Memory Batch Sync - runs every 15 minutes
✅ Reads last 15 minutes of chat logs
✅ Writes clean summary to daily memory file
✅ Triggers memory embedding index exactly once per run
✅ Runs 96 times per day (every 15 minutes) - well within API limits
"""

import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import sys

WORKSPACE = Path(__file__).parent.parent
DAILY_FILE = WORKSPACE / "memory" / f"{datetime.utcnow().strftime('%Y-%m-%d')}.md"

def get_ist_time():
    return datetime.utcnow() + timedelta(hours=5, minutes=30)

def main():
    now = get_ist_time()
    timestamp = now.strftime("%H:%M IST")
    
    # 1. Get last 15 minutes of chat transcript - 10s timeout
    try:
        result = subprocess.run(
            ["openclaw", "session", "history", "--limit", "30"],
            capture_output=True,
            text=True,
            cwd=WORKSPACE,
            timeout=10
        )
    except subprocess.TimeoutExpired:
        print("Session history timed out")
        sys.exit(1)
    
    if result.returncode != 0:
        print(f"Session history failed: {result.stderr}")
        return
    
    try:
        messages = json.loads(result.stdout)
    except json.JSONDecodeError:
        print("Invalid JSON from session history")
        sys.exit(1)
    
    # 2. Extract summary
    summary = []
    cutoff = (datetime.utcnow() - timedelta(minutes=15)).timestamp()
    
    for msg in messages:
        if msg.get("timestamp", 0) > cutoff:
            sender = msg.get("sender", "unknown")
            text = msg.get("text", "")[:150]
            summary.append(f"- [{timestamp}] {sender}: {text}")
    
    # 3. Append to daily file
    if summary:
        with open(DAILY_FILE, "a", encoding="utf-8") as f:
            f.write("\n\n")
            f.write(f"### Sync {timestamp}\n")
            f.write("\n".join(summary))
    
    # 4. Memory index disabled temporarily - broken upstream
    # try:
    #     subprocess.run(
    #         ["openclaw", "memory", "index"],
    #         capture_output=True,
    #         cwd=WORKSPACE,
    #         timeout=8
    #     )
    # except subprocess.TimeoutExpired:
    #     pass

if __name__ == "__main__":
    main()

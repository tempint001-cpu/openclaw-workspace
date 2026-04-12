#!/usr/bin/env python3
from datetime import datetime, timezone, timedelta
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
HEARTBEAT_FILE = WORKSPACE / "HEARTBEAT.md"

def get_ist_time():
    now = datetime.now(timezone.utc)
    ist = now + timedelta(hours=5, minutes=30)
    return ist.strftime("%Y-%m-%d %I:%M %p IST")

def update_time():
    if not HEARTBEAT_FILE.exists():
        return
    with open(HEARTBEAT_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    time_str = f"> CURRENT IST TIME: {get_ist_time()}\n"
    
    if lines and lines[0].startswith("> CURRENT IST TIME:"):
        lines[0] = time_str
    else:
        lines.insert(0, time_str)
        
    with open(HEARTBEAT_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)

if __name__ == "__main__":
    update_time()

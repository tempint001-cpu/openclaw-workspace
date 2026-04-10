#!/usr/bin/env python3
from datetime import datetime, timedelta
import subprocess
import json
import os

SCHEDULE = [
    ("07:00", "good-morning-dm"),
    ("07:30", "ai-news-digest"),
    ("08:00", "good-morning-group"),
    ("09:00", "daily-war-update"),
    ("10:00", "word-of-the-day"),
    ("15:00", "feminine-tip-daily"),
    ("16:00", "afternoon-jokes"),
    ("22:00", "goodnight-story"),
    ("03:00", "nightly-memory-review")
]

STATE_FILE = "/root/.openclaw/workspace/memory/scheduler_state.json"

def get_ist_time():
    return datetime.utcnow() + timedelta(hours=5, minutes=30)

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"last_run": {}}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def run_job(job_name):
    print(f"[{get_ist_time().strftime('%H:%M IST')}] Running job: {job_name}")

if __name__ == "__main__":
    state = load_state()
    now = get_ist_time()
    current_time = now.strftime("%H:%M")

    for time_str, job_name in SCHEDULE:
        if time_str == current_time and state['last_run'].get(job_name) != current_time:
            run_job(job_name)
            state['last_run'][job_name] = current_time
            save_state(state)

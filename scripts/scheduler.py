#!/usr/bin/env python3
from datetime import datetime, timedelta
import subprocess
import json
import os

SCHEDULE = [
    ("06:00", "daily-session-reset"),
    ("07:00", "good-morning-dm"),
    ("07:30", "ai-news-digest"),
    ("08:00", "good-morning-group"),
    ("09:00", "daily-war-update"),
    ("10:00", "word-of-the-day"),
    ("15:00", "feminine-tip-daily"),
    ("16:00", "afternoon-jokes"),
    ("22:00", "goodnight-story"),
    ("03:00", "nightly-memory-review"),
    ("*/15", "memory-batch-sync"),
    ("0 *", "git-auto-commit")
]

STATE_FILE = "/root/.openclaw/workspace/memory/scheduler_state.json"

def get_ist_time():
    # Exact same logic as clock.py
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
    log = f"[{get_ist_time().strftime('%H:%M IST')}] Running job: {job_name}"
    print(log)
    
    if job_name == "git-auto-commit":
        result = subprocess.run(['/root/.openclaw/workspace/scripts/git_backup.sh'], capture_output=True, text=True)
        if result.returncode != 0:
            # Only send failures to monitoring group
            error_msg = f"❌ Git backup FAILED\n{result.stdout}\n{result.stderr}"
            subprocess.run([
                'openclaw', 'message', 'send',
                '--channel', 'telegram',
                '--target', '-5120995986',
                '--message', error_msg
            ], capture_output=True)
        return
        
    if job_name == "word-of-the-day":
        result = subprocess.run(['python3', '/root/.openclaw/workspace/scripts/wotd.py'], capture_output=True, text=True)
        if result.returncode == 0:
            subprocess.run([
                'openclaw', 'message', 'send',
                '--channel', 'telegram',
                '--target', '-1003606834639',
                '--message', result.stdout
            ], capture_output=True)
        return
        
    if job_name == "daily-session-reset":
        subprocess.run(['/root/.openclaw/workspace/scripts/new_session_daily.sh'], capture_output=True)
        return
    
    # Send all other scheduler logs to main group
    subprocess.run([
        'openclaw', 'message', 'send',
        '--channel', 'telegram',
        '--target', '-1003606834639',
        '--message', log
    ], capture_output=True)

if __name__ == "__main__":
    state = load_state()
    now = get_ist_time()
    current_time = now.strftime("%H:%M")

    for time_str, job_name in SCHEDULE:
        if time_str == current_time and state['last_run'].get(job_name) != current_time:
            run_job(job_name)
            state['last_run'][job_name] = current_time
            save_state(state)

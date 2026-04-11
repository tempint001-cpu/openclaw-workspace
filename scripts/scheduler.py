#!/usr/bin/env python3
from datetime import datetime, timedelta
import subprocess
import json
import os
import sys
from pathlib import Path

SCHEDULE = [
    ("*", "clock-tick"),
    ("00", "hourly-memory-summary"),
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
    ("04:00", "memory-archive"),
    ("01", "git-auto-commit"),
]

WORKSPACE = Path(__file__).parent.parent
STATE_FILE = WORKSPACE / "memory" / "scheduler_state.json"
CHANNELS_FILE = WORKSPACE / "memory" / "target_channels.json"


def get_ist_time():
    return datetime.utcnow() + timedelta(hours=5, minutes=30)


def load_channels():
    default = {
        "monitor_group": "-1003951451198",
        "main_group": "-1003606834639",
        "nemesis_dm": "7924461837",
        "sravya_dm": "1880938940",
    }
    if os.path.exists(CHANNELS_FILE):
        try:
            with open(CHANNELS_FILE, "r") as f:
                return {**default, **json.load(f)}
        except:
            pass
    return default


CHANNELS = load_channels()


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"last_run": {}}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def run_isolated_job(job_name, message, target_key):
    target = CHANNELS.get(target_key, CHANNELS["main_group"])
    try:
        subprocess.run(
            [
                "openclaw",
                "cron",
                "add",
                "--name",
                f"{job_name}-dynamic",
                "--at",
                "30s",
                "--session",
                "isolated",
                "--message",
                message,
                "--announce",
                "--channel",
                "telegram",
                "--target",
                target,
            ],
            capture_output=True,
            timeout=30,
        )
    except Exception as e:
        print(f"Error triggering {job_name}: {e}")


def run_job(job_name):
    log = f"[{get_ist_time().strftime('%H:%M IST')}] Running job: {job_name}"
    print(log)

    try:
        if job_name == "git-auto-commit":
            result = subprocess.run(
                [str(WORKSPACE / "scripts" / "git_backup.sh")],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode != 0:
                error_msg = f"❌ Git backup FAILED\n{result.stdout}\n{result.stderr}"
                subprocess.run(
                    [
                        "openclaw",
                        "message",
                        "send",
                        "--channel",
                        "telegram",
                        "--target",
                        CHANNELS["monitor_group"],
                        "--message",
                        error_msg,
                    ],
                    capture_output=True,
                )
            return

        if job_name == "word-of-the-day":
            msg = """Read memory/wotd-history.json and check the 'used' array. Search for an interesting, obscure English word (not commonly known) that is NOT in the used list. Get its definition, pronunciation (IPA), and a meaningful quote.
            
After selecting, UPDATE memory/wotd-history.json by adding this word to the 'used' array. Format: 📚 Word of the Day: **Word** - Definition - Pronounced: /ipa/ - > "quote" """
            run_isolated_job("word-of-the-day", msg, "main_group")
            return

        if job_name == "daily-session-reset":
            subprocess.run(
                [str(WORKSPACE / "scripts" / "new_session_daily.sh")],
                capture_output=True,
                timeout=30,
            )
            return

        if job_name == "memory-batch-sync":
            subprocess.run(
                ["python3", str(WORKSPACE / "scripts" / "memory_batch_sync.py")],
                capture_output=True,
                timeout=30,
            )
            return

        if job_name == "memory-archive":
            subprocess.run(
                ["python3", str(WORKSPACE / "scripts" / "memory_archive.py")],
                capture_output=True,
                timeout=60,
            )
            return
            
        if job_name == "nightly-memory-review":
            msg = """
Run the nightly memory distillation process:

1. First read today's full daily memory file: memory/YYYY-MM-DD.md
2. Read the full MEMORY.md file
3. Review every single conversation from today, extract only:
   - Important decisions made
   - New rules, agreements, requirements
   - Bugs found, issues fixed
   - Lessons learned, mistakes
   - New facts about people, preferences, boundaries
   - Infrastructure changes
4. Remove all casual banter, chit chat, filler messages. Only keep hard facts.
5. Merge the extracted clean facts into MEMORY.md under the correct sections
6. Do not duplicate existing entries
7. Update MEMORY.md cleanly
8. Send a short summary to Nemesis DM with how many items were added

Do this properly. This is the most important job. Everything we talk about must survive here."""
            run_isolated_job("nightly-memory-review", msg, "nemesis_dm")
            return
            
        if job_name == "clock-tick":
            # Just update state, no work - keeps current time loaded in scheduler state
            return
            
        if job_name == "hourly-memory-summary":
            msg = """
Hourly memory summary job:

1. Get all chat messages from last 60 minutes: both this DM and the main group
2. Extract:
   ✅ Hard facts, decisions, requests, bugs, changes, agreements
   ✅ Mood, tone, emotional state, vibe, frustrations, satisfaction
   ✅ Unspoken context, things implied between lines
   ✅ Preferences, likes, dislikes that were shown not stated
   ✅ Trust signals, jokes that landed, things that annoyed
3. Do NOT discard banter and casual talk - this is where most of the context lives.
4. Summarize cleanly, separate Facts section and Context / Tone section
5. Append this summary cleanly to today's daily memory file
6. No notifications required. Run silently.
"""
            run_isolated_job("hourly-memory-summary", msg, "monitor_group")
            return

        if job_name == "feminine-tip-daily":
            msg = """Read memory/tips-history.json and check the 'used' array. Search for a fresh, practical self-care or wellness tip for women that is NOT in the used list.
            
Topics to rotate: Skincare, Mental health, Fitness, Nutrition, Work-life balance, Fashion.
After selecting, UPDATE memory/tips-history.json by adding this tip to the 'used' array."""
            run_isolated_job("feminine-tip-daily", msg, "sravya_dm")
            return

        if job_name == "afternoon-jokes":
            msg = """Read memory/jokes-history.json and check the 'used' array. Search for 2-3 fresh, clean, funny jokes that are NOT in the used list. Include one tech joke, one general joke, one pun.
            
After selecting, UPDATE memory/jokes-history.json by adding these jokes to the 'used' array."""
            run_isolated_job("afternoon-jokes", msg, "main_group")
            return

        if job_name == "goodnight-story":
            msg = """Read memory/stories-history.json and check the 'used' array. Search for a short bedtime story (under 300 words) that is NOT in the used list.
            
Topics to rotate: Indian mythology folktale, Motivational story, Nature story, Historical anecdote.
After selecting, UPDATE memory/stories-history.json by adding this story topic to the 'used' array."""
            run_isolated_job("goodnight-story", msg, "nemesis_dm")
            return

        if job_name == "good-morning-dm":
            msg = """It's morning in India (IST). Search for: 1) A daily motivational quote, 2) Any interesting news from last night, 3) A positive affirmation. Send a warm, personal good morning message to Nemesis. Keep it brief, heartfelt, end with an emoji."""
            run_isolated_job("good-morning-dm", msg, "nemesis_dm")
            return

        if job_name == "good-morning-group":
            msg = """Search for a trending topic or interesting fact from today. Post a good morning message to the group with: 1) Warm greeting, 2) One interesting thing happening today, 3) An engaging question for the group. Keep it natural."""
            run_isolated_job("good-morning-group", msg, "main_group")
            return

        if job_name == "ai-news-digest":
            msg = """Search for today's top AI and tech news. Create a concise digest with: 1) 3-5 key headlines, 2) One sentence summary each, 3) Most interesting story highlighted. Format as a clean list."""
            run_isolated_job("ai-news-digest", msg, "nemesis_dm")
            return

        if job_name == "daily-war-update":
            msg = """Today's date is {date}. Provide a comprehensive global war and conflict update for Nemesis with:
- Historical Context (~100 words): Overview of major ongoing global conflicts, focus on Iran-US situation, other significant conflicts worldwide, brief context on how situations evolved
- Last 24 Hours Developments: Key events, specific updates on Iran-US tensions, other conflict zone updates, diplomatic initiatives
- India-Specific Implications: How conflicts affect India's interests, predictions for future impact, India's potential role

Cross-verify information using multiple sources (web search). Be concise but comprehensive. If uncertain, state the uncertainty rather than guessing. Send result to Nemesis via Telegram."""
            run_isolated_job("daily-war-update", msg, "nemesis_dm")
            return

        # Default: log to main group
        subprocess.run(
            [
                "openclaw",
                "message",
                "send",
                "--channel",
                "telegram",
                "--target",
                CHANNELS["main_group"],
                "--message",
                log,
            ],
            capture_output=True,
        )

    except subprocess.TimeoutExpired:
        print(f"Job {job_name} timed out")
    except Exception as e:
        print(f"Error running {job_name}: {e}")


def should_run(time_str, now, last_run, job_name):
    current_time = now.strftime("%H:%M")
    minute = now.minute
    current_date = now.strftime("%Y-%m-%d")

    # Every minute tick
    if time_str == "*":
        last_run_val = last_run.get(job_name, "")
        expected_run_key = f"{current_date}-{now.strftime('%H:%M')}"
        if last_run_val != expected_run_key:
            return True

    # Exact time match (e.g., "10:00")
    if time_str == current_time:
        last_run_val = last_run.get(job_name, "")
        if not last_run_val.startswith(current_date):
            return True
        if last_run_val != f"{current_date}-{current_time}":
            return True

    # Minute list: "00,15,30,45"
    if "," in time_str:
        allowed_minutes = [int(m) for m in time_str.split(",")]
        if minute in allowed_minutes:
            last_run_val = last_run.get(job_name, "")
            expected_run_key = f"{current_date}-{now.strftime('%H:%M')}"
            if last_run_val != expected_run_key:
                return True

    # Single minute job
    if time_str.isdigit() and int(time_str) == minute:
        last_run_val = last_run.get(job_name, "")
        expected_run_key = f"{current_date}-{now.strftime('%H:%M')}"
        if last_run_val != expected_run_key:
            return True

    return False


if __name__ == "__main__":
    state = load_state()
    now = get_ist_time()
    current_date = now.strftime("%Y-%m-%d")

    # Manual job trigger via command line
    if len(sys.argv) == 2:
        job_name = sys.argv[1]
        run_job(job_name)

        # Send completion notification - ALWAYS send, manual or cron
        log_done = f"[{now.strftime('%H:%M IST')}] ✅ Completed job: {job_name}"
        try:
            subprocess.run(
                [
                    "openclaw",
                    "message",
                    "send",
                    "--channel",
                    "telegram",
                    "--target",
                    CHANNELS["monitor_group"],
                    "--message",
                    log_done,
                ],
                capture_output=True,
                timeout=15,
            )
        except:
            pass

        # Store full ISO timestamp with date
        state["last_run"][job_name] = f"{current_date}-{now.strftime('%H:%M')}"
        save_state(state)
        sys.exit(0)

    # Normal scheduled run
    for time_str, job_name in SCHEDULE:
        if should_run(time_str, now, state["last_run"], job_name):
            run_job(job_name)

            # Send completion notification - ALWAYS send, manual or cron
            log_done = f"[{now.strftime('%H:%M IST')}] ✅ Completed job: {job_name}"
            try:
                subprocess.run(
                    [
                        "openclaw",
                        "message",
                        "send",
                        "--channel",
                        "telegram",
                        "--target",
                        CHANNELS["monitor_group"],
                        "--message",
                        log_done,
                    ],
                    capture_output=True,
                    timeout=15,
                )
            except:
                pass

            # Store full ISO timestamp with date
            state["last_run"][job_name] = f"{current_date}-{now.strftime('%H:%M')}"
            save_state(state)

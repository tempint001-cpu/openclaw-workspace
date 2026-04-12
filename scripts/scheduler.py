#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import json
import os
import subprocess
import sys
import traceback
from typing import Any, Callable, Dict, Optional, Tuple

SCHEDULE = [
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

WORKSPACE = Path(__file__).resolve().parent.parent
STATE_FILE = WORKSPACE / "memory" / "scheduler_state.json"
CHANNELS_FILE = WORKSPACE / "memory" / "target_channels.json"
LOG_FILE = WORKSPACE / "logs" / "jobs.log"

LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
STATE_FILE.parent.mkdir(parents=True, exist_ok=True)


def get_ist_time() -> datetime:
    # Uses UTC + 5:30 to approximate IST without depending on external timezone data.
    return datetime.utcnow() + timedelta(hours=5, minutes=30)


def load_channels() -> Dict[str, str]:
    default = {
        "monitor_group": "-1003951451198",
        "main_group": "-1003606834639",
        "nemesis_dm": "7924461837",
        "sravya_dm": "1880938940",
    }
    if CHANNELS_FILE.exists():
        try:
            with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            if isinstance(loaded, dict):
                return {**default, **{str(k): str(v) for k, v in loaded.items()}}
        except Exception:
            pass
    return default


CHANNELS = load_channels()


def send_notification(message: str) -> Tuple[bool, str]:
    """Send a message to the existing monitor group.

    Returns:
     (ok, error_text)
    """
    try:
        result = subprocess.run(
            [
                "openclaw",
                "message",
                "send",
                "--channel",
                "telegram",
                "--to",
                CHANNELS["monitor_group"],
                "--message",
                message,
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return False, (result.stderr or result.stdout or "notification command failed").strip()
        return True, ""
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def log_and_notify(job_name: str, status: str, details: str = "") -> None:
    now = get_ist_time()
    timestamp = now.strftime("%H:%M IST")
    status_icon = "✅" if status == "SUCCESS" else "❌"

    log_line = f"[{timestamp}] {status_icon} {status}: {job_name}"
    if details:
        log_line += f" | {details}"

    # Persist first, then notify.
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")
        f.flush()
        try:
            os.fsync(f.fileno())
        except OSError:
            # Best-effort durability; continue to notification even if fsync is unavailable.
            pass

    ok, err = send_notification(log_line)
    if not ok:
        # Never silently lose this failure; append to the same log file.
        failure_line = f"[{timestamp}] ❌ NOTIFY_FAILED: {job_name} | {err}"
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(failure_line + "\n")


def load_state() -> Dict[str, Any]:
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            if isinstance(loaded, dict):
                loaded.setdefault("last_run", {})
                return loaded
        except Exception:
            pass
    return {"last_run": {}}


def save_state(state: Dict[str, Any]) -> None:
    tmp = STATE_FILE.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
        f.flush()
        try:
            os.fsync(f.fileno())
        except OSError:
            pass
    tmp.replace(STATE_FILE)


def run_command(command: list[str], timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run(command, capture_output=True, text=True, timeout=timeout)


def run_isolated_job(job_name: str, message: str, target_key: str) -> Tuple[bool, str]:
    """Trigger an OpenClaw isolated job.Success means the trigger request was accepted locally.
    Completion of the downstream job is not tracked here.
    """
    target = CHANNELS.get(target_key, CHANNELS["main_group"])
    try:
        result = run_command(
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
                "--to",
                target,
            ],
            timeout=30,
        )
        if result.returncode != 0:
            err = (result.stderr or result.stdout or "isolated job trigger failed").strip()
            return False, err
        return True, "trigger sent"
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def build_job_message(job_name: str) -> str:
    if job_name == "word-of-the-day":
        return (
            "Read memory/wotd-history.json and check the 'used' array. Search for an interesting, obscure English word "
            "(not commonly known) that is NOT in the used list. Get its definition, pronunciation (IPA), and a meaningful quote. "
            "After selecting, UPDATE memory/wotd-history.json by adding this word to the 'used' array. Format: "
            "📚 Word of the Day: **Word** - Definition - Pronounced: /ipa/ - > \"quote\""
        )

    if job_name == "nightly-memory-review":
        return (
            "Run the nightly memory distillation process:\n\n"
            "1. First read today's full daily memory file: memory/YYYY-MM-DD.md\n"
            "2. Read the full MEMORY.md file\n"
            "3. Review every single conversation from today, extract only:\n"
            " - Important decisions made\n"
            " - New rules, agreements, requirements\n"
            " - Bugs found, issues fixed\n"
            " - Lessons learned, mistakes\n"
            " - New facts about people, preferences, boundaries\n"
            " - Infrastructure changes\n"
            "4. Remove all casual banter, chit chat, filler messages. Only keep hard facts.\n"
            "5. Merge the extracted clean facts into MEMORY.md under the correct sections\n"
            "6. Do not duplicate existing entries\n"
            "7. Update MEMORY.md cleanly\n"
            "8. Send a short summary to Nemesis DM with how many items were added\n\n"
            "Do this properly. This is the most important job. Everything we talk about must survive here."
        )

    if job_name == "hourly-memory-summary":
        return (
            "Hourly memory summary job:\n\n"
            "1. Get all chat messages from last 60 minutes: both this DM and the main group\n"
            "2. Extract:\n"
            " ✅ Hard facts, decisions, requests, bugs, changes, agreements\n"
            " ✅ Mood, tone, emotional state, vibe, frustrations, satisfaction\n"
            " ✅ Unspoken context, things implied between lines\n"
            " ✅ Preferences, likes, dislikes that were shown not stated\n"
            " ✅ Trust signals, jokes that landed, things that annoyed\n"
            "3. Do NOT discard banter and casual talk - this is where most of the context lives.\n"
            "4. Summarize cleanly, separate Facts section and Context / Tone section\n"
            "5. Append this summary cleanly to today's daily memory file\n"
            "6. No notifications required. Run silently."
        )

    if job_name == "feminine-tip-daily":
        return (
            "Read memory/tips-history.json and check the 'used' array. Search for a fresh, practical self-care or wellness tip for women that is NOT in the used list.\n\n"
            "Topics to rotate: Skincare, Mental health, Fitness, Nutrition, Work-life balance, Fashion.\n"
            "After selecting, UPDATE memory/tips-history.json by adding this tip to the 'used' array."
        )

    if job_name == "afternoon-jokes":
        return (
            "Read memory/jokes-history.json and check the 'used' array. Search for 2-3 fresh, clean, funny jokes that are NOT in the used list. Include one tech joke, one general joke, one pun.\n\n"
            "After selecting, UPDATE memory/jokes-history.json by adding these jokes to the 'used' array."
        )

    if job_name == "goodnight-story":
        return (
            "Read memory/stories-history.json and check the 'used' array. Search for a short bedtime story (under 300 words) that is NOT in the used list.\n\n"
            "Topics to rotate: Indian mythology folktale, Motivational story, Nature story, Historical anecdote.\n"
            "After selecting, UPDATE memory/stories-history.json by adding this story topic to the 'used' array."
        )

    if job_name == "good-morning-dm":
        return (
            "It's morning in India (IST). Search for: 1) A daily motivational quote, 2) Any interesting news from last night, 3) A positive affirmation. "
            "Send a warm, personal good morning message to Nemesis. Keep it brief, heartfelt, end with an emoji."
        )

    if job_name == "good-morning-group":
        return (
            "Search for a trending topic or interesting fact from today. Post a good morning message to the group with: 1) Warm greeting, 2) One interesting thing happening today, 3) An engaging question for the group. Keep it natural."
        )

    if job_name == "ai-news-digest":
        return (
            "Search for today's top AI and tech news. Create a concise digest with: 1) 3-5 key headlines, 2) One sentence summary each, 3) Most interesting story highlighted. Format as a clean list."
        )

    if job_name == "daily-war-update":
        today = get_ist_time().strftime("%Y-%m-%d")
        return (
            f"Today's date is {today}. Provide a comprehensive global war and conflict update for Nemesis with:\n"
            "- Historical Context (~100 words): Overview of major ongoing global conflicts, focus on Iran-US situation, other significant conflicts worldwide, brief context on how situations evolved\n"
            "- Last 24 Hours Developments: Key events, specific updates on Iran-US tensions, other conflict zone updates, diplomatic initiatives\n"
            "- India-Specific Implications: How conflicts affect India's interests, predictions for future impact, India's potential role\n\n"
            "Cross-verify information using multiple sources (web search). Be concise but comprehensive. If uncertain, state the uncertainty rather than guessing. Send result to Nemesis via Telegram."
        )

    return ""


def get_job_target(job_name: str) -> str:
    return {
        "word-of-the-day": "main_group",
        "nightly-memory-review": "nemesis_dm",
        "hourly-memory-summary": "monitor_group",
        "feminine-tip-daily": "sravya_dm",
        "afternoon-jokes": "main_group",
        "goodnight-story": "nemesis_dm",
        "good-morning-dm": "nemesis_dm",
        "good-morning-group": "main_group",
        "ai-news-digest": "nemesis_dm",
        "daily-war-update": "nemesis_dm",
    }.get(job_name, "main_group")


def execute_job(job_name: str) -> None:
    """Single execution path for every job.

    Guarantees one completion notification per run.
    """
    started = get_ist_time()
    result_status = "SUCCESS"
    details = ""

    def fail_with_details(prefix: str, exc: Exception) -> Tuple[str, str]:
        tb = traceback.format_exc().strip()
        err = f"{prefix}: {type(exc).__name__}: {exc}"
        if tb:
            err = f"{err} | Traceback: {tb}"
        return "FAILED", err

    try:


        if job_name == "git-auto-commit":
            # Try once, then retry once on timeout.
            script = WORKSPACE / "scripts" / "git_backup.sh"
            try:
                result = run_command([str(script)], timeout=60)
            except subprocess.TimeoutExpired:
                try:
                    result = run_command([str(script)], timeout=60)
                except Exception as exc:
                    result_status, details = fail_with_details("git backup timeout retry failed", exc)
                    return

            if result.returncode != 0:
                stdout = (result.stdout or "").strip()
                stderr = (result.stderr or "").strip()
                details = " | ".join(
                    part for part in ["Git backup failed", f"stdout={stdout}" if stdout else "", f"stderr={stderr}" if stderr else ""] if part
                )
                result_status = "FAILED"
                return

            details = "git backup completed"
            return

        if job_name == "daily-session-reset":
            script = WORKSPACE / "scripts" / "new_session_daily.sh"
            try:
                result = run_command([str(script)], timeout=30)
            except subprocess.TimeoutExpired:
                try:
                    result = run_command([str(script)], timeout=30)
                except Exception as exc:
                    result_status, details = fail_with_details("daily session reset timeout retry failed", exc)
                    return

            if result.returncode != 0:
                stdout = (result.stdout or "").strip()
                stderr = (result.stderr or "").strip()
                details = " | ".join(
                    part for part in ["Daily session reset failed", f"stdout={stdout}" if stdout else "", f"stderr={stderr}" if stderr else ""] if part
                )
                result_status = "FAILED"
                return

            details = "daily session reset completed"
            return

        if job_name == "memory-batch-sync":
            try:
                result = run_command(["python3", str(WORKSPACE / "scripts" / "memory_batch_sync.py")], timeout=30)
            except subprocess.TimeoutExpired:
                try:
                    result = run_command(["python3", str(WORKSPACE / "scripts" / "memory_batch_sync.py")], timeout=30)
                except Exception as exc:
                    result_status, details = fail_with_details("memory batch sync timeout retry failed", exc)
                    return

            if result.returncode != 0:
                stdout = (result.stdout or "").strip()
                stderr = (result.stderr or "").strip()
                details = " | ".join(
                    part for part in ["Memory batch sync failed", f"stdout={stdout}" if stdout else "", f"stderr={stderr}" if stderr else ""] if part
                )
                result_status = "FAILED"
                return

            details = "memory batch sync completed"
            return

        if job_name == "memory-archive":
            try:
                result = run_command(["python3", str(WORKSPACE / "scripts" / "memory_archive.py")], timeout=60)
            except subprocess.TimeoutExpired:
                try:
                    result = run_command(["python3", str(WORKSPACE / "scripts" / "memory_archive.py")], timeout=60)
                except Exception as exc:
                    result_status, details = fail_with_details("memory archive timeout retry failed", exc)
                    return

            if result.returncode != 0:
                stdout = (result.stdout or "").strip()
                stderr = (result.stderr or "").strip()
                details = " | ".join(
                    part for part in ["Memory archive failed", f"stdout={stdout}" if stdout else "", f"stderr={stderr}" if stderr else ""] if part
                )
                result_status = "FAILED"
                return

            details = "memory archive completed"
            return

        if job_name in {
            "word-of-the-day",
            "nightly-memory-review",
            "hourly-memory-summary",
            "feminine-tip-daily",
            "afternoon-jokes",
            "goodnight-story",
            "good-morning-dm",
            "good-morning-group",
            "ai-news-digest",
            "daily-war-update",
        }:
            msg = build_job_message(job_name)
            target_key = get_job_target(job_name)
            ok, info = run_isolated_job(job_name, msg, target_key)
            if ok:
                details = info
            else:
                result_status = "FAILED"
                details = info
            return

        # Default: no special logic. Run a no-op but still report it so the run is visible.
        details = f"no handler for {job_name}"

    except Exception as exc:
        result_status, details = fail_with_details("job execution failed", exc)
    finally:
        elapsed = (get_ist_time() - started).total_seconds()
        final_details = details or f"completed in {elapsed:.1f}s"
        log_and_notify(job_name, result_status, final_details)


def should_run(time_str: str, now: datetime, last_run: Dict[str, str], job_name: str) -> bool:
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
        allowed_minutes = [int(m) for m in time_str.split(",") if m.strip().isdigit()]
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


def mark_ran(state: Dict[str, Any], job_name: str, now: datetime) -> None:
    state.setdefault("last_run", {})
    state["last_run"][job_name] = f"{now.strftime('%Y-%m-%d')}-{now.strftime('%H:%M')}"


def run_scheduler_once() -> None:
    state = load_state()
    now = get_ist_time()

    for time_str, job_name in SCHEDULE:
        if should_run(time_str, now, state.get("last_run", {}), job_name):
            execute_job(job_name)
            mark_ran(state, job_name, now)
            save_state(state)


if __name__ == "__main__":
    # Manual job trigger via command line:
    # python3 scheduler.py job-name
    # Or run the scheduler loop once:
    # python3 scheduler.py
    if len(sys.argv) > 1:
        execute_job(sys.argv[1])
    else:
        run_scheduler_once()

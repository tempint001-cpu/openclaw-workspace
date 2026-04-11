# TOOLS.md — Local Notes

## TTS
- TTS Style: Dynamic. Use a sharp, professional tone for daily tasks, and shift to warm/flirty ONLY when the conversation shifts to intimacy or casual storytelling.
- Voice works well for stories, jokes, pep talks
- Can't do Hindi/Odia voice naturally (English TTS only)

## Devices & Environment
- Server: Debian Bookworm (slim), volume at /root
- Gateway: loopback only, token auth
- Git: auto-push every 2h via cron. This must execute SILENTLY. Only alert Nemesis if the push fails.

## API Keys
- Gemini: used for web search AND memory embeddings
- Gemini Free Tier (1K embeddings/day): Optimize by ONLY embedding hard facts, decisions, and new persona details. DO NOT embed casual banter, generic agreements, or heartbeat checks.
- Telegram bot token: configured

## Quick Reference
- Config: ~/.openclaw/openclaw.json (JSON5, hot-reloads)
- Workspace: ./
- Full system reference: docs/openclaw-reference.md

<!-- BEGIN:kilo-cli -->
## Kilo CLI

The Kilo CLI (`kilo`) is an agentic coding assistant for the terminal, pre-configured with your KiloCode account.

- Interactive mode: `kilo`
- Autonomous mode: `kilo run --auto "your task description"`
- Config: `/root/.config/kilo/opencode.json` (customizable, persists across restarts)
- Shares your KiloCode API key and model access with OpenClaw
<!-- END:kilo-cli -->

<!-- BEGIN:scheduler -->
## Custom Scheduler

**DO NOT USE OPENCLAW CRON JOBS. THEY ARE BROKEN.**

We use our own custom scheduler script that runs once per minute. It is 100% reliable and will never get reset by gateway updates.

✅ Location: `./scripts/scheduler.py` (workspace-relative)
✅ Runs every minute via single cron entry
✅ Bypasses all broken OpenClaw cron logic completely
✅ All jobs run exactly on time
✅ All content jobs use AI search (dynamic, no duplicates)

### Adding a new job:
Edit `SCHEDULE` array in `scheduler.py`, add your time and job name. No other changes required.

### Current Schedule (IST) - 13 jobs:
| Time | Job | Type |
|------|-----|------|
| 04:00 | memory-archive | Internal (archives old daily files) |
| 06:00 | daily-session-reset | Internal |
| 07:00 | good-morning-dm | AI Search (dynamic) |
| 07:30 | ai-news-digest | AI Search (dynamic) |
| 08:00 | good-morning-group | AI Search (dynamic) |
| 09:00 | daily-war-update | AI Search (dynamic) |
| 10:00 | word-of-the-day | AI Search (dynamic) |
| 15:00 | feminine-tip-daily | AI Search (dynamic) |
| 16:00 | afternoon-jokes | AI Search (dynamic) |
| 22:00 | goodnight-story | AI Search (dynamic) |
| 03:00 | nightly-memory-review | Internal |
| 00,15,30,45 | memory-batch-sync | Internal (every 15 min) |
| 01 | git-auto-commit | Internal (hourly) |
<!-- END:scheduler -->
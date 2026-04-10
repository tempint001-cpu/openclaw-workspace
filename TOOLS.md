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

✅ Location: `/root/.openclaw/workspace/scripts/scheduler.py`
✅ Runs every minute via single cron entry
✅ Bypasses all broken OpenClaw cron logic completely
✅ All jobs run exactly on time

### Adding a new job:
Edit `SCHEDULE` array in `scheduler.py`, add your time and job name. No other changes required.

### Current Schedule (IST):
| Time | Job |
|---|---|
| 07:00 | Good morning DM |
| 07:30 | AI News digest DM |
| 08:00 | Good morning group |
| 09:00 | Daily war update DM |
| 10:00 | Word of the day group |
| 15:00 | Feminine tip group |
| 16:00 | Afternoon jokes group |
| 22:00 | Goodnight story group |
| 03:00 | Nightly memory review |
<!-- END:scheduler -->
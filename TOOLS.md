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
## Scheduling & Automation

All background tasks, scheduled messages, and system jobs are managed natively by the **OpenClaw Cron** engine and the system `crontab`.

✅ Initialization: Run `bash scripts/bootstrap_automation.sh` once to register all tasks.
✅ View Jobs: Use `openclaw cron list` or `crontab -l`.
✅ Job Architecture: AI-driven tasks run via OpenClaw isolated cron. Simple utility scripts (like git auto-commit or memory archival) run via Linux system cron.

### Current Schedule (IST):
**Time Awareness Directive:** To know the current time, ALWAYS look at the timestamp prepended to Nemesis's latest message in the chat log (e.g., `[4/12/2026 3:04 PM]`). Do NOT run tools to get the time. 
**Schedule Directive:** When asked about upcoming jobs, reference this table, compare it to the current time from the chat log, and calculate how many minutes remain until the job triggers.

| Time | Job | Type |
|------|-----|------|
| 03:10 | nightly-memory-review | OpenClaw AI Job |
| 04:30 | memory-archive | System Cron |
| 06:30 | daily-session-reset | System Cron |
| 07:10 | good-morning-dm | OpenClaw AI Job |
| 07:30 | ai-news-digest | OpenClaw AI Job |
| 08:10 | good-morning-group | OpenClaw AI Job |
| 09:10 | daily-war-update | OpenClaw AI Job |
| 10:10 | word-of-the-day | OpenClaw AI Job |
| 15:10 | feminine-tip-daily | OpenClaw AI Job |
| 16:10 | afternoon-jokes | OpenClaw AI Job |
| 22:10 | goodnight-story | OpenClaw AI Job |
| hourly at :00 | hourly-memory-summary | OpenClaw AI Job |
| hourly at :15 | git-auto-commit | System Cron |
| hourly at :20 | heartbeat-health-check | System Cron |
<!-- END:scheduler -->
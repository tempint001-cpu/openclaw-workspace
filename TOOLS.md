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
- Cron context: CRON-CONTEXT.md

<!-- BEGIN:kilo-cli -->
## Kilo CLI

The Kilo CLI (`kilo`) is an agentic coding assistant for the terminal, pre-configured with your KiloCode account.

- Interactive mode: `kilo`
- Autonomous mode: `kilo run --auto "your task description"`
- Config: `/root/.config/kilo/opencode.json` (customizable, persists across restarts)
- Shares your KiloCode API key and model access with OpenClaw
<!-- END:kilo-cli -->
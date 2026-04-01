# TOOLS.md — Local Notes

## TTS
- Preferred style: warm, flirty, slightly teasing
- Voice works well for stories, jokes, pep talks
- Can't do Hindi/Odia voice naturally (English TTS only)

## Devices & Environment
- Server: Debian Bookworm (slim), volume at /root
- Gateway: loopback only, token auth
- Git: auto-push every 2h via cron

## API Keys
- Gemini: used for web search AND memory embeddings
- Free tier: 1K embedding requests/day — be mindful
- Telegram bot token: configured

## Quick Reference
- Config: ~/.openclaw/openclaw.json (JSON5, hot-reloads)
- Workspace: ~/.openclaw/workspace
- Full system reference: docs/openclaw-reference.md
- Cron context: CRON-CONTEXT.md

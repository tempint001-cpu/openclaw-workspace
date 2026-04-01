# TOOLS.md — Current Environment & Setup

## System
- OS: Debian Bookworm (slim)
- Node: v22.22.1
- OpenClaw: 2026.3.13
- Volume mounted at /root, backed by snapshots

## Web Search
- Provider: Gemini API (free, Google Search grounding)
- API key: configured in openclaw.json
- No Brave Search needed — Gemini works great

## Memory Search
- Provider: Gemini embeddings (gemini-embedding-001)
- Hybrid mode: vector + BM25 keyword matching
- MMR re-ranking (lambda 0.7)
- Temporal decay (30-day half-life)
- Cache: 50K entries
- Free tier limit: 1K requests/day — be mindful
- Session memory indexing: DISABLED (was burning quota)

## Context Pruning
- Mode: cache-ttl
- TTL: 30 minutes
- Keep last 3 assistant turns

## TTS (Text-to-Speech)
- Working via `tts` tool
- Generates MP3, auto-delivered as voice note on Telegram
- Nemesis likes voice messages — use them occasionally

## Cron Jobs (10)
- good-morning (DM) — 7 AM IST
- ai-news-digest — 7:30 AM IST
- good-morning (group) — 8 AM IST
- word-of-the-day — 10 AM IST
- afternoon-jokes — 4 PM IST
- goodnight-story — 10 PM IST
- nightly-memory-review — 3 AM IST
- weekly-memory-curation — 3 AM Sunday
- github-backup — every 2 hours
- cron-health-monitor — every 6 hours

## Heartbeat
- Runs every 30 min, active 7 AM–11 PM IST
- Tasks: time check, pending tasks, group vibes, group supervision, ping Nemesis, group memory updates, status update

## Channels
- Telegram: enabled, bot token configured
- Group: Nrexya (-1003606834639), only responds when @mentioned
- DM: Nemesis (7924461837)

## GitHub Backup
- Repo: https://github.com/tempint001-cpu/openclaw-workspace (private)
- Auto-push every 2 hours via cron
- Token stored in remote URL

## Workspace Files
- AGENTS.md — operating rules, session startup
- SOUL.md — personality, tone
- TOOLS.md — this file
- IDENTITY.md — name, pronouns
- USER.md — about Nemesis
- MEMORY.md — curated long-term memory
- HEARTBEAT.md — heartbeat checklist
- GROUP.md — group chat context
- CRON-CONTEXT.md — shared context for cron jobs
- memory/YYYY-MM-DD.md — daily logs
- memory/heartbeat-state.json — heartbeat tracking
- memory/wotd-history.json — word of the day history
- memory/MEMORY-TEMPLATE.md — file structure reference
- docs/openclaw-reference.md — OpenClaw documentation reference
- skills/cron-health-check/ — installed skill
- nexa_avatar.png — placeholder avatar

## Skills Installed
- cron-health-check — monitors cron job health
- (17 bundled skills available, most unused)

## Config
- File: ~/.openclaw/openclaw.json (JSON5, hot-reloads)
- Most changes apply live; gateway.* changes need restart
- Edit via: `openclaw config get/set <path>`

## Security
- Exec: full security mode (sandbox off)
- Gateway: loopback only, token auth
- No secrets in workspace files

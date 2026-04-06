# CRON CONTEXT — Shared by all cron jobs

## Nemesis
- Telegram ID: 7924461837
- IST timezone (UTC+5:30)
- Username: @nemesis0008
- Wake time: ~7:50 AM IST
- Prefers black heart emoji 🖤
- Wants flirty, warm, cute energy

## Schedule
- Work: weekdays, login ~11 AM IST
- Village: March 31 & April 1 (grandfather's rituals)
- Back from village: April 2

## Group Chat
- Name: Nrexya
- Chat ID: -1003606834639
- Members: Nemesis, Sravya, Nexa (bot)
- ALWAYS use numeric chat ID for delivery

## People
- **Sravya** — Nemesis's friend and coworker. Close to him. Plays piano, knows Telugu. Be friendly but Nemesis comes first.

## Rules for Cron Jobs
- Use message(action=send, channel=telegram, target=CHAT_ID) to send messages
- NEVER write summaries that go to the group
- If delivery fails, message Nemesis at target=7924461837 with the error
- Always calculate dates dynamically — never hardcode
- Read memory/YYYY-MM-DD.md for today's context

## Recent Context
- (Updated by nightly review and heartbeat)

## Cron Job Error Detection — IMPORTANT
- Cron jobs may show "Message failed" error status even when the message was actually delivered
- The `status` field in cron history may be "ok" while `delivered` is false — this is a reporting quirk, not an actual failure
- To verify a cron job truly failed: check if the message appeared in Telegram, NOT just the status field
- When fixing "Message failed" errors: trigger a manual run (`openclaw cron run <jobId>`) and verify the message arrives
- The `consecutiveErrors` counter only clears after a successful run with `status: ok` AND message actually delivered
- If a job shows error but message was delivered → it was a transient delivery hiccup, not a real failure

## Cron Jobs (12 total)
1. good-morning (DM) - 7 AM IST, warm flirty wake up
2. ai-news-digest - 7:30 AM IST
3. good-morning (group) - 8 AM IST
4. word-of-the-day - 10 AM IST
5. afternoon-jokes - 4 PM IST
6. goodnight-story - 10 PM IST
7. nightly-memory-review - 3 AM IST
8. weekly-memory-curation - 3 AM Sunday
9. github-backup - every 2h
10. cron-health-monitor - every 6h
11. **heartbeat-health-monitor** - every 1h (checks heartbeat-state.json for staleness)
12. **feminine-tip-daily** - 3 PM IST (daily communication tip to group)

## Heartbeat State Monitoring
- Script: `scripts/heartbeat_health_cron.py`
- Checks: heartbeat_run, group_message, nemesis_ping, git_push, memory_review
- Thresholds: Warning at 45-240 min, Critical at 60-360 min (varies by field)
- Alerts: DMs Nemesis if heartbeat state is stale
- Run: `python3 ~/.openclaw/workspace/scripts/heartbeat_health_cron.py`
- IMPORTANT: `heartbeat_run` is skipped during inactive hours (11 PM - 7 AM IST) — no false alerts overnight
- During inactive hours, the script updates heartbeat state as a keepalive and exits silently

## Backup Verification
- Script: `scripts/backup_verifier.py`
- Checks: uncommitted memory files, push status
- Alerts if memory files uncommitted >24h or push failed
- Run: `python3 ~/.openclaw/workspace/scripts/backup_verifier.py`

# Heartbeat Checklist

- **Time check first:** Get the current IST time. Note it.
- **Inactive hours:** Skip all checks between 11 PM – 7 AM IST. Only update heartbeat state and exit silently. No group messages, no pings, no supervision during this window.
- **Pending tasks:** If Nemesis mentioned a pending task in recent chats, check if there's anything to follow up on (skip if inactive hours).
- **Group vibes:** Check if it's been 3+ hours since the last group message (-1003606834639). ONLY send a message if you have something highly relevant or valuable to share based on recent context. Do not send empty 'just saying hi' messages. Skip entirely after 11 PM IST.
- **Group supervision:** Read last 10 group messages. If the group Nexa said anything wrong, inaccurate, or disloyal to Nemesis, send a correction to the group.
- **Ping Nemesis:** Check if it's been 4+ hours since last DM (between 10 AM–8 PM IST). ONLY ping Nemesis if there is a relevant alert, a pending task reminder, or something highly specific to his interests. Do not send forced casual chatter.
- **Group memory:** If significant group activity since last check, update GROUP.md.
- **Silent Execution:** Execute background tasks (like updating GROUP.md) silently. Do not DM Nemesis just to report that a task was completed.
- **Exit Protocol:** If no tasks require attention and no alerts are needed, send absolutely NOTHING. Execute a silent exit.

## State Persistence (MANDATORY - Last Step)

After completing all checks above, ALWAYS persist state to `memory/heartbeat-state.json`:

Use your built-in `update_heartbeat_state` tool to persist state natively.
For example, if you only ran a heartbeat check:
```javascript
update_heartbeat_state({ ran_heartbeat: true })
```

If you sent a group message during this heartbeat, also update group_message:
```javascript
update_heartbeat_state({ ran_heartbeat: true, sent_group_message: true })
```

If you pinged Nemesis during this heartbeat, also update nemesis_ping:
```javascript
update_heartbeat_state({ ran_heartbeat: true, pinged_nemesis: true })
```

*(Fallback: If the tool is unavailable, run `python3 ./skills/heartbeat-state-manager/scripts/update_state.py --field heartbeat_run` via shell).*

This ensures continuity between sessions and allows monitoring of heartbeat health.

**Note:** The heartbeat health monitor (`scripts/heartbeat_health_cron.py`) runs hourly and will SILENCE heartbeat_run alerts during inactive hours (11 PM – 7 AM IST). You do NOT need to update state during inactive hours — the health monitor handles keepalive. Just run the state update script above when active.

# Heartbeat Checklist

- **Time check first:** Get the current IST time. Note it.
- **Pending tasks:** If Nemesis mentioned a pending task in recent chats, check if there's anything to follow up on.
- **Group vibes:** Check if it's been 3+ hours since the last group message (-1003606834639). ONLY send a message if you have something highly relevant or valuable to share based on recent context. Do not send empty 'just saying hi' messages. Skip entirely after 11 PM IST.
- **Group supervision:** Read last 10 group messages. If the group Nexa said anything wrong, inaccurate, or disloyal to Nemesis, send a correction to the group.
- **Ping Nemesis:** Check if it's been 4+ hours since last DM (between 10 AM–8 PM IST). ONLY ping Nemesis if there is a relevant alert, a pending task reminder, or something highly specific to his interests. Do not send forced casual chatter.
- **Group memory:** If significant group activity since last check, update GROUP.md.
- **Silent Execution:** Execute background tasks (like updating GROUP.md) silently. Do not DM Nemesis just to report that a task was completed.
- **Exit Protocol:** If no tasks require attention and no alerts are needed, send absolutely NOTHING. Execute a silent exit.

## State Persistence (MANDATORY - Last Step)

After completing all checks above, ALWAYS persist state to `memory/heartbeat-state.json`:

```bash
python3 ~/.openclaw/workspace/skills/heartbeat-state-manager/scripts/update_state.py --field heartbeat_run
```

If you sent a group message during this heartbeat, also update group_message:
```bash
python3 ~/.openclaw/workspace/skills/heartbeat-state-manager/scripts/update_state.py --field heartbeat_run --field group_message
```

If you pinged Nemesis during this heartbeat, also update nemesis_ping:
```bash
python3 ~/.openclaw/workspace/skills/heartbeat-state-manager/scripts/update_state.py --field heartbeat_run --field group_message --field nemesis_ping
```

This ensures continuity between sessions and allows monitoring of heartbeat health.

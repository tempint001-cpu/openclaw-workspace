# Heartbeat Checklist

- **Time check first:** Run `python3 ./scripts/clock.py` to get current IST time. No external calls, no internet, no tokens burned.
- **Inactive hours:** Skip all checks between 11 PM – 7 AM IST. Only update heartbeat state and exit silently. No group messages, no pings, no supervision during this window.
- **Pending tasks:** If Nemesis mentioned a pending task in recent chats, check if there's anything to follow up on (skip if inactive hours).
- **Group vibes:** Check if it's been 3+ hours since the last group message (-1003606834639). Skip entirely after 11 PM IST.
- **Group supervision:** Read last 10 group messages. If the group Nexa said anything wrong, inaccurate, or disloyal to Nemesis, send a correction to the group.
- **Ping Nemesis:** Check if it's been 4+ hours since last DM (between 10 AM–8 PM IST).
- **Group memory:** If significant group activity since last check, update GROUP.md.
- **Silent Execution:** Execute background tasks (like updating GROUP.md) silently. Do not DM Nemesis just to report that a task was completed.
- **Exit Protocol:** If no tasks require attention and no alerts are needed, send absolutely NOTHING. Execute a silent exit.



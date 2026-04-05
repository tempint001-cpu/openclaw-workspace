---
name: heartbeat-state-manager
description: Manages and persists heartbeat state to heartbeat-state.json
version: 1.0.0
---

# Heartbeat State Manager

Persists heartbeat check timestamps to `memory/heartbeat-state.json` for continuity between sessions.

## State Fields

| Field | Description | Updated By |
|-------|-------------|------------|
| `lastChecks.memory_review` | Last nightly memory review run | Nightly review cron |
| `lastChecks.group_message` | Last group message sent | Heartbeat group check |
| `lastChecks.git_push` | Last successful GitHub push | Git backup cron |
| `lastChecks.nemesis_ping` | Last DM ping to Nemesis | Heartbeat ping check |
| `lastChecks.heartbeat_run` | Last heartbeat execution | This skill |

## Usage

```bash
# Get current state
python3 {baseDir}/scripts/get_state.py

# Update specific field
python3 {baseDir}/scripts/update_state.py --field group_message

# Update multiple fields
python3 {baseDir}/scripts/update_state.py --field group_message --field nemesis_ping

# Full health check (returns staleness info)
python3 {baseDir}/scripts/health_check.py
```

## Heartbeat Integration

Add this as the **last step** of every heartbeat run:

```python
import subprocess
subprocess.run([
    "python3",
    "{baseDir}/scripts/update_state.py",
    "--field", "heartbeat_run"
])
```

## Health Check Thresholds

| Field | Warning | Critical |
|-------|---------|----------|
| heartbeat_run | >45 min | >60 min |
| group_message | >4 hours | >6 hours |
| nemesis_ping | >6 hours | >8 hours |
| git_push | >3 hours | >6 hours |
| memory_review | >26 hours | >30 hours |

## File Location

State file: `memory/heartbeat-state.json`

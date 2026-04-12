#!/bin/bash
# Daily clean session reset at 6 AM IST

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"
MONITOR_GROUP="-1003951451198"

notify() {
    openclaw message send --channel telegram --to "${MONITOR_GROUP}" --message "[$(date +'%H:%M IST')] $1"
}

notify "🔄 Starting daily session reset..."

# Clear temporary state (except heartbeat-state.json - keep for health tracking)
rm -f memory/scheduler_state.json
# rm -f memory/heartbeat-state.json  # Kept for continuity
notify "✅ Cleared temporary state files"

# Create fresh daily memory file for today
TODAY=$(date +'%Y-%m-%d')
DAILY_FILE="memory/${TODAY}.md"

if [ ! -f "${DAILY_FILE}" ]; then
    echo "# ${TODAY}" > "${DAILY_FILE}"
    echo "" >> "${DAILY_FILE}"
    echo "## Events" >> "${DAILY_FILE}"
    echo "- Daily session reset at 06:00 IST" >> "${DAILY_FILE}"
    echo "" >> "${DAILY_FILE}"
    echo "## Notes" >> "${DAILY_FILE}"
    echo "" >> "${DAILY_FILE}"
    notify "✅ Created new daily memory file: ${TODAY}.md"
else
    notify "ℹ️ Daily file already exists, skipping creation"
fi

# Commit clean state
git add "${DAILY_FILE}"
git commit -m "daily reset: ${TODAY}" --quiet
if [ $? -eq 0 ]; then
    notify "✅ Committed clean state"
else
    notify "⚠️ Nothing to commit"
fi

git push --quiet
if [ $? -eq 0 ]; then
    notify "✅ Pushed successfully to GitHub"
else
    notify "❌ FAILED to push to GitHub"
fi

notify "✅ New daily session initialized complete for ${TODAY}"
exit 0

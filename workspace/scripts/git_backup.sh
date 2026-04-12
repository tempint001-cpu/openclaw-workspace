#!/bin/bash
cd "$(dirname "$0")/../.."

git add MEMORY.md GROUP.md AGENTS.md SOUL.md USER.md HEARTBEAT.md TOOLS.md memory/*.md

if git diff --cached --quiet; then
  # No changes, exit silently
  exit 0
fi

git commit -m "auto backup: $(date +'%Y-%m-%d %H:%M IST')"
if [ $? -ne 0 ]; then
  echo "Git auto-backup failed: commit error"
  exit 1
fi

git push
if [ $? -ne 0 ]; then
  echo "Git auto-backup failed: push error"
  exit 1
fi

echo "Git auto-backup completed successfully"
exit 0

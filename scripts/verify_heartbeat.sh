#!/usr/bin/env bash
# verify_heartbeat.sh - Quick health check for heartbeat state
# Run this to verify heartbeat is updating state properly

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_DIR="$BASE_DIR/skills/heartbeat-state-manager"

echo "=========================================="
echo "HEARTBEAT STATE VERIFICATION"
echo "=========================================="
echo ""

# Check if state file exists
STATE_FILE="$BASE_DIR/memory/heartbeat-state.json"
if [ ! -f "$STATE_FILE" ]; then
    echo "✗ State file not found: $STATE_FILE"
    echo "  Heartbeat may not be persisting state"
    exit 1
fi

echo "✓ State file exists: $STATE_FILE"
echo ""

# Check if health check script exists
if [ -f "$SKILL_DIR/scripts/health_check.py" ]; then
    echo "Running health check..."
    echo ""
    python3 "$SKILL_DIR/scripts/health_check.py"
    exit $?
else
    echo "✗ Health check script not found"
    echo ""
    echo "Current state:"
    cat "$STATE_FILE"
    exit 1
fi

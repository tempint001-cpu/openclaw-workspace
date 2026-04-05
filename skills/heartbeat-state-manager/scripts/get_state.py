#!/usr/bin/env python3
"""
Get current heartbeat state from heartbeat-state.json
"""

import json
import sys
from pathlib import Path


def get_state():
    state_file = Path(__file__).parent.parent.parent / "memory" / "heartbeat-state.json"

    if not state_file.exists():
        print(json.dumps({"error": "State file not found"}, indent=2))
        return

    with open(state_file, "r") as f:
        state = json.load(f)

    print(json.dumps(state, indent=2))


if __name__ == "__main__":
    get_state()

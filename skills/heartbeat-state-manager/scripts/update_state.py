#!/usr/bin/env python3
"""
Update heartbeat state field(s) in heartbeat-state.json
Usage: update_state.py --field field_name [--field field_name ...]
"""

import json
import argparse
from datetime import datetime, timezone
from pathlib import Path


def get_state_file():
    return Path(__file__).parent.parent.parent / "memory" / "heartbeat-state.json"


def load_state():
    state_file = get_state_file()

    if state_file.exists():
        with open(state_file, "r") as f:
            return json.load(f)

    return {"lastChecks": {}}


def save_state(state):
    state_file = get_state_file()
    state_file.parent.mkdir(parents=True, exist_ok=True)

    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)


def update_fields(fields):
    state = load_state()
    now = datetime.now(timezone.utc).isoformat()

    for field in fields:
        if field not in state["lastChecks"]:
            state["lastChecks"][field] = None

        state["lastChecks"][field] = now

    save_state(state)

    print(f"Updated: {', '.join(fields)}")
    print(f"Timestamp: {now}")


def main():
    parser = argparse.ArgumentParser(description="Update heartbeat state")
    parser.add_argument(
        "--field",
        action="append",
        required=True,
        help="Field to update (can be specified multiple times)",
    )

    args = parser.parse_args()
    update_fields(args.field)


if __name__ == "__main__":
    main()

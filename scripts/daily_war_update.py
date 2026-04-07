#!/usr/bin/env python3
"""
Daily War Update Script - Triggers AI agent to generate war update via agentTurn
"""

import json
import subprocess
import sys
from datetime import datetime, timezone, timedelta


def main():
    # Get current time for context
    now_utc = datetime.now(timezone.utc)
    ist_offset = timedelta(hours=5, minutes=30)
    now_ist = now_utc + ist_offset
    date_str = now_ist.strftime("%Y-%m-%d")

    # Create the prompt for the AI agent
    prompt = f"""Today's date is {date_str}. 

Please provide a comprehensive global war and conflict update for Nemesis with the following structure:

**Historical Context (approximately 100 words, excluding the 24hr update):**
- Overview of major ongoing global conflicts and tensions
- Focus on Iran-US situation as requested
- Include other significant conflicts worldwide
- Brief context on how situations have evolved to current state

**Last 24 Hours Developments:**
- Key events and developments in the last 24 hours
- Specific updates on Iran-US tensions
- Other significant conflict zone updates
- Any diplomatic initiatives or escalations

**India-Specific Implications:**
- How these conflicts affect India's interests
- Predictions for future impact on India based on current trends
- India's potential role or stance in these situations

**Important Instructions:**
- Cross-verify information using multiple sources before presenting facts
- Keep the historical summary to approximately 100 words (not including the 24hr update section)
- Be concise but comprehensive
- Use clear, accessible language
- If uncertain about any information, state the uncertainty rather than guessing
- Format the response clearly with the section headers as shown above

Please execute this request using your available tools (including web search for verification) and send the result to Nemesis via Telegram message."""

    # Create a one-time cron job to execute this prompt as an agentTurn
    # Use --at with relative time "30s" to run in 30 seconds
    # NOTE: No --announce flag - the script handles its own message delivery
    cmd = [
        "openclaw",
        "cron",
        "add",
        "--name",
        "daily-war-update-execution",
        "--at",
        "30s",
        "--session",
        "isolated",
        "--message",
        prompt,
        "--delete-after-run",  # Clean up after execution
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Failed to create execution job: {result.stderr}")
        sys.exit(1)
    else:
        print("War update execution job created successfully")


if __name__ == "__main__":
    main()

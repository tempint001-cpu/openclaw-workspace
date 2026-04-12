#!/bin/bash
# Bootstrap OpenClaw Native Cron & System Crontab
# Replaces the legacy Python scheduler loop.

echo "=========================================="
echo "Bootstrapping OpenClaw Automation"
echo "=========================================="

# Define Targets
MAIN_GROUP="-1003606834639"
MONITOR_GROUP="-1003951451198"
NEMESIS_DM="7924461837"
SRAVYA_DM="1880938940"

# Helper function to add openclaw cron jobs
add_oc_cron() {
    local name="$1"
    local cron="$2"
    local to="$3"
    local msg="$4"
    
    # Check if job already exists first
    if openclaw cron list | grep -q "$name"; then
        echo "✅ $name already exists, skipping."
        return 0
    fi
    
    echo "Registering $name..."
    openclaw cron add \
        --name "$name" \
        --cron "$cron" \
        --tz "Asia/Kolkata" \
        --session "isolated" \
        --announce \
        --channel "telegram" \
        --to "$to" \
        --message "$msg"
}

# 1. Register AI-Driven Jobs via OpenClaw
echo "Adding AI background tasks to OpenClaw..."

add_oc_cron "hourly-memory-summary" "0 * * * *" "$MONITOR_GROUP" \
"Hourly memory summary job:
1. Get all chat messages from last 60 minutes: both this DM and the main group
2. Extract: Hard facts, decisions, requests, bugs, changes, agreements, Mood, tone, emotional state, vibe, frustrations, satisfaction, Unspoken context, things implied between lines, Preferences, likes, dislikes that were shown not stated, Trust signals, jokes that landed, things that annoyed
3. Do NOT discard banter and casual talk - this is where most of the context lives.
4. Summarize cleanly, separate Facts section and Context / Tone section
5. Append this summary cleanly to today's daily memory file
6. No notifications required. Run silently."

add_oc_cron "nightly-memory-review" "10 3 * * *" "$NEMESIS_DM" \
"Run the nightly memory distillation process:
1. First read today's full daily memory file: memory/YYYY-MM-DD.md
2. Read the full MEMORY.md file
3. Review every single conversation from today, extract only: Important decisions made, New rules, agreements, requirements, Bugs found, issues fixed, Lessons learned, mistakes, New facts about people, preferences, boundaries, Infrastructure changes
4. Remove all casual banter, chit chat, filler messages. Only keep hard facts.
5. Merge the extracted clean facts into MEMORY.md under the correct sections
6. Do not duplicate existing entries
7. Update MEMORY.md cleanly
8. Send a short summary to Nemesis DM with how many items were added"

add_oc_cron "good-morning-dm" "10 7 * * *" "$NEMESIS_DM" \
"It's morning in India (IST). Search for: 1) A daily motivational quote, 2) Any interesting news from last night, 3) A positive affirmation. Send a warm, personal good morning message to Nemesis. Keep it brief, heartfelt, end with an emoji."

add_oc_cron "ai-news-digest" "30 7 * * *" "$NEMESIS_DM" \
"Search for today's top AI and tech news. Create a concise digest with: 1) 3-5 key headlines, 2) One sentence summary each, 3) Most interesting story highlighted. Format as a clean list."

add_oc_cron "good-morning-group" "10 8 * * *" "$MAIN_GROUP" \
"Search for a trending topic or interesting fact from today. Post a good morning message to the group with: 1) Warm greeting, 2) One interesting thing happening today, 3) An engaging question for the group. Keep it natural."

add_oc_cron "daily-war-update" "10 9 * * *" "$NEMESIS_DM" \
"Provide a comprehensive global war and conflict update for Nemesis with:
- Historical Context (~100 words): Overview of major ongoing global conflicts, focus on Iran-US situation, other significant conflicts worldwide, brief context on how situations evolved
- Last 24 Hours Developments: Key events, specific updates on Iran-US tensions, other conflict zone updates, diplomatic initiatives
- India-Specific Implications: How conflicts affect India's interests, predictions for future impact, India's potential role
Cross-verify information using multiple sources (web search). Be concise but comprehensive. If uncertain, state the uncertainty rather than guessing. Send result to Nemesis via Telegram."

add_oc_cron "word-of-the-day" "10 10 * * *" "$MAIN_GROUP" \
"Read memory/wotd-history.json and check the 'used' array. Search for an interesting, obscure English word (not commonly known) that is NOT in the used list. Get its definition, pronunciation (IPA), and a meaningful quote. After selecting, UPDATE memory/wotd-history.json by adding this word to the 'used' array. Format: 📚 Word of the Day: **Word** - Definition - Pronounced: /ipa/ - > \"quote\""

add_oc_cron "feminine-tip-daily" "10 15 * * *" "$SRAVYA_DM" \
"Read memory/tips-history.json and check the 'used' array. Search for a fresh, practical self-care or wellness tip for women that is NOT in the used list. Topics to rotate: Skincare, Mental health, Fitness, Nutrition, Work-life balance, Fashion. After selecting, UPDATE memory/tips-history.json by adding this tip to the 'used' array."

add_oc_cron "afternoon-jokes" "10 16 * * *" "$MAIN_GROUP" \
"Read memory/jokes-history.json and check the 'used' array. Search for 2-3 fresh, clean, funny jokes that are NOT in the used list. Include one tech joke, one general joke, one pun. After selecting, UPDATE memory/jokes-history.json by adding these jokes to the 'used' array."

add_oc_cron "goodnight-story" "10 22 * * *" "$NEMESIS_DM" \
"Read memory/stories-history.json and check the 'used' array. Search for a short bedtime story (under 300 words) that is NOT in the used list. Topics to rotate: Indian mythology folktale, Motivational story, Nature story, Historical anecdote. After selecting, UPDATE memory/stories-history.json by adding this story topic to the 'used' array."

echo "✅ OpenClaw AI Jobs Registered."

# 2. Register System Scripts to Linux Crontab
echo "Setting up Linux crontab for utility scripts..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="$(which python3)"

# Temporary file for crontab
CRON_FILE=$(mktemp)
crontab -l > "$CRON_FILE" 2>/dev/null || true

# Helper to add if missing
add_to_crontab() {
    local schedule="$1"
    local command="$2"
    if ! grep -Fq "$command" "$CRON_FILE"; then
        echo "$schedule $command >> ${SCRIPT_DIR}/../logs/cron.log 2>&1" >> "$CRON_FILE"
    fi
}

add_to_crontab "15 * * * *" "bash ${SCRIPT_DIR}/git_backup.sh"
add_to_crontab "20 * * * *" "${PYTHON_BIN} ${SCRIPT_DIR}/heartbeat_health_cron.py"
add_to_crontab "30 4 * * *" "${PYTHON_BIN} ${SCRIPT_DIR}/memory_archive.py"
add_to_crontab "30 6 * * *" "bash ${SCRIPT_DIR}/new_session_daily.sh"

crontab "$CRON_FILE"
rm -f "$CRON_FILE"

echo "✅ Linux Crontab updated."
echo ""
echo "Bootstrapping complete! You can now safely delete the custom scheduler."
echo "Use 'openclaw cron list' to view registered AI jobs."
echo "Use 'crontab -l' to view registered system scripts."

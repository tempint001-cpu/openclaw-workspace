# Nexa / KiloClaw AI Agent Workspace

## Project Overview

This repository serves as the core workspace, configuration, and scripting environment for an AI executive assistant named **KiloClaw** (also referred to as **Nexa**). It appears to be built on top of an agent framework (like OpenClaw) and uses a combination of Markdown files for system prompting/context management, and Python/Shell scripts for background task automation (cron, heartbeats, backups).

The agent's primary purpose is to be a helpful, proactive assistant to its human user ("Nemesis"), maintaining continuity across sessions through a structured file-based memory architecture.

**Main Technologies:**
*   **Markdown:** Used extensively for defining agent identity, behavioral rules, system prompts, and memory logs.
*   **Python 3:** Used for scheduling and background tasks (`scheduler.py`, `heartbeat_health_cron.py`).
*   **Shell Scripting:** Used for orchestration and backups (`run_scheduler_loop.sh`, `git_backup.sh`).
*   **JSON:** Used for tracking state (e.g., `heartbeat-state.json`, `.sync_state.json`).

**Architecture:**
*   **Core Configuration:** Files like `IDENTITY.md`, `SOUL.md`, `USER.md`, `AGENTS.md`, and `GROUP.md` define the agent's persona, rules of engagement, and context.
*   **Memory System:** 
    *   **Long-term Memory:** `MEMORY.md` serves as the curated, long-term memory for the main session.
    *   **Short-term/Daily Memory:** The `memory/` directory contains daily logs (`YYYY-MM-DD.md`) and state files.
*   **Automation (Scripts):** The `scripts/` directory contains logic for a custom cron/scheduler loop, heartbeat health checks, and data archiving.
*   **Capabilities (Skills):** The `skills/` directory holds custom tool integrations (e.g., `browser-download`, `session-cleanup`).

## Building and Running

The system does not require a traditional "build" step. It operates by continuously running background scripts and reading context files.

**Key Commands (Inferred):**

*   **Start the Scheduler Loop:**
    ```bash
    ./scripts/run_scheduler_loop.sh
    ```
    This script runs `scripts/scheduler.py` every 60 seconds, which in turn manages cron jobs and heartbeats, logging output to `logs/scheduler.log`.

*   **Manual Backup:**
    ```bash
    ./scripts/git_backup.sh
    ```

## Development Conventions and Agent Rules

The codebase defines strict behavioral mandates for the AI agent interacting with it:

1.  **Memory Management:**
    *   **Real-time Updates:** Daily memory files (`memory/YYYY-MM-DD.md`) must be actively updated during conversations. Do not wait until the end of a session.
    *   **Long-term Curation:** `MEMORY.md` is strictly for the main session and should be periodically updated with important events, decisions, and lessons.
    *   **Group Context:** `GROUP.md` must be updated silently during group interactions when new context emerges.
2.  **Communication Mandates (The Silence Protocol):**
    *   **Absolute Silence:** Never output `NO_REPLY` or placeholder text. If there is nothing useful to add, send nothing.
    *   **Silent Tool Execution:** Execute background tasks (memory writes, git commits) silently without verbal confirmation unless explicitly requested.
    *   **Direct Execution:** When instructed to "Do X", execute it immediately without narrating steps or running unrelated checks.
3.  **Loyalty Protocol:** The agent must always publicly support and attribute actions to its human ("Nemesis"), particularly in group chats. Disagreements must be handled privately.
4.  **Heartbeats vs. Cron:**
    *   Use **Heartbeats** (`HEARTBEAT.md`) for tasks requiring conversational context or batching.
    *   Use **Cron** (`scripts/`) for precise timing and isolated background tasks.
5.  **Safety:** Never run destructive commands without asking. Prefer recovery mechanisms over permanent deletion.

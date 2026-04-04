# OpenClaw Comprehensive Reference

> Practical reference for day-to-day OpenClaw operations. Written from official docs.
> Last updated: 2026-03-29

---

## 1. Architecture

### Gateway (Daemon)
- Single long-lived process owning all messaging surfaces (WhatsApp/Baileys, Telegram/grammY, Slack, Discord, Signal, iMessage, WebChat).
- Control-plane clients (macOS app, CLI, WebUI) connect via **WebSocket** on `127.0.0.1:18789` (default).
- **Nodes** (macOS/iOS/Android/headless) also connect over WebSocket with `role: node`.
- One Gateway per host; it's the only place that opens a WhatsApp session.
- Canvas host served under `/__openclaw__/canvas/` and `/__openclaw__/a2ui/` on the Gateway port.

### Agent Loop
1. `agent` RPC validates params, resolves session, persists metadata, returns `{ runId, acceptedAt }` immediately.
2. `agentCommand` runs: resolves model, loads skills, calls `runEmbeddedPiAgent`.
3. `runEmbeddedPiAgent`: serializes runs via per-session + global queues, resolves model+auth, subscribes to pi events, streams assistant/tool deltas, enforces timeout.
4. Events emitted: `lifecycle` (start/end/error), `assistant` (deltas), `tool` (start/update/end).
5. Runs are **serialized per session key** — no parallel tool calls within one session.

### Wire Protocol
- Transport: WebSocket, text frames with JSON payloads.
- First frame must be `connect`. After handshake: `{type:"req"}` → `{type:"res"}`, events are `{type:"event"}`.
- If `OPENCLAW_GATEWAY_TOKEN` is set, `connect.params.auth.token` must match.

### Remote Access
```bash
# SSH tunnel
ssh -N -L 18789:127.0.0.1:18789 user@host
# Or Tailscale serve/funnel
```

---

## 2. Configuration

### Basics
- Config file: `~/.openclaw/openclaw.json` (JSON5 — comments + trailing commas allowed).
- All fields optional — safe defaults when omitted.
- **Strict validation**: unknown keys cause Gateway to refuse to start.
- Hot reload: Gateway watches the file and applies changes automatically.

### Editing Config
```bash
openclaw onboard              # full setup wizard
openclaw configure            # config wizard
openclaw config get <path>    # read a value
openclaw config set <path> <value>
openclaw config unset <path>
openclaw config validate      # check against schema
openclaw config file          # show config file path
```

### Hot Reload Modes
```json5
{ gateway: { reload: { mode: "hybrid", debounceMs: 300 } } }
```
- `hybrid` (default): hot-applies safe changes, auto-restarts for critical ones.
- `hot`: hot-applies only, warns on restart-needed.
- `restart`: restarts on any change.
- `off`: no file watching.

**No restart needed**: channels, agents, models, hooks, cron, sessions, tools, skills, UI.
**Restart needed**: `gateway.*` (port, bind, auth, TLS), `discovery`, `plugins`.

### Config Includes
```json5
{
  agents: { $include: "./agents.json5" },
  broadcast: { $include: ["./a.json5", "./b.json5"] }  // deep-merged
}
```
- Nested includes up to 10 levels deep.
- Paths relative to the including file.

### Environment Variables
- Reads from parent process + `.env` (CWD) + `~/.openclaw/.env`.
- Inline env: `{ env: { OPENROUTER_API_KEY: "sk-or-..." } }`
- Substitution in config strings: `"${VAR_NAME}"` — only uppercase names.
- Shell env import: `{ env: { shellEnv: { enabled: true } } }`

### Key Config Sections (Minimal Example)
```json5
{
  agents: { defaults: { workspace: "~/.openclaw/workspace" } },
  channels: { telegram: { enabled: true, botToken: "123:abc" } },
  session: { dmScope: "per-channel-peer" },
}
```

---

## 3. Channels

### Supported Channels
WhatsApp, Telegram, Discord, Slack, Signal, iMessage, Google Chat, Mattermost, MS Teams, IRC, Matrix, LINE, Nostr, Feishu, Zalo, Nextcloud Talk, Synology Chat, Twitch, BlueBubbles.

### DM Policies (per channel)
| Policy | Behavior |
|--------|----------|
| `pairing` (default) | Unknown senders get pairing code; owner approves |
| `allowlist` | Only senders in `allowFrom` |
| `open` | Allow all (requires `allowFrom: ["*"]`) |
| `disabled` | Ignore all DMs |

### Group Policies
| Policy | Behavior |
|--------|----------|
| `allowlist` (default) | Only groups in allowlist |
| `open` | Bypass allowlists (mention-gating still applies) |
| `disabled` | Block all group messages |

### Mention Gating
Group messages default to **require mention**. Configure per agent:
```json5
{
  agents: { list: [{ id: "main", groupChat: { mentionPatterns: ["@openclaw"] } }] },
  channels: { whatsapp: { groups: { "*": { requireMention: true } } } }
}
```

### Channel Config Examples

**Telegram:**
```json5
{
  channels: {
    telegram: {
      enabled: true,
      botToken: "your-bot-token",
      dmPolicy: "pairing",
      allowFrom: ["tg:123456789"],
      groups: { "*": { requireMention: true } },
      streaming: "partial",  // off | partial | block | progress
    }
  }
}
```

**Discord:**
```json5
{
  channels: {
    discord: {
      enabled: true,
      token: "your-bot-token",
      dmPolicy: "pairing",
      guilds: { "1234567890": { requireMention: false, channels: { general: { allow: true } } } },
      threadBindings: { enabled: true, idleHours: 24 },
    }
  }
}
```

**WhatsApp:**
```json5
{
  channels: {
    whatsapp: {
      dmPolicy: "pairing",
      allowFrom: ["+15555550123"],
      groups: { "*": { requireMention: true } },
    }
  }
}
```

### Multi-Account
```json5
{
  channels: {
    telegram: {
      accounts: {
        default: { botToken: "123456:ABC..." },
        alerts: { botToken: "987654:XYZ..." },
      }
    }
  }
}
```
- Env tokens only apply to the **default** account.
- Use `bindings[].match.accountId` to route accounts to different agents.

### Routing (Agent Selection)
Deterministic order: peer match → guild → team → account → channel → default agent.

### Session Key Shapes
- Direct: `agent:<agentId>:<mainKey>` (default `agent:main:main`)
- Groups: `agent:<agentId>:<channel>:group:<id>`
- Channels: `agent:<agentId>:<channel>:channel:<id>`
- Telegram topics: `...group:<id>:topic:<threadId>`
- Threads: `...thread:<threadId>`

---

## 4. Automation

### Heartbeat vs Cron — When to Use Each

| Use Case | Use | Why |
|----------|-----|-----|
| Check inbox/calendar every 30 min | **Heartbeat** | Batches with other checks, context-aware |
| Daily report at 9am sharp | **Cron (isolated)** | Exact timing |
| Remind me in 20 minutes | **Cron (main, `--at`)** | One-shot precise |
| Weekly deep analysis | **Cron (isolated)** | Standalone, different model |

### Heartbeat
```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m",       // 0m disables
        target: "last",     // last | whatsapp | telegram | discord | none
        directPolicy: "allow",
        lightContext: false, // true = only HEARTBEAT.md from bootstrap
        activeHours: { start: "08:00", end: "22:00" },
      }
    }
  }
}
```
- Runs in the **main session** at regular intervals.
- Reply `HEARTBEAT_OK` if nothing needs attention.
- Create `HEARTBEAT.md` in workspace with a checklist.

### Cron Jobs
```bash
# One-shot reminder
openclaw cron add --name "Reminder" --at "20m" --session main \
  --system-event "Check the oven" --wake now --delete-after-run

# Recurring isolated job
openclaw cron add --name "Morning brief" --cron "0 7 * * *" \
  --tz "America/New_York" --session isolated \
  --message "Summarize inbox + calendar" --announce --channel telegram --to "123456"

# List / edit / run / view history
openclaw cron list
openclaw cron edit <jobId> --message "Updated prompt"
openclaw cron run <jobId>
openclaw cron runs --id <jobId> --limit 10
openclaw cron remove <jobId>
```

**Main vs Isolated:**
- `main`: system event queued, runs on next heartbeat with full context.
- `isolated`: dedicated turn in `cron:<jobId>`, fresh session, can override model/thinking, announces results.

**Delivery modes:** `announce` (channel delivery), `webhook` (HTTP POST), `none`.

**Retry:** One-shot retries transient errors 3× with backoff. Recurring uses exponential backoff (30s → 1m → 5m → 15m → 60m).

### Hooks (Webhooks)
```json5
{
  hooks: {
    enabled: true,
    token: "shared-secret",
    path: "/hooks",
    mappings: [
      { match: { path: "gmail" }, action: "agent", agentId: "main", deliver: true }
    ]
  }
}
```
- `POST /hooks/wake` → wake agent
- `POST /hooks/agent` → run agent with message
- `POST /hooks/<name>` → resolved via mappings
- Auth: `Authorization: Bearer <token>`

---

## 5. Tools

### Exec Tool
```bash
# Foreground
{ "tool": "exec", "command": "ls -la" }

# Background + poll
{"tool":"exec","command":"npm run build","yieldMs":1000}
{"tool":"process","action":"poll","sessionId":"<id>"}

# Send keys
{"tool":"process","action":"send-keys","sessionId":"<id>","keys":["C-c"]}
```

**Key params:** `command`, `workdir`, `env`, `yieldMs`, `background`, `timeout`, `pty`, `host` (sandbox|gateway|node), `security`, `elevated`.

**Host execution:** `host=gateway` or `host=node` — requires approvals from `~/.openclaw/exec-approvals.json`.

**Config:**
```json5
{
  tools: {
    exec: {
      backgroundMs: 10000,
      timeoutSec: 1800,
      pathPrepend: ["~/bin"],
      notifyOnExit: true,
    }
  }
}
```

### Web Search & Fetch
```json5
{
  tools: {
    web: {
      search: {
        enabled: true,
        provider: "brave",  // brave | gemini | grok | kimi | perplexity
        apiKey: "BRAVE_API_KEY",
        maxResults: 5,
        cacheTtlMinutes: 15,
      },
      fetch: {
        enabled: true,
        maxChars: 50000,
        timeoutSeconds: 30,
      }
    }
  }
}
```
- Providers: Brave (`BRAVE_API_KEY`), Gemini (`GEMINI_API_KEY`), Grok (`XAI_API_KEY`), Kimi (`KIMI_API_KEY`), Perplexity (`PERPLEXITY_API_KEY`).
- Auto-detects provider from available keys.
- `web_fetch` does HTTP GET + readability extraction (no JS execution).

### Browser Tool
```json5
{
  browser: {
    enabled: true,
    defaultProfile: "openclaw",
    profiles: {
      openclaw: { cdpPort: 18800 },
      user: { driver: "existing-session", attachOnly: true },
    }
  }
}
```
- `openclaw` profile: isolated, agent-only browser.
- `user` profile: attaches to your real Chrome session.
- `chrome-relay`: extension relay to system browser.
- Actions: open, click, type, snapshot, screenshot, PDF, evaluate.

### Sub-Agents
```json5
{
  agents: {
    defaults: {
      subagents: {
        model: "minimax/MiniMax-M2.5",  // cheaper model for sub-agents
        maxConcurrent: 8,
        runTimeoutSeconds: 900,
        maxSpawnDepth: 1,  // 2 for orchestrator pattern
        archiveAfterMinutes: 60,
      }
    }
  }
}
```

```bash
# Slash commands
/subagents list
/subagents spawn <agentId> "task description" --model opus
/subagents kill <id>
/subagents log <id> 50
```

**Tool:** `sessions_spawn` — returns `{ status: "accepted", runId, childSessionKey }` immediately.
- Session key: `agent:<agentId>:subagent:<uuid>`
- Results **announce** back to requester chat.
- Sub-agents get all tools except session tools (`sessions_list/history/send/spawn`).
- Sub-agent context only injects `AGENTS.md` + `TOOLS.md` (no SOUL.md, IDENTITY.md, etc.).

### TTS (Text-to-Speech)
```json5
{
  messages: {
    tts: {
      auto: "always",  // off | always | inbound | tagged
      provider: "elevenlabs",  // elevenlabs | openai | edge
      elevenlabs: { apiKey: "...", voiceId: "..." },
      openai: { apiKey: "...", voice: "alloy" },
      edge: { voice: "en-US-MichelleNeural" },  // no API key needed
    }
  }
}
```
- Edge TTS: free, no key, default fallback.
- `/tts off|always|inbound|tagged` per session.
- Telegram gets Opus voice note bubble.

### Skills (AgentSkills)
- Loaded from: bundled (npm install) → `~/.openclaw/skills` → `<workspace>/skills` (highest precedence).
- Each skill is a folder with `SKILL.md` (YAML frontmatter + instructions).
- Install from ClawHub: `clawhub install <skill-slug>`
- Config: `skills.entries.<name>.enabled`, `.apiKey`, `.env`.

### Tool Profiles & Groups
```json5
{
  tools: {
    profile: "coding",  // minimal | coding | messaging | full
    allow: ["browser"],
    deny: ["canvas"],
    byProvider: { "openai/gpt-5.2": { profile: "minimal" } }
  }
}
```

**Groups:** `group:fs` (read/write/edit), `group:runtime` (exec/process), `group:sessions`, `group:memory`, `group:web`, `group:ui` (browser/canvas), `group:automation` (cron/gateway), `group:messaging` (message).

### Loop Detection
```json5
{
  tools: {
    loopDetection: {
      enabled: true,
      warningThreshold: 10,
      criticalThreshold: 20,
      globalCircuitBreakerThreshold: 30,
    }
  }
}
```

---

## 6. Sessions

### How Sessions Work
- One session per direct chat per agent (controlled by `dmScope`).
- Group/channel chats get isolated sessions.
- Serialized per session key — no parallel runs within a session.
- Transcripts: `~/.openclaw/agents/<agentId>/sessions/<SessionId>.jsonl`
- Store: `~/.openclaw/agents/<agentId>/sessions/sessions.json`

### DM Scope
```json5
{
  session: {
    dmScope: "per-channel-peer",  // main | per-peer | per-channel-peer | per-account-channel-peer
    identityLinks: {
      alice: ["telegram:123456789", "discord:987654321012345678"]
    }
  }
}
```
- `main`: all DMs share one session (default, good for single-user).
- `per-channel-peer`: isolate by channel + sender (recommended for multi-user).
- `identityLinks`: same person across channels shares a session.

### Session Reset
```json5
{
  session: {
    reset: { mode: "daily", atHour: 4, idleMinutes: 120 },
    resetByType: {
      direct: { mode: "idle", idleMinutes: 240 },
      group: { mode: "idle", idleMinutes: 120 },
      thread: { mode: "daily", atHour: 4 },
    },
    resetTriggers: ["/new", "/reset"],
  }
}
```
- Daily reset defaults to 4:00 AM local time.
- Whichever expires first (daily or idle) forces a new session.
- `/new` or `/reset` starts fresh. `/new <model>` switches model.

### Compaction
- When session nears context window limit, older history is **summarized** and persisted.
- Auto-compaction triggers automatically; manual: `/compact` or `/compact <instructions>`.
- Pre-compaction memory flush: silent turn to store durable memories before compacting.
```json5
{
  agents: {
    defaults: {
      compaction: {
        mode: "safeguard",
        reserveTokensFloor: 24000,
        memoryFlush: { enabled: true, softThresholdTokens: 6000 },
        model: "openrouter/anthropic/claude-sonnet-4-5",  // optional compaction model
      }
    }
  }
}
```

### Session Pruning
- Trims old **tool results** from in-memory context (doesn't rewrite JSONL).
```json5
{
  agents: {
    defaults: {
      contextPruning: {
        mode: "cache-ttl",
        ttl: "1h",
        keepLastAssistants: 3,
      }
    }
  }
}
```

### Session Maintenance
```json5
{
  session: {
    maintenance: {
      mode: "enforce",  // warn | enforce
      pruneAfter: "30d",
      maxEntries: 500,
      rotateBytes: "10mb",
      maxDiskBytes: "500mb",
    }
  }
}
```
```bash
openclaw sessions cleanup --dry-run
openclaw sessions cleanup --enforce
openclaw sessions --active 120  # sessions active in last 120 min
```

### Send Policy
```json5
{
  session: {
    sendPolicy: {
      rules: [
        { action: "deny", match: { channel: "discord", chatType: "group" } }
      ],
      default: "allow"
    }
  }
}
```

### Inspecting Sessions
- `/status` — window usage + session settings
- `/context list` — injected files + sizes
- `/context detail` — detailed breakdown
- `/compact` — force compaction
- `/new` or `/reset` — fresh session
- `openclaw sessions --json` — dump all sessions
- `openclaw gateway call sessions.list --params '{}'` — from running gateway

---

## 7. Memory & Context

### Workspace Files (Auto-Injected)
These files are injected into the system prompt if present in the workspace:

| File | Purpose |
|------|---------|
| `AGENTS.md` | Workspace rules, conventions, session startup |
| `SOUL.md` | Personality, tone, identity |
| `TOOLS.md` | Environment notes, tool preferences |
| `IDENTITY.md` | Name, pronouns, avatar |
| `USER.md` | About the human |
| `HEARTBEAT.md` | Heartbeat checklist |
| `BOOTSTRAP.md` | First-run only, then deleted |

**Limits:** `bootstrapMaxChars: 20000` per file, `bootstrapTotalMaxChars: 150000` total.

### Memory Files
- `memory/YYYY-MM-DD.md` — daily logs (append-only). Read today + yesterday at session start.
- `MEMORY.md` — curated long-term memory. **Only load in main/private sessions** (never groups).
- Tools: `memory_search` (semantic), `memory_get` (targeted read).
- Vector index over memory files for semantic search (auto-configured).

### What Counts as Context
Everything the model sees: system prompt, conversation history, tool calls/results, attachments, compaction summaries, tool schemas.

### Context Commands
- `/status` — "how full is my window?"
- `/context list` — injected files + rough sizes
- `/context detail` — per-file, per-tool schema sizes, per-skill sizes
- `/usage tokens` — per-reply usage footer

### Pre-Compaction Memory Flush
Before auto-compaction, a silent turn reminds the model to write durable notes:
```json5
{
  agents: {
    defaults: {
      compaction: {
        memoryFlush: {
          enabled: true,
          softThresholdTokens: 6000,
          prompt: "Write any lasting notes to memory/YYYY-MM-DD.md; reply with  if nothing to store."
        }
      }
    }
  }
}
```

---

## 8. CLI Commands

### Gateway Management
```bash
openclaw gateway                    # run foreground
openclaw gateway start              # start service
openclaw gateway stop               # stop service
openclaw gateway restart            # restart service
openclaw gateway status             # service + RPC probe
openclaw gateway health             # health check
openclaw gateway probe              # debug everything
openclaw gateway install            # install as service
openclaw gateway uninstall          # remove service
openclaw gateway discover           # Bonjour scan
openclaw gateway call <method>      # low-level RPC
openclaw gateway call config.get --params '{}'
openclaw gateway call sessions.list --params '{}'
```

### Config
```bash
openclaw config get <path>          # e.g. agents.defaults.workspace
openclaw config set <path> <value>
openclaw config unset <path>
openclaw config validate
openclaw config file                # show path
```

### Sessions
```bash
openclaw sessions                   # list sessions
openclaw sessions --active 120      # active in last N minutes
openclaw sessions --json            # machine-readable
openclaw sessions --all-agents      # multi-agent
openclaw sessions cleanup --dry-run # preview maintenance
openclaw sessions cleanup --enforce # apply maintenance
```

### Cron
```bash
openclaw cron add --name "X" --cron "0 7 * * *" --session isolated --message "..." --announce
openclaw cron list
openclaw cron edit <jobId> --message "Updated"
openclaw cron run <jobId>           # force run (queued)
openclaw cron runs --id <jobId>     # run history
openclaw cron remove <jobId>
```

### Status & Diagnostics
```bash
openclaw status                     # channel + session diagnostics
openclaw status --all               # full overview
openclaw status --deep              # live probes
openclaw doctor                     # health checks + repairs
openclaw doctor --fix               # auto-repair
openclaw doctor --deep              # thorough check
openclaw health                     # quick health
openclaw logs                       # view logs
```

### Models
```bash
openclaw models list                # available models
openclaw models set <provider/model>  # set primary
openclaw models auth login --provider <name>
openclaw models auth paste-token --provider anthropic
```

### Other
```bash
openclaw onboard                    # full setup wizard
openclaw configure                  # config wizard
openclaw configure --section web    # web search setup
openclaw plugins install <plugin>
openclaw plugins enable <plugin>
openclaw plugins update
openclaw browser status             # browser control
openclaw browser open <url>
openclaw browser snapshot
openclaw system event --mode now --text "..."
openclaw update                     # update OpenClaw
openclaw security audit             # security check
openclaw tui                        # terminal UI
```

### In-Chat Slash Commands
- `/status` — session info + context usage
- `/context list|detail` — context breakdown
- `/compact [instructions]` — force compaction
- `/new [model]` — new session, optionally switch model
- `/reset` — reset session
- `/stop` — abort current run + queued followups + subagents
- `/model [provider/model]` — switch model
- `/think [level]` — thinking mode (off/low/medium/high)
- `/verbose [on|off]` — verbose mode
- `/tts [off|always|inbound|tagged|status]` — TTS control
- `/subagents list|kill|spawn|log|info` — subagent management
- `/elevated [on|off|ask]` — elevated exec mode
- `/send [on|off]` — session send policy override
- `/config show|set|unset` — config from chat
- `/exec host=gateway security=allowlist` — per-session exec defaults

---

## 9. Security

### Sandboxing
```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",  // off | non-main | all
        scope: "agent",    // session | agent | shared
        workspaceAccess: "none",  // none | ro | rw
        docker: {
          image: "openclaw-sandbox:bookworm-slim",
          network: "none",  // none | bridge (not "host")
          user: "1000:1000",
          capDrop: ["ALL"],
          memory: "1g",
          pidsLimit: 256,
        }
      }
    }
  }
}
```
- Tools run in Docker containers when enabled.
- `elevated` exec bypasses sandbox and runs on host.
- Build images: `scripts/sandbox-setup.sh`

### Exec Policies
```json5
{
  tools: {
    elevated: {
      enabled: true,
      allowFrom: { whatsapp: ["+15555550123"] }
    },
    exec: {
      security: "allowlist",  // deny | allowlist | full
      ask: "on-miss",         // off | on-miss | always
    }
  }
}
```
- `/elevated on|off|ask` per session.
- Host execution (`host=gateway/node`) uses `exec-approvals.json`.
- `safeBins`: stdin-only safe binaries (cat, grep, head, tail, etc.).
- `env.PATH` and `LD_*`/`DYLD_*` rejected for host execution.

### Secrets
- SecretRefs: `{ source: "env"|"file"|"exec", provider: "...", id: "..." }`
- Resolved eagerly at startup into in-memory snapshot.
- Startup fails fast if active SecretRef can't be resolved.
- Inactive surfaces (disabled channels) don't block startup.
```json5
{
  models: {
    providers: {
      openai: { apiKey: { source: "env", provider: "default", id: "OPENAI_API_KEY" } }
    }
  }
}
```

### Gateway Auth
```json5
{
  gateway: {
    auth: {
      mode: "token",  // none | token | password | trusted-proxy
      token: "your-token",
      allowTailscale: true,
      rateLimit: { maxAttempts: 10, windowMs: 60000, lockoutMs: 300000 }
    }
  }
}
```
- Non-loopback binds require auth.
- `OPENCLAW_GATEWAY_TOKEN` env var overrides config token.

### Security Audit
```bash
openclaw security audit
openclaw doctor --fix
```

---

## 10. Providers

### Model Format
`provider/model` — e.g., `anthropic/claude-opus-4-6`, `openai/gpt-5.4`, `google/gemini-3.1-pro-preview`.

### Built-In Providers
| Provider | Env Var | Auth |
|----------|---------|------|
| OpenAI | `OPENAI_API_KEY` | API key |
| Anthropic | `ANTHROPIC_API_KEY` | API key or OAuth |
| Google Gemini | `GEMINI_API_KEY` | API key |
| OpenRouter | `OPENROUTER_API_KEY` | API key |
| Groq | `GROQ_API_KEY` | API key |
| Mistral | `MISTRAL_API_KEY` | API key |
| xAI | `XAI_API_KEY` | API key |
| Ollama | None (local) | — |
| vLLM | Optional | — |
| KiloCode | `KILOCODE_API_KEY` | API key |

### Configuration
```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-sonnet-4-5",
        fallbacks: ["openai/gpt-5.2"]
      },
      models: {
        "anthropic/claude-sonnet-4-5": { alias: "Sonnet" },
        "openai/gpt-5.2": { alias: "GPT" },
      },
      contextTokens: 200000,
      maxConcurrent: 3,
    }
  }
}
```

### Custom Providers
```json5
{
  models: {
    mode: "merge",  // merge | replace
    providers: {
      "my-proxy": {
        baseUrl: "http://localhost:4000/v1",
        apiKey: "KEY",
        api: "openai-completions",  // openai-completions | anthropic-messages | google-generative-ai
        models: [{ id: "llama-3.1-8b", contextWindow: 128000, maxTokens: 32000 }]
      }
    }
  }
}
```

### Failover
1. **Auth profile rotation** within provider (OAuth before API keys, round-robin).
2. **Model fallback** to next model in `fallbacks` list.
3. Session stickiness: profile pinned per session for cache warmth.
4. Cooldowns: exponential backoff (1m → 5m → 25m → 1h cap).
5. Billing disables: 5h → doubles → 24h cap.

### API Key Rotation
- `OPENAI_API_KEYS` (comma-separated), `OPENAI_API_KEY_1`, `OPENAI_API_KEY_2`, `OPENCLAW_LIVE_OPENAI_KEY`.
- Retries with next key only on rate-limit (429).

### Built-In Aliases
| Alias | Model |
|-------|-------|
| `opus` | `anthropic/claude-opus-4-6` |
| `sonnet` | `anthropic/claude-sonnet-4-6` |
| `gpt` | `openai/gpt-5.4` |
| `gemini` | `google/gemini-3.1-pro-preview` |

---

## 11. Troubleshooting

### Gateway Won't Start
- Check config validation: `openclaw doctor`
- Run `openclaw doctor --fix` to repair
- Unknown keys in config cause boot failure — doctor can strip them
- Check `OPENCLAW_SKIP_CRON` / `OPENCLAW_SKIP_CANVAS_HOST` env vars

### Unauthorized Errors
- Check `OPENCLAW_GATEWAY_TOKEN` env var (overrides config)
- On macOS: `launchctl getenv OPENCLAW_GATEWAY_TOKEN` and `launchctl unsetenv ...`
- If both `gateway.auth.token` and `gateway.auth.password` set, `gateway.auth.mode` must be explicit

### WhatsApp Issues
- Relink if credentials expired (check `/status` for last refresh)
- `openclaw doctor --deep` probes WhatsApp Web connectivity

### Cron Not Running
- Check `cron.enabled: true` and no `OPENCLAW_SKIP_CRON=1`
- Gateway must run continuously (cron runs inside gateway process)
- Check timezone: `--tz` vs host timezone

### High Token Usage
- Reduce `heartbeat.every` or set `heartbeat.target: "none"`
- Keep `HEARTBEAT.md` small
- Use `agents.defaults.subagents.model` for cheaper sub-agent model
- Check `/context detail` for bloated tool schemas or skills
- Enable context pruning: `contextPruning.mode: "cache-ttl"`
- Lower `bootstrapMaxChars` or `bootstrapTotalMaxChars`

### Sub-Agent Announce Lost
- Pending announces lost if gateway restarts
- Check `/subagents list` for stuck runs
- `/subagents kill <id>` to stop

### Memory Search Not Working
- Check embedding provider configured: `agents.defaults.memorySearch.provider`
- Auto-selects: local → openai → gemini → voyage → mistral
- `openclaw doctor` checks memory-search readiness

### Config Validation Errors
- `openclaw config validate --json` for details
- `openclaw doctor --fix` strips unknown keys (backs up to `.bak`)

### Docker Sandbox Issues
- `openclaw doctor` warns if Docker unavailable but sandbox mode is on
- Build images: `scripts/sandbox-setup.sh`
- Network `"none"` is default — set to `"bridge"` for outbound access

---

## 12. Skills

### How Skills Work
- Each skill is a folder with `SKILL.md` (YAML frontmatter + markdown instructions).
- Loaded from 3 locations (highest precedence wins):
  1. `<workspace>/skills` (per-agent)
  2. `~/.openclaw/skills` (shared across agents)
  3. Bundled (shipped with npm install)
- Extra dirs: `skills.load.extraDirs` (lowest precedence).
- System prompt gets a compact skills list (name + description + location).
- Skill instructions loaded on-demand when model reads `SKILL.md`.

### SKILL.md Format
```markdown
---
name: my-skill
description: What this skill does
metadata: {"openclaw": {"requires": {"bins": ["ffmpeg"], "env": ["API_KEY"]}, "primaryEnv": "API_KEY"}}
---
# Instructions
Use {baseDir} to reference the skill folder path.
```

### Gating (Load-Time Filters)
- `requires.bins` — must exist on PATH
- `requires.env` — env var must exist
- `requires.config` — openclaw.json path must be truthy
- `os` — limit to platforms (darwin, linux, win32)
- `always: true` — skip other gates

### Config Overrides
```json5
{
  skills: {
    allowBundled: ["gemini", "peekaboo"],
    entries: {
      "my-skill": {
        enabled: true,
        apiKey: "KEY",  // or { source: "env", ... }
        env: { API_KEY: "value" }
      },
      "unused-skill": { enabled: false }
    }
  }
}
```

### ClawHub (Public Registry)
```bash
npm i -g clawhub
clawhub search "calendar"
clawhub install <skill-slug>
clawhub update --all
clawhub sync --all
clawhub publish  # publish your own
```
Site: [clawhub.com](https://clawhub.com)

### Creating Skills
1. Create folder in `<workspace>/skills/<skill-name>/`
2. Write `SKILL.md` with frontmatter (`name`, `description`, optional `metadata`)
3. Add supporting files if needed
4. Skills auto-reload via file watcher (hot reload mid-session)

### Token Impact
- Base overhead: 195 chars (when ≥1 skill).
- Per skill: ~97 chars + name + description + location.
- Rough: ~24 tokens per skill + field lengths.

### Plugins That Ship Skills
Plugins can include `skills` directories in `openclaw.plugin.json`. Plugin skills load when enabled and participate in normal precedence.

---

## Quick Reference Card

| What | Command/Config |
|------|---------------|
| Start gateway | `openclaw gateway` |
| Check status | `openclaw status` |
| Doctor | `openclaw doctor --fix` |
| Config get/set | `openclaw config get/set <path>` |
| List sessions | `openclaw sessions` |
| Session cleanup | `openclaw sessions cleanup --dry-run` |
| Add cron job | `openclaw cron add --name "X" --cron "..." --session isolated --message "..."` |
| List cron | `openclaw cron list` |
| Install skill | `clawhub install <slug>` |
| Switch model | `/model provider/model` |
| Force compact | `/compact` |
| New session | `/new` |
| Abort run | `/stop` |
| Context check | `/context detail` |
| Security audit | `openclaw security audit` |
| Update | `openclaw update` |

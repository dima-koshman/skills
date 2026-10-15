---
type: Tool
title: Claude Code
description: Anthropic's coding agent — Claude in a loop with file, shell, and code tools, available as
  CLI, IDE extension, and SDK.
resource: https://code.claude.com/docs
tags:
- ai-engineering
- agents
parent: /ai-engineering/agents.md
related:
- /ai-engineering/agents/agent.md
- /ai-engineering/context/prompt-caching.md
- /ai-engineering/harness.md
implements: /ai-engineering/agents/agent.md
provider: /ai-engineering/providers/claude.md
execution_surface:
- CLI
- IDE extension
- SDK
sources:
- id: ref-1
  resource: https://code.claude.com/docs
  title: code.claude.com
- id: ref-2
  resource: https://docs.langchain.com/langsmith/trace-claude-code
  title: plugin
- id: ref-3
  resource: https://claude.com/blog/lessons-from-building-claude-code-prompt-caching-is-everything
  title: Lessons from building Claude Code - Prompt caching is everything
generated:
  by: antigravity/gemini-3-8-flash
  at: '2026-10-15T17:37:00+04:00'
---

Reference: <https://code.claude.com/docs>

Claude Code is Anthropic's coding [agent](/ai-engineering/agents/agent.md): a terminal-native
[harness](/ai-engineering/harness.md) running Claude.

## Harness architecture and prompt caching

Claude Code's runtime is engineered entirely around [prompt caching](/ai-engineering/context/prompt-caching.md) to minimize latency and token cost during multi-turn coding sessions:

- **Strict prefix ordering**: Base system instructions and tools are positioned first (globally cached), followed by project guidelines like `CLAUDE.md` and memory (cached per project), session environment context (cached per session), and finally append-only conversation messages.
- **Invariant tool definitions**: The harness never adds or removes tools mid-session. Modes such as Plan Mode are modeled as tools (`EnterPlanMode`, `ExitPlanMode`) that adjust instructions via conversation messages rather than modifying tool definitions. MCP tools use deferred loading (`defer_loading: true`) with tool search so schemas are discovered on demand without breaking prefix stability.
- **Message-based updates**: Dynamic data and context refreshes are injected into the message flow (e.g., via `<system-reminder>` blocks) rather than mutating the system prompt.
- **Cache-safe compaction**: When approaching context limits, compaction forks a call using the exact same system prompt, tools, and message prefix with a summarization prompt at the end, reusing the cached conversation history at cache-hit rates.
- **Operational observability**: Cache hit ratio is treated as a critical production health metric, with automated alerting and incident escalation when hit rates drop.

Claude Code usage can also be traced via LangSmith using this [plugin](https://docs.langchain.com/langsmith/trace-claude-code).

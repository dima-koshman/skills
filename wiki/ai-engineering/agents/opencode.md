---
type: Tool
title: OpenCode
description: Open-source, terminal-native, model-agnostic coding agent — a vendor-neutral alternative
  to Claude Code.
resource: https://opencode.ai
tags:
- ai-engineering
- agents
parent: /ai-engineering/agents.md
related:
- /ai-engineering/agents/agent.md
- /ai-engineering/agents/claude-code.md
implements: /ai-engineering/agents/agent.md
execution_surface:
- local terminal
provider_model: model-agnostic
sources:
- id: ref-1
  resource: https://opencode.ai
  title: opencode.ai
- id: ref-2
  resource: https://docs.langchain.com/langsmith/trace-with-opencode
  title: plugin
generated:
  by: codex/gpt-6
  at: '2026-10-15T15:23:06+04:00'
---

Reference: <https://opencode.ai>

OpenCode is an open-source, terminal-native coding [agent](/ai-engineering/agents/agent.md) (by
the SST team) that is model-agnostic — it connects to many model providers rather
than a single vendor, runs locally, and stores its sessions on disk. A
vendor-neutral counterpart to [Claude Code](/ai-engineering/agents/claude-code.md). Can be used with Codex or Antigravity subscriptions, but not with Claude.

OpenCode usage can be traced via LangSmith using this [plugin](https://docs.langchain.com/langsmith/trace-with-opencode).

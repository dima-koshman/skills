---
type: Knowledge Area
title: Agent Harness
description: 'The runtime scaffolding around the model loop: tool dispatch, state, sandboxing, and loop
  control.'
tags:
- ai-engineering
parent: /ai-engineering.md
related:
- /ai-engineering/agents/agent.md
- /ai-engineering/harness/workflows.md
- /ai-engineering/agents/deep-agents.md
generated:
  by: codex/gpt-6
  at: '2026-10-15T15:23:06+04:00'
topics:
- /ai-engineering/harness/frontend-tools.md
- /ai-engineering/harness/provider-tools.md
- /ai-engineering/harness/subagents.md
- /ai-engineering/harness/tools.md
- /ai-engineering/harness/workflows.md
---

The harness is the runtime that drives the agent loop around the model: it parses each model response, dispatches the tool calls, feeds results back, manages context and memory, enforces sandboxing and limits (retries, max steps, budgets), and decides when to stop. It is the concrete implementation of an [agent architecture](/ai-engineering/agents/agent.md) — the model and the tools plug into it, and it is what runs a [workflow](/ai-engineering/harness/workflows.md) or a full agent loop. Frameworks like [deepagents](/ai-engineering/agents/deep-agents.md) ship a ready-made harness.

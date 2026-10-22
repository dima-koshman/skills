---
type: Concept
title: Agent
description: The loop, planning, subagents, tools, and memory that turn an LLM into a task-completing
  agent.
tags:
- ai-engineering
- agents
parent: /ai-engineering/agents.md
related:
- /ai-engineering/harness/tools.md
- /ai-engineering/harness/programmatic-tool-calling.md
- /ai-engineering/context/memory.md
- /ai-engineering/harness/subagents.md
- /ai-engineering/harness.md
- /ai-engineering/agents/deep-agents.md
sources:
- id: ref-1
  resource: https://docs.langchain.com/oss/python/langchain/agents
  title: docs.langchain.com
generated:
  by: codex/gpt-6
  at: '2026-10-15T15:23:06+04:00'
---

Reference: <https://docs.langchain.com/oss/python/langchain/agents>

Agent is not a well-defined term, but in most cases it means an **LLM in a loop
with tools**: the model picks the next action, calls a [tool](/ai-engineering/harness/tools.md),
observes the result, and repeats until the task is done. What distinguishes an
agent from a fixed pipeline is that the *model* — not hard-coded logic — directs
the control flow; when the flow can be fixed instead, a
fixed workflow is the leaner option. The recurring ingredients
are the loop, planning (decomposing a goal into steps), tool use,
[memory](/ai-engineering/context/memory.md) (carrying context across steps), and often
[subagents](/ai-engineering/harness/subagents.md) for delegating focused subtasks. The loop is
driven by an [agent harness](/ai-engineering/harness.md); frameworks like
[deepagents](/ai-engineering/agents/deep-agents.md) package these patterns.

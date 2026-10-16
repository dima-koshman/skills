---
type: Tool
title: Deep Agents
description: Opinionated LangChain package for high level agent patterns.
resource: https://docs.langchain.com/oss/python/deepagents/overview
tags:
- ai-engineering
- agents
parent: /ai-engineering/agents.md
related:
- /ai-engineering/agents/agent.md
- /ai-engineering/harness/subagents.md
- /ai-engineering/context/memory.md
- /ai-engineering/harness/workflows.md
- /ai-engineering/harness.md
- /ai-engineering/models/scaledown.md
implements: /ai-engineering/agents/agent.md
runtime_framework: LangGraph
sources:
- id: ref-1
  resource: https://docs.langchain.com/oss/python/deepagents/overview
  title: docs.langchain.com
- id: langchain-scaledown
  resource: https://www.langchain.com/blog/building-long-running-agents-with-scaledown-and-deep-agents
  title: Building long-running agents with ScaleDown and Deep Agents
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-10-16T14:00:00+04:00'
---

Reference: <https://docs.langchain.com/oss/python/deepagents/overview>

Deep Agents is the LangChain library that packages production [agent](/ai-engineering/agents/agent.md) patterns — planning, [subagents](/ai-engineering/harness/subagents.md), durable [memory](/ai-engineering/context/memory.md), human-in-the-loop, and [workflows](/ai-engineering/harness/workflows.md) — on top of LangGraph, which serves as its [harness](/ai-engineering/harness.md).

Middleware can hand Deep Agents' frequent context chores to small models. For
example, [ScaleDown](/ai-engineering/models/scaledown.md) replaces the built-in
history summarization, compresses tool output, extracts fields into state, and
acts as a classifier circuit breaker for looping runs.[^langchain-scaledown]

[^langchain-scaledown]: LangChain blog, 2026-10-13

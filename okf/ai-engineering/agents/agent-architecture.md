---
type: Architecture Pattern
title: Agent Architecture
description: The loop, planning, subagents, tools, and memory that turn an LLM into a task-completing agent.
tags: [agents, architecture, deepagents, platform]
timestamp: 2026-07-04T00:00:00Z
---

An agent is an LLM in a loop with tools, working memory, and a stopping
condition. Beyond the toy loop, production agents add **planning** (explicit
task decomposition), **subagents** (isolated context for delegated work),
**durable state/memory**, and **human-in-the-loop** checkpoints. deepagents
packages these patterns vendor-neutrally on top of LangGraph.

## In an enterprise platform

This is the shape of both your work platform and your personal
[agents](https://github.com/dima-koshman/agents) project. The engineering
substance is not the model call — it is context management, tool orchestration,
and controlling the loop. Get the architecture right and the choice of model
becomes swappable.

## Design considerations

- **Context engineering over prompt cleverness** — what enters the window each
  turn (tool results, memory, retrieved knowledge such as an
  [OKF](/context/okf.md) bundle) determines behavior more than
  the system prompt.
- **Subagents for isolation** — spin up fresh context for a bounded task; return
  only the conclusion. Prevents context rot on long runs.
- **Durable execution** — checkpoint state (deepagents/LangGraph on Postgres) so
  long tasks survive restarts and support resume/approval.
- **Tools via [MCP](/context/mcp.md)** — get capabilities from the gateway, not
  hardcoded, so the agent and the platform evolve independently.
- **Every step is untrusted** — tool results can carry
  [prompt injection](/security/threats/asi01-agent-goal-hijack.md); wrap the loop in
  [guardrails](/security/controls/guardrails.md) and trace it with
  [observability](/observability/observability.md).

# Citations

[1] [deepagents overview — LangChain](https://docs.langchain.com/oss/python/deepagents/overview)
[2] [Cognition blog](https://cognition.com/blog)
[3] [LangChain blog](https://www.langchain.com/blog)
[4] [The Agentic Operating Model — LangChain](https://www.langchain.com/resources/the-agentic-operating-model)

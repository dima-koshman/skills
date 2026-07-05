---
type: Architecture Pattern
title: Agent Harness
description: "The runtime scaffolding around the model loop: tool dispatch, state, sandboxing, and loop control."
tags: [agents, harness, runtime, architecture]
timestamp: 2026-07-05T00:00:00Z
---

The harness is the runtime that drives the agent loop around the model: it parses each model response, dispatches the tool calls, feeds results back, manages context and memory, enforces sandboxing and limits (retries, max steps, budgets), and decides when to stop. It is the concrete implementation of an [agent architecture](/agents/agent.md) — the model and the tools plug into it, and it is what runs a [workflow](/agents/workflows.md) or a full agent loop. Frameworks like [deepagents](/agents/deepagents.md) ship a ready-made harness.

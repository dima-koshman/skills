---
type: Architecture Pattern
title: Agent Architecture
description: The loop, planning, subagents, tools, and memory that turn an LLM into a task-completing agent.
tags: [agents, architecture, deepagents, platform]
timestamp: 2026-07-05T00:00:00Z
---

Agent is not a well-defined term, but in most cases it means an **LLM in a loop
with tools**: the model picks the next action, calls a [tool](/tools/tools.md),
observes the result, and repeats until the task is done. What distinguishes an
agent from a fixed pipeline is that the *model* — not hard-coded logic — directs
the control flow; when the flow can be fixed instead, a
[workflow](/agents/workflows.md) is the leaner option. The recurring ingredients
are the loop, planning (decomposing a goal into steps), tool use,
[memory](/agents/memory.md) (carrying context across steps), and often
[subagents](/agents/subagents.md) for delegating focused subtasks. The loop is
driven by an [agent harness](/agents/harness.md); frameworks like
[deepagents](/agents/deepagents.md) package these patterns.

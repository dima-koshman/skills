---
type: Overview
title: Agent
description: The loop, planning, subagents, tools, and memory that turn an LLM into a task-completing agent.
resource: https://docs.langchain.com/oss/python/langchain/agents
---

Agent is not a well-defined term, but in most cases it means an **LLM in a loop
with tools**: the model picks the next action, calls a [tool](/harness/tools.md),
observes the result, and repeats until the task is done. What distinguishes an
agent from a fixed pipeline is that the *model* — not hard-coded logic — directs
the control flow; when the flow can be fixed instead, a
[workflow](/harness/workflows.md) is the leaner option. The recurring ingredients
are the loop, planning (decomposing a goal into steps), tool use,
[memory](/context/memory.md) (carrying context across steps), and often
[subagents](/harness/subagents.md) for delegating focused subtasks. The loop is
driven by an [agent harness](/harness/harness.md); frameworks like
[deepagents](/agents/deep-agents.md) package these patterns.

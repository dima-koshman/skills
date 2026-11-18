---
type: Knowledge Area
title: Multi-Agent Systems
description: "How agents work with other agents: subagents under a parent, code-driven subagents, peers without a parent, and the A2A protocol."
tags:
- ai-engineering
- multi-agent
parent: /ai-engineering.md
topics:
- /ai-engineering/multi-agent/a2a.md
- /ai-engineering/multi-agent/dynamic-subagents.md
- /ai-engineering/multi-agent/peer-agents.md
- /ai-engineering/multi-agent/subagents.md
status: draft
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-18T12:00:00+04:00'
---

Agents working with other agents. [Subagents](/ai-engineering/multi-agent/subagents.md) run under a parent; [peer agents](/ai-engineering/multi-agent/peer-agents.md) coordinate without one. The definition of an [agent](/ai-engineering.md#agent) is in the AI Engineering glossary.

## Topics

- [Agent2Agent](/ai-engineering/multi-agent/a2a.md) — A protocol designed by Google enabling communication and interoperability between opaque agentic applications.
- [Dynamic Subagents](/ai-engineering/multi-agent/dynamic-subagents.md) — An agent writes code that dispatches subagents, branches on their results, and controls what returns to the coordinating model.
- [Peer Agents](/ai-engineering/multi-agent/peer-agents.md) — Independently governed agents that own goals and coordinate as peers rather than through a permanent parent.
- [Subagents](/ai-engineering/multi-agent/subagents.md) — Delegating focused subtasks to separate agent instances, and orchestrating multiple agents together.

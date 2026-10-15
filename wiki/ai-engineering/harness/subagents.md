---
type: Concept
title: Subagents
description: Delegating focused subtasks to separate agent instances, and orchestrating multiple agents
  together.
tags:
- ai-engineering
- harness
parent: /ai-engineering/harness.md
related:
- /ai-engineering/agents/peer-agents.md
- /ai-engineering/security/risks/insecure-inter-agent-communication.md
sources:
- id: ref-1
  resource: https://docs.langchain.com/oss/python/deepagents/subagents
  title: docs.langchain.com
generated:
  by: codex/gpt-6
  at: '2026-10-15T15:23:06+04:00'
---

Reference: <https://docs.langchain.com/oss/python/deepagents/subagents>

Subagents are separate agent instances spawned to handle a focused subtask with
their own context, keeping the parent's context clean; multi-agent systems
coordinate several such agents, often under a supervisor. Unlike
[peer agents](/ai-engineering/agents/peer-agents.md), subagents receive their task and authority
from a parent, even though the underlying invocation machinery may be the same.
The pattern adds a new attack surface — see
[insecure inter-agent communication](/ai-engineering/security/risks/insecure-inter-agent-communication.md).

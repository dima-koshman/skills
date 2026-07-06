---
type: Technique
title: Subagents
description: Delegating focused subtasks to separate agent instances, and orchestrating multiple agents together.
resource: https://docs.langchain.com/oss/python/deepagents/subagents
---

Subagents are separate agent instances spawned to handle a focused subtask with
their own context, keeping the parent's context clean; multi-agent systems
coordinate several such agents, often under a supervisor. Unlike
[peer agents](/agents/peer-agents.md), subagents receive their task and authority
from a parent, even though the underlying invocation machinery may be the same.
The pattern adds a new attack surface — see
[insecure inter-agent communication](/security/risks/insecure-inter-agent-communication.md).

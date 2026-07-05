---
type: Technique
title: Workflows
description: Workflows let an agent orchestrate its tool calls programmatically — scripted tool use for lower token cost and long-running tasks.
tags: [agents, workflows, code-mode, tools, technique]
timestamp: 2026-07-05T00:00:00Z
---

Workflows give an [agent](/agents/agent.md) a way to make tool calls in a scripted way, allowing for reduced token usage and orchestration of long running tasks. They become especially powerful with access to a [subagent](/agents/subagents.md)-spawning tool. Because they run model-written code inside the [harness](/agents/harness.md), they raise [unexpected code execution](/security/threats/unexpected-code-execution.md) risk.

Examples of workflow implementations:

- [Claude Workflows](https://code.claude.com/docs/en/workflows)
- [LangChain Interpreters](https://docs.langchain.com/oss/python/deepagents/interpreters)

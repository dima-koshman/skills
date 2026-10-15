---
type: Concept
title: Workflows
description: Workflows let an agent orchestrate its tool calls programmatically — scripted tool use for
  lower token cost and long-running tasks.
tags:
- ai-engineering
- harness
parent: /ai-engineering/harness.md
related:
- /ai-engineering/agents/agent.md
- /ai-engineering/harness/subagents.md
- /ai-engineering/security/risks/unexpected-code-execution.md
sources:
- id: ref-1
  resource: https://code.claude.com/docs/en/workflows
  title: Claude Workflows
- id: ref-2
  resource: https://docs.langchain.com/oss/python/deepagents/dynamic-subagents
  title: LangChain Dynamic Subagents
generated:
  by: codex/gpt-6
  at: '2026-10-15T15:23:06+04:00'
---

Workflows give an [agent](/ai-engineering/agents/agent.md) a way to make tool calls in a scripted way, allowing for reduced token usage and orchestration of long running tasks. They become especially powerful with access to a [subagent](/ai-engineering/harness/subagents.md)-spawning tool. Because they run model-written code inside the [harness](/ai-engineering/harness.md), they raise [unexpected code execution](/ai-engineering/security/risks/unexpected-code-execution.md) risk.

Examples of workflow implementations:

- [Claude Workflows](https://code.claude.com/docs/en/workflows)
- [LangChain Dynamic Subagents](https://docs.langchain.com/oss/python/deepagents/dynamic-subagents)

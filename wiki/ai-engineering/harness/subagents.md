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
- /ai-engineering/context/prompt-caching.md
- /ai-engineering/harness/programmatic-tool-calling.md
- /ai-engineering/harness/dynamic-subagents.md
- /ai-engineering/security/risks/insecure-inter-agent-communication.md
sources:
- id: ref-1
  resource: https://docs.langchain.com/oss/python/deepagents/subagents
  title: docs.langchain.com
- id: ref-2
  resource: https://claude.com/blog/lessons-from-building-claude-code-prompt-caching-is-everything
  title: claude.com/blog
- id: claude-workflows
  resource: https://code.claude.com/docs/en/workflows
  title: Claude Code dynamic workflows
- id: codex-subagents
  resource: https://learn.chatgpt.com/docs/agent-configuration/subagents
  title: Subagents
generated:
  by: codex/gpt-6
  at: '2026-10-22T13:46:52+04:00'
---

Reference: <https://docs.langchain.com/oss/python/deepagents/subagents>

Subagents are separate agent instances spawned to handle a focused subtask with
their own context, keeping the parent's context clean; multi-agent systems
coordinate several such agents, often under a supervisor. Unlike
[peer agents](/ai-engineering/agents/peer-agents.md), subagents receive their task and authority
from a parent, even though the underlying invocation machinery may be the same.
The pattern adds a new attack surface — see
[insecure inter-agent communication](/ai-engineering/security/risks/insecure-inter-agent-communication.md).

## When subagents make sense

Subagents are not a universal organizational pattern; they introduce significant coordination and token overhead. Spawning a subagent makes sense only when:

1. **A specialized, compact context and goal can be split cleanly** from the main process. If the subagent requires most of the parent's conversation and environment state to act, the separation provides little value.
2. **Tool isolation is needed**: Restricting tools (e.g., read-only codebase exploration) to prevent catastrophic actions in the main loop.
3. **Context pollution prevention**: Isolating noisy intermediate reasoning or large raw command outputs that would otherwise bloat the parent context.

## Parallelization and cost

Running subagents in parallel can improve wall-clock throughput, but each worker
still performs model and tool work. Cost depends on total worker effort, repeated
context, models, caching, and coordination; concurrency alone does not determine
total tokens. Codex documents greater token use than comparable single-agent
runs.[^codex-subagents]

[Dynamic Subagents](/ai-engineering/harness/dynamic-subagents.md), also called
**programmatic subagent orchestration**, is the use of
[PTC](/ai-engineering/harness/programmatic-tool-calling.md) to control these workers
from code. It can reduce coordinator overhead for the same set of workers while
still costing more overall than a single-agent solution. Separate worker contexts
already exist with ordinary delegation; scripting additionally keeps dispatch
logic and intermediate worker results outside the parent's model context.[^claude-workflows]

## Prompt caching and the context handoff trap

The interaction between [prompt caching](/ai-engineering/context/prompt-caching.md) and agent contexts introduces an unintuitive cost dynamic:

- A warm parent context can make another turn cheaper than initializing a worker.
  Compare billed usage, not only model list prices or raw context lengths.
- A new thread is **not necessarily a cold cache**. Claude Code workflows explicitly
  allow matching sibling agents to reuse the tools/system-prompt prefix; the
  runtime can stagger starts to enable this reuse.[^claude-workflows]
- Cache reuse depends on matching prefixes and provider/runtime cache boundaries.
  Claude's workflow documentation requires matching model and agent configuration
  for this sibling reuse, so changing models is not a cache-preserving handoff.[^claude-workflows]

[^claude-workflows]: [Claude Code dynamic workflows](https://code.claude.com/docs/en/workflows), especially prompt caching and cost.
[^codex-subagents]: [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents), official OpenAI documentation.

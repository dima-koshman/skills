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
- /ai-engineering/security/risks/insecure-inter-agent-communication.md
sources:
- id: ref-1
  resource: https://docs.langchain.com/oss/python/deepagents/subagents
  title: docs.langchain.com
- id: ref-2
  resource: https://claude.com/blog/lessons-from-building-claude-code-prompt-caching-is-everything
  title: claude.com/blog
generated:
  by: antigravity/gemini-3-8-flash
  at: '2026-10-15T17:36:00+04:00'
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

Running subagents in parallel is powerful for wall-clock throughput — such as executing multiple test runs, surveying different sections of a codebase, or testing independent hypotheses concurrently. However, parallelization is inherently expensive: token consumption multiplies linearly with each concurrently active subagent stream, rapidly burning through rate limits and budget.

## Prompt caching and the context handoff trap

The interaction between [prompt caching](/ai-engineering/context/prompt-caching.md) and agent contexts introduces an unintuitive cost dynamic:

- In a long-running session, the parent agent's large context (often 50k–100k+ tokens) is warm in the model's cache. Subsequent turns in the main process hit this cached prefix, paying heavily discounted cache-read rates (~0.1× base input cost).
- Spawning a subagent creates a new conversation thread with a **cold prompt cache**. Even if the subagent operates with a smaller context, initializing that context incurs full uncached input or cache-write fees.
- If a task attempts to save money by routing work to a subagent on a smaller model (e.g., Claude Haiku instead of Opus), prompt caches do not transfer across models. The subagent must rebuild the cache on the new model.
- Consequently, handing off work to a smaller subagent can be **more expensive** than simply continuing with the larger, but already-cached parent context, unless the subagent's handoff prompt is extremely compact or the subtask runs long enough to amortize the cold cache startup.

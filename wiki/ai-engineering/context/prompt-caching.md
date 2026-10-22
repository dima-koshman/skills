---
type: Concept
title: Prompt Caching
description: Reusing cached prefix tokens across LLM requests to minimize latency and token costs, and how to design agent harnesses around cache preservation.
tags:
- ai-engineering
- context
parent: /ai-engineering/context.md
related:
- /ai-engineering/context/context-engineering.md
- /ai-engineering/harness/subagents.md
- /ai-engineering/agents/claude-code.md
- /ai-engineering/enterprise/llm-gateway.md
- /ai-engineering/observability/langfuse.md
- /ai-engineering/providers/claude.md
- /ai-engineering/providers/gpt.md
- /ai-engineering/compute/serving/prefix-caching.md
- /ai-engineering/compute/serving/kv-cache.md
sources:
- id: ref-1
  resource: https://claude.com/blog/lessons-from-building-claude-code-prompt-caching-is-everything
  title: "Lessons from building Claude Code: Prompt caching is everything"
generated:
  by: codex/gpt-6
  at: '2026-10-22T13:46:52+04:00'
---

Reference: <https://claude.com/blog/lessons-from-building-claude-code-prompt-caching-is-everything>

For the serving-side execution mechanism, see
[Prefix Caching](/ai-engineering/compute/serving/prefix-caching.md) and
[KV Cache](/ai-engineering/compute/serving/kv-cache.md). This page focuses on
prompt layout and agent-harness economics.

Prompt caching allows LLM providers to reuse KV-cache computation from previous requests whenever an incoming prompt matches a previously seen token prefix. Because cached prompt tokens are dramatically cheaper (e.g., 90% discount on [Claude](/ai-engineering/providers/claude.md) and [GPT](/ai-engineering/providers/gpt.md)) and significantly reduce time-to-first-token (TTFT), prompt caching is the primary technical and economic foundation for long-running agent loops.

Designing an agent harness around prompt caching requires structuring all prompt assembly and execution workflows to preserve prefix stability.

## Prefix matching and prompt layout

Prompt caches operate via **prefix matching**: the provider caches tokens strictly from the start of the prompt up to a designated cache breakpoint. Any mutation anywhere in the prefix invalidates all cached tokens that follow it.

To maximize cache hits across agent iterations and user sessions, prompts should be strictly ordered from **most static to most dynamic**:

1. **Global static system prompt and tool definitions**: Base instructions and schema definitions shared across all users and sessions (globally cached).
2. **Project-level context**: Project instructions, repository configurations (e.g., `CLAUDE.md`, coding standards), or team guidelines (cached across sessions within the same project).
3. **Session-level context**: Environment variables, working directory paths, active MCP server summaries, and output preferences (cached across turns within a session).
4. **Conversation history and messages**: The sequence of user messages, assistant tool calls, and tool outputs that grows incrementally turn-by-turn.

## Harness design principles for cache preservation

Because any prefix drift invalidates downstream cache, agent harnesses must be engineered around specific constraints:

### 1. Never add or remove tools mid-session

Tool definitions are part of the cached prefix. Adding, removing, or reordering tools between turns invalidates the cache for the entire conversation history.

- **State transitions via tools**: If an agent should enter a constrained mode (such as Plan Mode or read-only mode), do not swap the tool schemas. Instead, maintain a stable tool set and provide state tools (e.g., `EnterPlanMode` and `ExitPlanMode`). Calling the tool updates agent instructions via conversation messages while keeping tool schemas identical.
- **Deferred tool loading**: When dealing with dozens of MCP tools, avoid dynamically loading and unloading schemas. Send stable, lightweight stubs (`defer_loading: true`) and let the model retrieve full schemas on demand via a tool search tool without breaking prefix order.

### 2. Use messages for dynamic updates

Avoid injecting dynamic data (such as current timestamps, changing git status, or updated file notifications) into the static system prompt. Modifying the system prompt triggers an immediate cache miss across the entire prompt.

Instead, inject updates into the conversation flow as message turn metadata or system reminders (e.g., `<system-reminder>` blocks inside user messages or tool outputs).

### 3. Avoid mid-session model switching

Prompt caches are isolated per model. If an agent is 100k tokens into a conversation with a large model (e.g., Claude Opus), switching to a cheaper model (e.g., Claude Haiku) for a simple subtask requires re-uploading and reprocessing the full 100k context to build a brand new cache on the small model. This makes mid-session model switching within the same conversation thread more expensive and slower than continuing with the larger, already-cached model.

### 4. Cache-safe compaction and forking

When an agent reaches context window limits, compaction is required to summarize conversation history. Initiating a standalone summarization call with a different prompt and stripped tools causes the prefixes to diverge at token 0, incurring full uncached input fees for the entire history.

Instead, execute **cache-safe forking**: invoke compaction using the exact same system prompt, tool definitions, and conversation prefix, appending the summarization request as the final user message. The request achieves a near-100% cache hit on the parent prefix. Harnesses must reserve a compaction buffer in the context window to accommodate this final turn.

## Cache hit ratio and observability

Prompt cache hit ratio (`cache_read_tokens / total_prompt_tokens`) is a primary operational reliability and cost metric. In production agent harnesses, cache hit rates should be monitored and alerted on like system availability:

- **LLM Gateway tracking**: An [LLM gateway](/ai-engineering/enterprise/llm-gateway.md) such as LiteLLM can track prompt cache hit ratios across providers centrally via custom middleware and logging hooks, alerting when cache hit rates drop below target thresholds.
- **Agent tracing**: Observability platforms like [Langfuse](/ai-engineering/observability/langfuse.md) capture token usage breakdowns (`cache_read`, `cache_creation`, and uncached input) across LangChain and custom agent traces, enabling step-level inspection of cache invalidation causes.

## Interaction with subagents

The caching mechanics of the main agent context affect multi-agent orchestration.
A [subagent](/ai-engineering/harness/subagents.md) starts a separate context thread,
but matching prompt prefixes may still be reused within the provider's cache
boundaries. A warm parent can be cheaper than a new worker; compare actual cache
usage and worker effort rather than assuming every worker is entirely cold. See
[Dynamic Subagents](/ai-engineering/harness/dynamic-subagents.md) for Claude Code's
documented sibling-prefix reuse.

---
type: Tool
title: Langfuse
description: Open-source LLM observability and tracing, OpenTelemetry-friendly.
resource: https://langfuse.com
tags:
- ai-engineering
- observability
parent: /ai-engineering/observability.md
related:
- /ai-engineering/context/prompt-caching.md
- /ai-engineering/observability/langsmith.md
- /software-engineering/reliability/toil.md
sources:
- id: ref-1
  resource: https://langfuse.com
  title: langfuse.com
generated:
  by: antigravity/gemini-3-8-flash
  at: '2026-10-15T17:37:45+04:00'
---

Reference: <https://langfuse.com>

Langfuse is an open-source LLM observability platform — self-hostable tracing, metrics, and evals, a vendor-neutral alternative to [LangSmith](/ai-engineering/observability/langsmith.md) on the same OTel backbone.

Its LLM-as-a-judge evaluators can run online. They score incoming production observations that match filter rules and write the scores with reasoning back onto the traces, which makes them a continuous quality signal for agents to act on (see [toil](/software-engineering/reliability/toil.md#agents-as-toil-automation)).

For agent frameworks like LangChain, Langfuse captures detailed token usage breakdowns — distinguishing cached input reads from uncached input and cache creation. This allows teams to track the [prompt caching](/ai-engineering/context/prompt-caching.md) cache hit ratio as a first-class metric per run, agent turn, or step, pinpointing prefix invalidations and excessive context expansion.

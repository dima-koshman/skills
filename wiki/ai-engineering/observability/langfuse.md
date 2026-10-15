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
- /ai-engineering/observability/langsmith.md
- /software-engineering/reliability/toil.md
sources:
- id: ref-1
  resource: https://langfuse.com
  title: langfuse.com
generated:
  by: codex/gpt-6
  at: '2026-10-15T15:23:06+04:00'
---

Reference: <https://langfuse.com>

Langfuse is an open-source LLM observability platform — self-hostable tracing, metrics, and evals, a vendor-neutral alternative to [LangSmith](/ai-engineering/observability/langsmith.md) on the same OTel backbone.

Its LLM-as-a-judge evaluators can run online. They score incoming production observations that match filter rules and write the scores with reasoning back onto the traces, which makes them a continuous quality signal for agents to act on (see [toil](/software-engineering/reliability/toil.md#agents-as-toil-automation)).

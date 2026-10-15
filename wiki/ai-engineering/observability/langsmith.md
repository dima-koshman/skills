---
type: Tool
title: LangSmith
description: LangChain's tracing and evaluation platform for LLM/agent observability.
resource: https://www.langchain.com/langsmith
tags:
- ai-engineering
- observability
parent: /ai-engineering/observability.md
related:
- /ai-engineering/observability/langsmith-evals.md
- /ai-engineering/observability/langfuse.md
- /software-engineering/reliability/toil.md
sources:
- id: ref-1
  resource: https://www.langchain.com/langsmith
  title: www.langchain.com
- id: ref-2
  resource: https://docs.langchain.com/langsmith/engine-overview
  title: LangSmith Engine
generated:
  by: codex/gpt-6
  at: '2026-10-15T15:23:06+04:00'
---

Reference: <https://www.langchain.com/langsmith>

LangSmith is LangChain's managed platform for tracing, monitoring, and [evaluating](/ai-engineering/observability/langsmith-evals.md) LLM apps and agents — the observability backend used across this work. [Langfuse](/ai-engineering/observability/langfuse.md) is the open-source alternative.

[LangSmith Engine](https://docs.langchain.com/langsmith/engine-overview) is its in-product agent. It scans tracing projects on a schedule, groups recurring failures into issues, diagnoses them against connected source code, and proposes fixes as pull requests. See [toil](/software-engineering/reliability/toil.md#agents-as-toil-automation) for where this fits.

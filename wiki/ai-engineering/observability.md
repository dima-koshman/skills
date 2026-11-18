---
type: Knowledge Area
title: Observability and Evaluation
aliases:
- LangSmith
- LangSmith Evals
- Langfuse
description: 'Tracing, monitoring and evaluation platforms for LLM apps and agents: LangSmith, managed and with
  evals and an in-product agent, and Langfuse, open source and self-hostable.'
tags:
- ai-engineering
- observability
parent: /ai-engineering.md
related:
- /software-engineering/reliability/toil.md
- /ai-engineering/context/prompt-caching.md
status: draft
sources:
- id: ref-1
  resource: https://www.langchain.com/langsmith
  title: www.langchain.com
- id: ref-2
  resource: https://docs.langchain.com/langsmith/engine-overview
  title: LangSmith Engine
- id: langsmith-evals-ref-1
  resource: https://docs.langchain.com/oss/python/langchain/test/evals
  title: docs.langchain.com
- id: langfuse-ref-1
  resource: https://langfuse.com
  title: langfuse.com
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-18T12:00:00+04:00'
---

| | [LangSmith](/ai-engineering/observability.md#langsmith) | [Langfuse](/ai-engineering/observability.md#langfuse) |
| --- | --- | --- |
| Maker and hosting | LangChain, managed | Open source, self-hostable |
| Tracing | Traces and monitoring for LLM apps and agents | OpenTelemetry-friendly tracing and metrics |
| Evals | Datasets, LLM-as-judge and custom evaluators, experiments over traces | LLM-as-a-judge evaluators, also online on production observations |
| Notable | LangSmith Engine: scheduled failure grouping, diagnosis and fix PRs | Token usage split into cached reads, uncached input and cache creation |

## LangSmith

Reference: <https://www.langchain.com/langsmith>

LangSmith is LangChain's managed platform for tracing, monitoring, and [evaluating](/ai-engineering/observability.md#langsmith-evals) LLM apps and agents — the observability backend used across this work. [Langfuse](/ai-engineering/observability.md#langfuse) is the open-source alternative.

[LangSmith Engine](https://docs.langchain.com/langsmith/engine-overview) is its in-product agent. It scans tracing projects on a schedule, groups recurring failures into issues, diagnoses them against connected source code, and proposes fixes as pull requests. See [toil](/software-engineering/reliability/toil.md#agents-as-toil-automation) for where this fits.

### LangSmith Evals

Dataset and evaluator tooling in LangSmith for offline and online agent evaluation.

Reference: <https://docs.langchain.com/oss/python/langchain/test/evals>

[LangSmith](/ai-engineering/observability.md#langsmith)'s evaluation tooling runs datasets, LLM-as-judge and custom evaluators, and experiments over traces — the operational side of evals in this stack.

## Langfuse

Reference: <https://langfuse.com>

Langfuse is an open-source LLM observability platform — self-hostable tracing, metrics, and evals, a vendor-neutral alternative to [LangSmith](/ai-engineering/observability.md#langsmith) on the same OTel backbone.

Its LLM-as-a-judge evaluators can run online. They score incoming production observations that match filter rules and write the scores with reasoning back onto the traces, which makes them a continuous quality signal for agents to act on (see [toil](/software-engineering/reliability/toil.md#agents-as-toil-automation)).

For agent frameworks like LangChain, Langfuse captures detailed token usage breakdowns — distinguishing cached input reads from uncached input and cache creation. This allows teams to track the [prompt caching](/ai-engineering/context/prompt-caching.md) cache hit ratio as a first-class metric per run, agent turn, or step, pinpointing prefix invalidations and excessive context expansion.

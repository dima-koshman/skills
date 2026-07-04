---
type: Practice
title: AI Observability & Tracing
description: Capturing traces, spans, and metrics of LLM/agent execution to debug, evaluate, and monitor in production.
tags: [observability, tracing, opentelemetry, langsmith]
timestamp: 2026-07-04T00:00:00Z
---

AI observability is the practice of instrumenting LLM and
[agent](/agents/agent-architecture.md) runs so every prompt, tool call,
retrieval, and decision is captured as a **trace** of nested **spans**, with
token/cost/latency metrics attached. It is the difference between "the agent did
something weird" and a reproducible timeline of exactly what it saw and did.

## In an enterprise platform

Agents are non-deterministic and multi-step; without tracing they are
undebuggable. In an enterprise [gateway](/enterprise/llm-gateway.md), the trace is
also the **audit record** and the raw material for
[evals](/evaluation/evals.md) and [guardrail](/security/controls/guardrails.md) tuning —
one instrumentation layer serves debugging, compliance, and quality.

## Design considerations

- **Trace the whole agent, not just the model call** — tool I/O, retrieval, and
  control-flow branches are where bugs live.
- **OTel as the neutral backbone** — emit OpenTelemetry so you can send to
  LangSmith, Logfire, or any backend without re-instrumenting; avoids
  vendor lock-in the way the platform does elsewhere.
- **Correlate by thread/session** — link spans across turns to follow a
  conversation, not just a request.
- **Mask before you trace** — traces capture raw I/O; apply
  [PII masking](/security/controls/pii-masking.md) on the path into telemetry.
- **Close the loop** — production traces become eval datasets and injection
  forensics; treat observability as input to quality, not just monitoring.

# Citations

[1] [LangSmith](https://www.langchain.com/langsmith)
[2] [OpenTelemetry](https://opentelemetry.io)
[3] [Anthropic Engineering blog](https://www.anthropic.com/engineering)

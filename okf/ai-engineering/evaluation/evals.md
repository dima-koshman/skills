---
type: Practice
title: Evals & LLM-as-Judge
description: Systematic measurement of LLM/agent quality offline and online, often using model-graded scoring.
tags: [evals, quality, llm-as-judge, testing]
timestamp: 2026-07-04T00:00:00Z
---

Evals are the systematic measurement of LLM/agent output quality: curated
datasets, scoring functions, and regression gates. Because outputs are open-
ended, scoring often uses **LLM-as-judge** — a model grading another model's
output against a rubric — alongside deterministic checks (exact match, schema,
tool-call correctness). Evals are to AI systems what tests are to software.

## In an enterprise platform

Without evals, every prompt or model change is a guess and every regression is
found in production. For a platform team, evals are the gate that lets you
upgrade models, refactor [agents](/agents/agent-architecture.md), or tune
[guardrails](/security/controls/guardrails.md) with confidence rather than fear.

## Design considerations

- **Deterministic first, judge second** — cheap exact/schema/tool checks catch
  most regressions; reserve LLM-as-judge for open-ended quality where it earns
  its cost and noise.
- **Judge the judge** — calibrate the grader against human labels; an
  unvalidated judge manufactures false confidence.
- **Offline + online** — a static regression suite for CI *and* sampled scoring
  of live traffic; production behavior drifts from your test set.
- **Traces are your dataset** — mine [observability](/observability/observability.md)
  for real failures and hard cases instead of inventing synthetic ones.
- **Same judge, two jobs** — the model-based scorer doubles as a production
  [guardrail](/security/controls/guardrails.md); build it once.
- **Domain evals** — score [PII detection](/security/controls/pii-masking.md) and
  [injection](/security/threats/asi01-agent-goal-hijack.md) resistance explicitly, not just
  "helpfulness."

# Citations

[1] [LangSmith](https://www.langchain.com/langsmith)
[2] [LangChain blog](https://www.langchain.com/blog)

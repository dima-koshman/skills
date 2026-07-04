---
type: Control
title: Guardrails
description: Input/output controls that constrain LLM behavior to a safe, policy-compliant envelope.
tags: [security, control, policy, moderation]
timestamp: 2026-07-04T00:00:00Z
---

Guardrails are the deterministic and model-based controls wrapped around an LLM
call to keep behavior inside a safe envelope: input filters (jailbreak/
[injection](/security/threats/asi01-agent-goal-hijack.md) detection, topic limits), output
filters (moderation, PII checks, schema/format validation), and action gates
(approval required before destructive tool calls). They are policy enforcement,
distinct from the model's own alignment.

## In an enterprise platform

In an enterprise [gateway](/enterprise/llm-gateway.md), guardrails are where
compliance becomes executable — the uniform layer that every agent inherits
rather than re-implementing. They convert "the model should not…" into "the
platform will not let it."

## Design considerations

- **Layer the checks** — cheap deterministic validators (regex, schema, all/deny
  lists) first; expensive model-based judges only where needed.
- **Output path is the priority** — most real damage (leaks, unsafe content) is
  on egress; validate before the response leaves the boundary.
- **Fail closed for high-risk actions** — ambiguous → block or route to a human,
  don't pass through.
- **Guardrails ≠ evals, but share machinery** — the same judge that gates
  production traffic can score offline [evals](/evaluation/evals.md); reuse it.
- **Measure the guardrails themselves** — false-positive/negative rates matter;
  a guardrail nobody can tune becomes a guardrail everyone disables.

## Related

Mitigate [prompt injection](/security/threats/asi01-agent-goal-hijack.md); complement
[PII masking](/security/controls/pii-masking.md) on the output path; observable via
[tracing](/observability/observability.md).

# Citations

[1] [OWASP GenAI / LLM Top 10](https://genai.owasp.org)
[2] [State of Agentic AI Security and Governance v2.01 — OWASP](https://genai.owasp.org/resource/state-of-agentic-ai-security-and-governance/)

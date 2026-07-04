---
type: Control
title: PII Masking & Anonymization
description: Detecting and redacting or tokenizing personal data in LLM inputs/outputs, reversibly where needed.
tags: [security, control, privacy, pii]
timestamp: 2026-07-04T00:00:00Z
---

PII masking is the detection and transformation of personal data flowing through
an AI system — redaction, pseudonymization, or reversible tokenization — so that
sensitive fields never reach a model, a log, or a third party in the clear. In a
bank, this is a hard regulatory boundary, not a nice-to-have.

## In an enterprise platform

The masker is the third pillar of the enterprise triad and a key
[guardrail](/security/controls/guardrails.md) on the [gateway](/enterprise/llm-gateway.md)
output path. It is also a [prompt-injection](/security/threats/asi01-agent-goal-hijack.md)
containment control: even if an agent is hijacked, masked egress limits what can
actually leak.

## Design considerations

- **Detection quality is the ceiling** — recognizer coverage (NER + patterns +
  context) bounds everything downstream; Presidio locally, or an API detector,
  with domain-specific recognizers for local identifiers.
- **Reversible vs. irreversible** — redaction for logs/telemetry; reversible
  tokenization when the workflow must restore the original (e.g. round-tripping
  a ticket). Store the mapping in a vault, never inline.
- **Placement** — anonymize *before* logging/tracing and *before* egress; inject
  real secrets only inside the trusted boundary, after masking is applied to
  outputs.
- **Locale matters** — names, IDs, and formats are region-specific
  (Azerbaijan/Turkic naming, local doc numbers); generic English models
  under-detect. Tune and evaluate on real local data.
- **Measure it** — treat detection as a scored task with precision/recall
  [evals](/evaluation/evals.md); a silent miss is a breach.

# Citations

[1] [State of Agentic AI Security and Governance v2.01 — OWASP](https://genai.owasp.org/resource/state-of-agentic-ai-security-and-governance/)
[2] [Bir MCP — anonymization middleware (Presidio/Dataiku)](https://gitlab.com/koshmandk/bir_mcp)

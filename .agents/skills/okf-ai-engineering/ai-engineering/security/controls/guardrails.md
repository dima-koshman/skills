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

# Related

Mitigate [prompt injection](/security/threats/asi01-agent-goal-hijack.md); complement
[PII masking](/security/controls/pii-masking.md) on the output path.

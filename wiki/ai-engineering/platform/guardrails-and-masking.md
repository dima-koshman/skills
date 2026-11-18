---
type: Security Control
title: Guardrails and PII Masking
aliases:
- Guardrails
- PII Masking & Anonymization
description: 'Controls around model and tool calls: guardrails keep behavior inside a policy envelope, and PII masking
  keeps personal data from reaching models, logs or third parties in the clear.'
tags:
- ai-engineering
- platform
- security
- mitigations
parent: /ai-engineering/platform.md
related:
- /ai-engineering/security.md
- /ai-engineering/platform/ai-gateways.md
status: draft
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-18T12:00:00+04:00'
mitigates:
- /ai-engineering/security.md
---

## Guardrails

**Control surface:** input, output, tool actions.

Guardrails are the deterministic and model-based controls wrapped around an LLM
call to keep behavior inside a safe envelope: input filters (jailbreak/
[injection](/ai-engineering/security.md#risks-owasp-agentic-top-10) detection, topic limits), output
filters (moderation, PII checks, schema/format validation), and action gates
(approval required before destructive tool calls). They are policy enforcement,
distinct from the model's own alignment. They complement
[PII masking](/ai-engineering/platform/guardrails-and-masking.md#pii-masking--anonymization) on the output path and are
typically enforced at the [MCP gateway](/ai-engineering/platform/ai-gateways.md#mcp-gateway).

## PII Masking & Anonymization

**Control surface:** LLM inputs, LLM outputs, logs, third-party data flows.

PII masking is the detection and transformation of personal data flowing through
an AI system — redaction, pseudonymization, or reversible tokenization — so that
sensitive fields never reach a model, a log, or a third party in the clear. It is
the privacy counterpart to [guardrails](/ai-engineering/platform/guardrails-and-masking.md#guardrails) and is
typically enforced at the [MCP gateway](/ai-engineering/platform/ai-gateways.md#mcp-gateway). In a bank,
this is a hard regulatory boundary, not a nice-to-have.

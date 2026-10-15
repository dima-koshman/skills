---
type: Security Control
title: PII Masking & Anonymization
description: Detecting and redacting or tokenizing personal data in LLM inputs/outputs, reversibly where
  needed.
tags:
- ai-engineering
- security
- mitigations
parent: /ai-engineering/security/mitigations.md
related:
- /ai-engineering/security/mitigations/guardrails.md
- /ai-engineering/enterprise/mcp-gateway.md
control_surface:
- LLM inputs
- LLM outputs
- logs
- third-party data flows
generated:
  by: codex/gpt-6
  at: '2026-10-15T15:23:06+04:00'
---

PII masking is the detection and transformation of personal data flowing through
an AI system — redaction, pseudonymization, or reversible tokenization — so that
sensitive fields never reach a model, a log, or a third party in the clear. It is
the privacy counterpart to [guardrails](/ai-engineering/security/mitigations/guardrails.md) and is
typically enforced at the [MCP gateway](/ai-engineering/enterprise/mcp-gateway.md). In a bank,
this is a hard regulatory boundary, not a nice-to-have.

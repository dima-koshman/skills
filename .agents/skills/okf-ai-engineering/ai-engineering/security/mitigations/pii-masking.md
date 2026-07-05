---
type: Technique
title: PII Masking & Anonymization
description: Detecting and redacting or tokenizing personal data in LLM inputs/outputs, reversibly where needed.
---

PII masking is the detection and transformation of personal data flowing through
an AI system — redaction, pseudonymization, or reversible tokenization — so that
sensitive fields never reach a model, a log, or a third party in the clear. It is
the privacy counterpart to [guardrails](/security/mitigations/guardrails.md) and is
typically enforced at the [MCP gateway](/enterprise/mcp-gateway.md). In a bank,
this is a hard regulatory boundary, not a nice-to-have.

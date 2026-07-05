---
type: Control
title: PII Masking & Anonymization
description: Detecting and redacting or tokenizing personal data in LLM inputs/outputs, reversibly where needed.
tags: [security, control, privacy, pii]
timestamp: 2026-07-04T00:00:00Z
---

PII masking is the detection and transformation of personal data flowing through
an AI system — redaction, pseudonymization, or reversible tokenization — so that
sensitive fields never reach a model, a log, or a third party in the clear. It is
the privacy counterpart to [guardrails](/security/controls/guardrails.md) and is
typically enforced at the [MCP gateway](/enterprise/mcp-gateway.md). In a bank,
this is a hard regulatory boundary, not a nice-to-have.

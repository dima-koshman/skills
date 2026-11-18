---
type: Knowledge Area
title: AI Platform
description: 'The enterprise control layer around agents: gateways for model and tool traffic, guardrails and personal-data
  masking.'
tags:
- ai-engineering
- platform
parent: /ai-engineering.md
status: draft
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-18T12:00:00+04:00'
topics:
- /ai-engineering/platform/ai-gateways.md
- /ai-engineering/platform/guardrails-and-masking.md
---

The controls an enterprise runs around its agents, so individual apps stay thin. The risks these controls contain are in [Agent Security](/ai-engineering/security.md).

## Topics

- [AI Gateways](/ai-engineering/platform/ai-gateways.md) — The control points between AI clients and what they call: the LLM gateway in front of models and the MCP gateway in front of tools, centralizing auth, permissions, routing, policy and audit.
- [Guardrails and PII Masking](/ai-engineering/platform/guardrails-and-masking.md) — Controls around model and tool calls: guardrails keep behavior inside a policy envelope, and PII masking keeps personal data from reaching models, logs or third parties in the clear.

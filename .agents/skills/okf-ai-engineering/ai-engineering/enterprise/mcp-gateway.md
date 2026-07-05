---
type: Technique
title: MCP Gateway
description: An enterprise gateway multiplexing MCP servers behind auth, permissions, secrets, and audit.
---

An MCP gateway is the control point in front of many [MCP](/context/mcp.md) servers — one authenticated endpoint applying permissions, secret injection, [anonymization](/security/mitigations/pii-masking.md), [guardrails](/security/mitigations/guardrails.md), and audit. It is the tool-side counterpart to the [LLM gateway](/enterprise/llm-gateway.md) and the main control against [agent identity & privilege abuse](/security/risks/identity-privilege-abuse.md).

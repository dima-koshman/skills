---
type: Architecture Pattern
title: MCP Gateway
description: An enterprise gateway multiplexing MCP servers behind auth, permissions, secrets, and audit.
tags: [enterprise, mcp, gateway, platform]
timestamp: 2026-07-05T00:00:00Z
---

An MCP gateway is the control point in front of many [MCP](/context/mcp.md) servers — one authenticated endpoint applying permissions, secret injection, [anonymization](/security/controls/pii-masking.md), [guardrails](/security/controls/guardrails.md), and audit. It is the tool-side counterpart to the [LLM gateway](/enterprise/llm-gateway.md) and the main control against [agent identity & privilege abuse](/security/threats/identity-privilege-abuse.md).

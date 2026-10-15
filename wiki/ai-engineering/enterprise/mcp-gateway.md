---
type: Concept
title: MCP Gateway
description: An enterprise gateway multiplexing MCP servers behind auth, permissions, secrets, and audit.
tags:
- ai-engineering
- enterprise
parent: /ai-engineering/enterprise.md
related:
- /ai-engineering/context/mcp.md
- /ai-engineering/security/mitigations/pii-masking.md
- /ai-engineering/security/mitigations/guardrails.md
- /ai-engineering/enterprise/llm-gateway.md
- /ai-engineering/security/risks/identity-privilege-abuse.md
plane: control
policy_surface: tool and resource access
generated:
  by: codex/gpt-6
  at: '2026-10-15T15:23:06+04:00'
---

An MCP gateway is the control point in front of many [MCP](/ai-engineering/context/mcp.md) servers — one authenticated endpoint applying permissions, secret injection, [anonymization](/ai-engineering/security/mitigations/pii-masking.md), [guardrails](/ai-engineering/security/mitigations/guardrails.md), and audit. It is the tool-side counterpart to the [LLM gateway](/ai-engineering/enterprise/llm-gateway.md) and the main control against [agent identity & privilege abuse](/ai-engineering/security/risks/identity-privilege-abuse.md).

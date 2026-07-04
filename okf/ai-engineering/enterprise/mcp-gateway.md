---
type: Architecture Pattern
title: "MCP Gateway"
description: An enterprise gateway multiplexing MCP servers behind auth, permissions, secrets, and audit.
resource: https://gitlab.com/koshmandk/bir_mcp
tags: [enterprise, mcp, gateway, platform]
timestamp: 2026-07-05T00:00:00Z
---

An MCP gateway is the enterprise control point in front of many MCP servers — one authenticated endpoint applying permissions, secret injection, anonymization, and audit (see Bir MCP).

## In an enterprise platform

_TODO: how this manifests in the platform / gateway / agents, and why it matters here._

## Design considerations

- _TODO: key decisions, mitigations, and tradeoffs._

## Related

- [MCP](/context/mcp.md)
- [LLM Gateway](/enterprise/llm-gateway.md)
- [Guardrails](/security/controls/guardrails.md)
- [PII Masking & Anonymization](/security/controls/pii-masking.md)
- [Agent Identity & Privilege Abuse](/security/threats/asi03-identity-privilege-abuse.md)

# Citations

[1] [MCP Gateway](https://gitlab.com/koshmandk/bir_mcp)

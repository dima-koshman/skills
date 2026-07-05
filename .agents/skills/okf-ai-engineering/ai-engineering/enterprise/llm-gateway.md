---
type: Architecture Pattern
title: LLM Gateway
description: A control plane sitting between AI clients and models/tools for auth, routing, policy, and observability.
tags: [platform, gateway, security, enterprise]
timestamp: 2026-07-04T00:00:00Z
---

An LLM gateway is the control plane between AI clients and the
models they use. It centralizes cross-cutting concerns — authentication,
authorization, rate limiting, routing/failover, content
policy, and audit — so that individual apps and agents stay thin. It is the
model-side counterpart to the [MCP gateway](/enterprise/mcp-gateway.md) and a
natural enforcement point for [guardrails](/security/controls/guardrails.md).

Examples:

- LiteLLM

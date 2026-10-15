---
type: Concept
title: LLM Gateway
description: A control plane sitting between AI clients and models/tools for auth, routing, policy, and
  observability.
tags:
- ai-engineering
- enterprise
parent: /ai-engineering/enterprise.md
related:
- /ai-engineering/context/prompt-caching.md
- /ai-engineering/enterprise/mcp-gateway.md
- /ai-engineering/security/mitigations/guardrails.md
plane: control
policy_surface: model requests
generated:
  by: antigravity/gemini-3-8-flash
  at: '2026-10-15T17:37:30+04:00'
---

An LLM gateway is the control plane between AI clients and the
models they use. It centralizes cross-cutting concerns — authentication,
authorization, rate limiting, routing/failover, content
policy, and audit — so that individual apps and agents stay thin. It is the
model-side counterpart to the [MCP gateway](/ai-engineering/enterprise/mcp-gateway.md) and a
natural enforcement point for [guardrails](/ai-engineering/security/mitigations/guardrails.md).

It is also an essential observation point for token economics and [prompt caching](/ai-engineering/context/prompt-caching.md). Gateways like LiteLLM can track prompt cache hit ratios centrally across all upstream models via middleware or logging hooks, surfacing token efficiency metrics without requiring per-application instrumentation.

Examples:

- LiteLLM

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
- /ai-engineering/harness/model-routing.md
- /software-engineering/reliability/metastable-failures.md
- /ai-engineering/compute/max.md
plane: control
policy_surface: model requests
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-10-16T16:00:00+04:00'
---

An LLM gateway is the control plane between AI clients and the
models they use. It centralizes cross-cutting concerns — authentication,
authorization, rate limiting, routing/failover, content
policy, and audit — so that individual apps and agents stay thin. It is the
model-side counterpart to the [MCP gateway](/ai-engineering/enterprise/mcp-gateway.md) and a
natural enforcement point for [guardrails](/ai-engineering/security/mitigations/guardrails.md).

It is also an essential observation point for token economics and [prompt caching](/ai-engineering/context/prompt-caching.md). Gateways like LiteLLM can track prompt cache hit ratios centrally across all upstream models via middleware or logging hooks, surfacing token efficiency metrics without requiring per-application instrumentation.

"Routing" here means sending a named model to its deployments, with failover and load balancing. Choosing
*which* model a request should use is left to the client or its harness; see
[Model Routing](/ai-engineering/harness/model-routing.md). A gateway that retries upstream calls can also
feed a retry storm; see [Metastable Failures](/software-engineering/reliability/metastable-failures.md).

Examples:

- LiteLLM

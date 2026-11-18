---
type: Concept
title: AI Gateways
aliases:
- LLM Gateway
- MCP Gateway
description: 'The control points between AI clients and what they call: the LLM gateway in front of models and the
  MCP gateway in front of tools, centralizing auth, permissions, routing, policy and audit.'
tags:
- ai-engineering
- platform
- enterprise
parent: /ai-engineering/platform.md
related:
- /ai-engineering/context/prompt-caching.md
- /ai-engineering/platform/guardrails-and-masking.md
- /ai-engineering/harness/model-routing.md
- /software-engineering/reliability/metastable-failures.md
- /ai-engineering/compute/software-stack/max.md
- /ai-engineering/harness/mcp.md
- /ai-engineering/security.md
status: draft
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-18T12:00:00+04:00'
---

Both gateways are control-plane components. They differ in the traffic they govern:

| | LLM gateway | MCP gateway |
| --- | --- | --- |
| Plane | Control | Control |
| Policy surface | Model requests | Tool and resource access |
| Example | LiteLLM | |

## LLM Gateway

An LLM gateway is the control plane between AI clients and the
models they use. It centralizes cross-cutting concerns — authentication,
authorization, rate limiting, routing/failover, content
policy, and audit — so that individual apps and agents stay thin. It is the
model-side counterpart to the [MCP gateway](/ai-engineering/platform/ai-gateways.md#mcp-gateway) and a
natural enforcement point for [guardrails](/ai-engineering/platform/guardrails-and-masking.md#guardrails).

It is also an essential observation point for token economics and [prompt caching](/ai-engineering/context/prompt-caching.md). Gateways like LiteLLM can track prompt cache hit ratios centrally across all upstream models via middleware or logging hooks, surfacing token efficiency metrics without requiring per-application instrumentation.

"Routing" here means sending a named model to its deployments, with failover and load balancing. Choosing
*which* model a request should use is left to the client or its harness; see
[Model Routing](/ai-engineering/harness/model-routing.md). A gateway that retries upstream calls can also
feed a retry storm; see [Metastable Failures](/software-engineering/reliability/metastable-failures.md).

Examples:

- LiteLLM

## MCP Gateway

An MCP gateway is the control point in front of many [MCP](/ai-engineering/harness/mcp.md) servers — one authenticated endpoint applying permissions, secret injection, [anonymization](/ai-engineering/platform/guardrails-and-masking.md#pii-masking--anonymization), [guardrails](/ai-engineering/platform/guardrails-and-masking.md#guardrails), and audit. It is the tool-side counterpart to the [LLM gateway](/ai-engineering/platform/ai-gateways.md#llm-gateway) and the main control against [agent identity & privilege abuse](/ai-engineering/security.md#risks-owasp-agentic-top-10).

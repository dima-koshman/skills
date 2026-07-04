---
type: Architecture Pattern
title: LLM Gateway
description: A control plane sitting between AI clients and models/tools for auth, routing, policy, and observability.
tags: [platform, gateway, security, enterprise]
timestamp: 2026-07-04T00:00:00Z
---

An LLM gateway is the enterprise control plane between AI clients and the
models/tools they use. It centralizes cross-cutting concerns — authentication,
authorization, secret injection, rate limiting, routing/failover, content
policy, and audit — so that individual apps and agents stay thin. In an
MCP-centric platform the same layer multiplexes many
[MCP](/context/mcp.md) subservers behind one authenticated endpoint.

## In an enterprise platform

This is the load-bearing component of the enterprise triad (platform + gateway +
masker). It is where vendor-neutrality is actually enforced: clients depend on
the gateway's contract, not on any one model or backend. It is also the natural
home for every control that must apply *uniformly* — you do not want each agent
re-implementing auth or PII handling.

## Design considerations

- **Middleware pipeline** — model cross-cutting concerns as a composable,
  ordered pipeline (rate-limit → authz → secret-inject →
  [anonymize](/security/controls/pii-masking.md) → [moderate](/security/controls/guardrails.md) →
  log). Order matters: mask before logging, authorize before injecting secrets.
- **Auth bridging** — OIDC proxy / token exchange to connect enterprise SSO to
  clients lacking DCR.
- **Per-user, per-tool permissions** — a graded model (disabled/read/write/
  destroy) beats a binary allow/deny for real IT-ops use.
- **Egress > ingress for data risk** — tool *outputs* are the leak channel;
  anonymization and moderation belong on the response path.
- **Observability is first-class** — the gateway is the one place to get
  complete [traces](/observability/observability.md) across every agent and tool.

## Reference implementation

[Bir MCP](https://gitlab.com/koshmandk/bir_mcp) — an enterprise MCP gateway with
OAuth/OIDC, Vault/Consul-backed secrets, a composable middleware pipeline,
Presidio anonymization, and LangSmith tracing.

# Citations

[1] [The Agentic Operating Model — LangChain](https://www.langchain.com/resources/the-agentic-operating-model)
[2] [Zero Trust for AI agents — Anthropic](https://claude.com/blog/zero-trust-for-ai-agents)
[3] [Anthropic Engineering blog](https://www.anthropic.com/engineering)

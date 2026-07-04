---
type: Threat
title: "ASI01: Agent Goal Hijack"
description: Adversarial input redirects the agent's plan or objective — OWASP's #1 agentic risk, prompt injection being the primary mechanism.
resource: https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/
tags: [security, threat, agents, owasp, asi01]
timestamp: 2026-07-05T00:00:00Z
---

Agent goal hijack is when adversarial input redirects an agent's plan or
objective away from the developer's intent. Its primary mechanism is **prompt
injection** — adversarial instructions embedded in content the model reads (a web
page, a document, a tool result, an email). **Indirect** injection (via data the
agent retrieves rather than the user's own message) is the dangerous variant for
autonomous agents. There is no known complete fix; it is a systemic property of
models that follow natural-language instructions.

## In an enterprise platform

For an [agent](/agents/agent-architecture.md) with real tools behind an
[MCP gateway](/enterprise/mcp-gateway.md), a successful hijack turns the agent
into a confused deputy: it wields the *user's* permissions against the user.
Data exfiltration and unauthorized tool calls are the concrete outcomes. The more
capable the tool surface, the higher the blast radius.

## Design considerations

- **Assume every tool result is hostile** — treat retrieved content as data, not
  instructions; never let it silently escalate.
- **Least privilege is the real control** — scope tool permissions per user and
  per action (disabled/read/write/destroy) so an injection can't reach
  destructive tools.
- **Constrain egress** — the payoff for most injections is exfiltration; gate and
  [anonymize](/security/controls/pii-masking.md) outbound data.
- **Defense in depth, not a silver bullet** — combine
  [guardrails](/security/controls/guardrails.md), human approval for high-risk actions,
  and full [tracing](/observability/observability.md) to detect and forensically
  analyze attempts.
- **Zero-trust framing** — every agent action is authenticated, authorized, and
  logged as if the agent were a potentially-compromised insider.

# Citations

[1] [OWASP GenAI / LLM Top 10](https://genai.owasp.org)
[2] [State of Agentic AI Security and Governance v2.01 — OWASP](https://genai.owasp.org/resource/state-of-agentic-ai-security-and-governance/)
[3] [Zero Trust for AI agents — Anthropic](https://claude.com/blog/zero-trust-for-ai-agents)

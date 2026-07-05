---
type: Overview
title: Security
description: How enterprise agent platforms are attacked and defended — the OWASP Agentic Top 10 risks and the mitigations that contain them.
resource: https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/
---

Agentic systems act with real tools and the user's own permissions, so their
attack surface is the tool, identity, memory, and communication surface — not
just the prompt. This area splits into **risks** (how agents are subverted) and
**mitigations** (what keeps them inside a safe envelope — minimizing risk, never
fully eliminating it). The reference model is the OWASP Top 10 for Agentic
Applications (2026).

# Risks (OWASP Agentic Top 10)

- [Agent Goal Hijack](/security/risks/agent-goal-hijack.md)
- [Tool Misuse & Exploitation](/security/risks/tool-misuse.md)
- [Agent Identity & Privilege Abuse](/security/risks/identity-privilege-abuse.md)
- [Agentic Supply Chain Compromise](/security/risks/supply-chain-compromise.md)
- [Unexpected Code Execution](/security/risks/unexpected-code-execution.md)
- [Memory & Context Poisoning](/security/risks/memory-context-poisoning.md)
- [Insecure Inter-Agent Communication](/security/risks/insecure-inter-agent-communication.md)
- [Cascading Agent Failures](/security/risks/cascading-agent-failures.md)
- [Human-Agent Trust Exploitation](/security/risks/human-agent-trust-exploitation.md)
- [Rogue Agents](/security/risks/rogue-agents.md)

# Mitigations

- [Guardrails](/security/mitigations/guardrails.md) — input/output/action policy enforcement around the model.
- [PII Masking & Anonymization](/security/mitigations/pii-masking.md) — redacting or tokenizing personal data on the way in and out.

Mitigations are enforced in practice at the [LLM gateway](/enterprise/llm-gateway.md)
and [MCP gateway](/enterprise/mcp-gateway.md), under a zero-trust posture: every
agent action authenticated, authorized, least-privileged, and logged.

# Resources

- [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)
- [State of Agentic AI Security and Governance v2.01 — OWASP](https://genai.owasp.org/resource/state-of-agentic-ai-security-and-governance/)
- [Zero Trust for AI agents — Anthropic](https://claude.com/blog/zero-trust-for-ai-agents)

---
type: Overview
title: Security
description: How enterprise agent platforms are attacked and defended — the OWASP Agentic Top 10 threats and the controls that contain them.
resource: https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/
tags: [security, overview, owasp, agents]
timestamp: 2026-07-05T00:00:00Z
---

Agentic systems act with real tools and the user's own permissions, so their
attack surface is the tool, identity, memory, and communication surface — not
just the prompt. This area splits into **threats** (how agents are subverted) and
**controls** (what keeps them inside a safe envelope). The reference model is the
OWASP Top 10 for Agentic Applications (2026).

# Threats (OWASP Agentic Top 10)

- [ASI01: Agent Goal Hijack](/security/threats/asi01-agent-goal-hijack.md)
- [ASI02: Tool Misuse & Exploitation](/security/threats/asi02-tool-misuse.md)
- [ASI03: Agent Identity & Privilege Abuse](/security/threats/asi03-identity-privilege-abuse.md)
- [ASI04: Agentic Supply Chain Compromise](/security/threats/asi04-supply-chain-compromise.md)
- [ASI05: Unexpected Code Execution](/security/threats/asi05-unexpected-code-execution.md)
- [ASI06: Memory & Context Poisoning](/security/threats/asi06-memory-context-poisoning.md)
- [ASI07: Insecure Inter-Agent Communication](/security/threats/asi07-insecure-inter-agent-communication.md)
- [ASI08: Cascading Agent Failures](/security/threats/asi08-cascading-agent-failures.md)
- [ASI09: Human-Agent Trust Exploitation](/security/threats/asi09-human-agent-trust-exploitation.md)
- [ASI10: Rogue Agents](/security/threats/asi10-rogue-agents.md)

# Controls

- [Guardrails](/security/controls/guardrails.md) — input/output/action policy enforcement around the model.
- [PII Masking & Anonymization](/security/controls/pii-masking.md) — redacting or tokenizing personal data on the way in and out.

Controls are enforced in practice at the [LLM gateway](/enterprise/llm-gateway.md)
and [MCP gateway](/enterprise/mcp-gateway.md), under a zero-trust posture: every
agent action authenticated, authorized, least-privileged, and logged.

# Resources

- [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)
- [State of Agentic AI Security and Governance v2.01 — OWASP](https://genai.owasp.org/resource/state-of-agentic-ai-security-and-governance/)
- [Zero Trust for AI agents — Anthropic](https://claude.com/blog/zero-trust-for-ai-agents)

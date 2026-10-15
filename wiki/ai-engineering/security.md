---
type: Knowledge Area
title: Agent Security
description: How enterprise agent platforms are attacked and defended — the OWASP Agentic Top 10 risks
  and the mitigations that contain them.
tags:
- ai-engineering
parent: /ai-engineering.md
related:
- /ai-engineering/security/risks/agent-goal-hijack.md
- /ai-engineering/security/risks/tool-misuse.md
- /ai-engineering/security/risks/identity-privilege-abuse.md
- /ai-engineering/security/risks/supply-chain-compromise.md
- /ai-engineering/security/risks/unexpected-code-execution.md
- /ai-engineering/security/risks/memory-context-poisoning.md
- /ai-engineering/security/risks/insecure-inter-agent-communication.md
- /ai-engineering/security/risks/cascading-agent-failures.md
- /ai-engineering/security/risks/human-agent-trust-exploitation.md
- /ai-engineering/security/risks/rogue-agents.md
- /ai-engineering/security/mitigations/guardrails.md
- /ai-engineering/security/mitigations/pii-masking.md
- /ai-engineering/enterprise/llm-gateway.md
- /ai-engineering/enterprise/mcp-gateway.md
sources:
- id: ref-1
  resource: https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/
  title: genai.owasp.org
- id: ref-2
  resource: https://genai.owasp.org/download/52117/?tmstv=1765059207
  title: download the report (PDF)
- id: ref-3
  resource: https://genai.owasp.org/resource/state-of-agentic-ai-security-and-governance/
  title: State of Agentic AI Security and Governance v2.01 — OWASP
- id: ref-4
  resource: https://claude.com/resources/articles/zero-trust-for-ai-agents
  title: Zero Trust for AI agents — Anthropic
generated:
  by: codex/gpt-6
  at: '2026-10-15T15:23:06+04:00'
topics:
- /ai-engineering/security/mitigations.md
- /ai-engineering/security/risks.md
---

Reference: <https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/>

Agentic systems act with real tools and the user's own permissions, so their
attack surface is the tool, identity, memory, and communication surface — not
just the prompt. This area splits into **risks** (how agents are subverted) and
**mitigations** (what keeps them inside a safe envelope — minimizing risk, never
fully eliminating it). The reference model is the OWASP Top 10 for Agentic
Applications (2026).

## Risks (OWASP Agentic Top 10)

- [Agent Goal Hijack](/ai-engineering/security/risks/agent-goal-hijack.md)
- [Tool Misuse & Exploitation](/ai-engineering/security/risks/tool-misuse.md)
- [Agent Identity & Privilege Abuse](/ai-engineering/security/risks/identity-privilege-abuse.md)
- [Agentic Supply Chain Compromise](/ai-engineering/security/risks/supply-chain-compromise.md)
- [Unexpected Code Execution](/ai-engineering/security/risks/unexpected-code-execution.md)
- [Memory & Context Poisoning](/ai-engineering/security/risks/memory-context-poisoning.md)
- [Insecure Inter-Agent Communication](/ai-engineering/security/risks/insecure-inter-agent-communication.md)
- [Cascading Agent Failures](/ai-engineering/security/risks/cascading-agent-failures.md)
- [Human-Agent Trust Exploitation](/ai-engineering/security/risks/human-agent-trust-exploitation.md)
- [Rogue Agents](/ai-engineering/security/risks/rogue-agents.md)

## Mitigations

- [Guardrails](/ai-engineering/security/mitigations/guardrails.md) — input/output/action policy enforcement around the model.
- [PII Masking & Anonymization](/ai-engineering/security/mitigations/pii-masking.md) — redacting or tokenizing personal data on the way in and out.

Mitigations are enforced in practice at the [LLM gateway](/ai-engineering/enterprise/llm-gateway.md)
and [MCP gateway](/ai-engineering/enterprise/mcp-gateway.md), under a zero-trust posture: every
agent action authenticated, authorized, least-privileged, and logged.

## Resources

- [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) — [download the report (PDF)](https://genai.owasp.org/download/52117/?tmstv=1765059207).
- [State of Agentic AI Security and Governance v2.01 — OWASP](https://genai.owasp.org/resource/state-of-agentic-ai-security-and-governance/)
- [Zero Trust for AI agents — Anthropic](https://claude.com/resources/articles/zero-trust-for-ai-agents) — online article; the linked resource is HTML, not a PDF download.

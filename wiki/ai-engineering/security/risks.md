---
type: Knowledge Area
title: Agentic Security Risks
description: The ten agentic attack surfaces described in the existing OWASP reference notes.
tags:
- ai-engineering
- security
- risks
parent: /ai-engineering/security.md
topics:
- /ai-engineering/security/risks/agent-goal-hijack.md
- /ai-engineering/security/risks/cascading-agent-failures.md
- /ai-engineering/security/risks/human-agent-trust-exploitation.md
- /ai-engineering/security/risks/identity-privilege-abuse.md
- /ai-engineering/security/risks/insecure-inter-agent-communication.md
- /ai-engineering/security/risks/memory-context-poisoning.md
- /ai-engineering/security/risks/rogue-agents.md
- /ai-engineering/security/risks/supply-chain-compromise.md
- /ai-engineering/security/risks/tool-misuse.md
- /ai-engineering/security/risks/unexpected-code-execution.md
generated:
  by: codex/gpt-6
  at: '2026-10-15T15:23:06+04:00'
---

## Topics

- [Agent Goal Hijack](/ai-engineering/security/risks/agent-goal-hijack.md) — Adversarial input redirects the agent's plan or objective — OWASP's #1 agentic risk, prompt injection being the primary mechanism.
- [Cascading Agent Failures](/ai-engineering/security/risks/cascading-agent-failures.md) — A local failure or compromise propagates across agents and tools into a systemic failure.
- [Human-Agent Trust Exploitation](/ai-engineering/security/risks/human-agent-trust-exploitation.md) — The agent is used to manipulate the human, or humans over-trust the agent's output.
- [Agent Identity & Privilege Abuse](/ai-engineering/security/risks/identity-privilege-abuse.md) — The agent's identity or permissions are misused, impersonated, or escalated.
- [Insecure Inter-Agent Communication](/ai-engineering/security/risks/insecure-inter-agent-communication.md) — Trust, spoofing, or tampering weaknesses in messaging between agents.
- [Memory & Context Poisoning](/ai-engineering/security/risks/memory-context-poisoning.md) — Malicious content persists in the agent's memory or context and influences later decisions.
- [Rogue Agents](/ai-engineering/security/risks/rogue-agents.md) — Unauthorized or compromised agents operating outside governance and oversight.
- [Agentic Supply Chain Compromise](/ai-engineering/security/risks/supply-chain-compromise.md) — Malicious or compromised components — tools, MCP servers, models, dependencies — enter the agent supply chain.
- [Tool Misuse & Exploitation](/ai-engineering/security/risks/tool-misuse.md) — The agent invokes tools in ways they were not intended or authorized for.
- [Unexpected Code Execution](/ai-engineering/security/risks/unexpected-code-execution.md) — The agent executes attacker-influenced code, e.g. via a code interpreter or a tool with an RCE path.

---
type: Knowledge Area
title: Agent Security
aliases:
- Agent Goal Hijack
- Tool Misuse & Exploitation
- Agent Identity & Privilege Abuse
- Agentic Supply Chain Compromise
- Unexpected Code Execution
- Memory & Context Poisoning
- Insecure Inter-Agent Communication
- Cascading Agent Failures
- Human-Agent Trust Exploitation
- Rogue Agents
- Agentic Security Risks
description: 'How enterprise agent platforms are attacked: the OWASP Agentic Top 10 risks in one table, with pointers
  to the platform controls that contain them.'
tags:
- ai-engineering
parent: /ai-engineering.md
related:
- /ai-engineering/platform.md
- /ai-engineering/platform/ai-gateways.md
- /ai-engineering/platform/guardrails-and-masking.md
status: draft
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
  by: claude-code/claude-opus-5-5
  at: '2026-11-18T12:00:00+04:00'
---

Reference: <https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/>

Agentic systems act with real tools and the user's own permissions, so their
attack surface is the tool, identity, memory, and communication surface — not
just the prompt. This page covers the **risks** (how agents are subverted). The **mitigations**, which keep
agents inside a safe envelope (minimizing risk, never fully eliminating it), are in
[AI Platform](/ai-engineering/platform.md). The reference model is the OWASP Top 10 for Agentic
Applications (2026).

## Risks (OWASP Agentic Top 10)

| # | Risk | Surface | Description |
| --- | --- | --- | --- |
| 1 | Agent Goal Hijack | goals and instructions | Adversarial input redirects the agent's plan or objective — OWASP's #1 agentic risk, prompt injection being the primary mechanism. |
| 2 | Tool Misuse & Exploitation | tool invocation | The agent invokes tools in ways they were not intended or authorized for. |
| 3 | Agent Identity & Privilege Abuse | identity and authorization | The agent's identity or permissions are misused, impersonated, or escalated. |
| 4 | Agentic Supply Chain Compromise | dependencies and components | Malicious or compromised components — tools, MCP servers, models, dependencies — enter the agent supply chain. |
| 5 | Unexpected Code Execution | code execution | The agent executes attacker-influenced code, e.g. via a code interpreter or a tool with an RCE path. |
| 6 | Memory & Context Poisoning | persistent memory and context | Malicious content persists in the agent's memory or context and influences later decisions. |
| 7 | Insecure Inter-Agent Communication | agent messages | Trust, spoofing, or tampering weaknesses in messaging between agents. |
| 8 | Cascading Agent Failures | failure propagation | A local failure or compromise propagates across agents and tools into a systemic failure. |
| 9 | Human-Agent Trust Exploitation | human trust | The agent is used to manipulate the human, or humans over-trust the agent's output. |
| 10 | Rogue Agents | agent governance | Unauthorized or compromised agents operating outside governance and oversight. |

### Notes per risk

- **Agent Goal Hijack.** Agent goal hijack is when adversarial input redirects an agent's plan or objective away from the developer's intent. Its primary mechanism is **prompt injection** — adversarial instructions embedded in content the model reads (a web page, a document, a tool result, an email). **Indirect** injection (via data the agent retrieves rather than the user's own message) is the dangerous variant for autonomous agents. There is no known complete fix; it is a systemic property of models that follow natural-language instructions.
- **Tool Misuse & Exploitation.** Tool misuse is when an agent is driven to call tools — or chain them — in ways outside their intended, authorized use, turning legitimate capabilities into an attack.
- **Agent Identity & Privilege Abuse.** Identity and privilege abuse covers impersonation, token theft, and privilege escalation — the agent acting with authority it should not have.
- **Agentic Supply Chain Compromise.** Supply chain compromise is the poisoning of what the agent depends on: a backdoored MCP server, a tampered model, a malicious package, or a spoofed tool.
- **Unexpected Code Execution.** Unexpected code execution is when an agent runs attacker-controlled code — a growing risk as agents gain interpreters and code-mode tools.
- **Memory & Context Poisoning.** Memory and context poisoning plants adversarial content that survives across turns — the persistent cousin of goal hijack, corrupting future reasoning.
- **Insecure Inter-Agent Communication.** In multi-agent systems, the channels between agents become an attack surface: unauthenticated messages, spoofed peers, and tampered hand-offs.
- **Cascading Agent Failures.** Cascading failures are when one bad output, loop, or outage ripples through dependent agents and tools — a reliability failure that is also a security one.
- **Human-Agent Trust Exploitation.** Trust exploitation runs both ways: an agent weaponized to socially engineer a person, and humans granting unearned trust to fluent but wrong output.
- **Rogue Agents.** Rogue agents are those running outside the sanctioned control plane — unregistered, compromised, or drifted beyond their mandate.

## Mitigations

- [Guardrails](/ai-engineering/platform/guardrails-and-masking.md#guardrails) — input/output/action policy enforcement around the model.
- [PII Masking & Anonymization](/ai-engineering/platform/guardrails-and-masking.md#pii-masking--anonymization) — redacting or tokenizing personal data on the way in and out.

Mitigations are enforced in practice at the [LLM gateway](/ai-engineering/platform/ai-gateways.md#llm-gateway)
and [MCP gateway](/ai-engineering/platform/ai-gateways.md#mcp-gateway), under a zero-trust posture: every
agent action authenticated, authorized, least-privileged, and logged.

## Resources

- [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) — [download the report (PDF)](https://genai.owasp.org/download/52117/?tmstv=1765059207).
- [State of Agentic AI Security and Governance v2.01 — OWASP](https://genai.owasp.org/resource/state-of-agentic-ai-security-and-governance/)
- [Zero Trust for AI agents — Anthropic](https://claude.com/resources/articles/zero-trust-for-ai-agents) — online article; the linked resource is HTML, not a PDF download.

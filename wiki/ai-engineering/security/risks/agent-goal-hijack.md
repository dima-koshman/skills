---
type: Security Risk
title: Agent Goal Hijack
description: 'Adversarial input redirects the agent''s plan or objective — OWASP''s #1 agentic risk, prompt
  injection being the primary mechanism.'
tags:
- ai-engineering
- security
- risks
parent: /ai-engineering/security/risks.md
risk_surface: goals and instructions
sources:
- id: ref-1
  resource: https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/
  title: genai.owasp.org
generated:
  by: codex/gpt-6
  at: '2026-10-15T15:23:06+04:00'
---

Reference: <https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/>

Agent goal hijack is when adversarial input redirects an agent's plan or
objective away from the developer's intent. Its primary mechanism is **prompt
injection** — adversarial instructions embedded in content the model reads (a web
page, a document, a tool result, an email). **Indirect** injection (via data the
agent retrieves rather than the user's own message) is the dangerous variant for
autonomous agents. There is no known complete fix; it is a systemic property of
models that follow natural-language instructions.

---
type: Security risk
title: Agent Goal Hijack
description: "Adversarial input redirects the agent's plan or objective — OWASP's #1 agentic risk, prompt injection being the primary mechanism."
resource: https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/
---

Agent goal hijack is when adversarial input redirects an agent's plan or
objective away from the developer's intent. Its primary mechanism is **prompt
injection** — adversarial instructions embedded in content the model reads (a web
page, a document, a tool result, an email). **Indirect** injection (via data the
agent retrieves rather than the user's own message) is the dangerous variant for
autonomous agents. There is no known complete fix; it is a systemic property of
models that follow natural-language instructions.

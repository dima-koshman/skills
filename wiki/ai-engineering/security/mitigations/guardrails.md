---
type: Security Control
title: Guardrails
description: Input/output controls that constrain LLM behavior to a safe, policy-compliant envelope.
tags:
- ai-engineering
- security
- mitigations
parent: /ai-engineering/security/mitigations.md
related:
- /ai-engineering/security/risks/agent-goal-hijack.md
- /ai-engineering/security/mitigations/pii-masking.md
- /ai-engineering/enterprise/mcp-gateway.md
mitigates:
- /ai-engineering/security/risks/agent-goal-hijack.md
control_surface:
- input
- output
- tool actions
generated:
  by: codex/gpt-6
  at: '2026-10-15T15:23:06+04:00'
---

Guardrails are the deterministic and model-based controls wrapped around an LLM
call to keep behavior inside a safe envelope: input filters (jailbreak/
[injection](/ai-engineering/security/risks/agent-goal-hijack.md) detection, topic limits), output
filters (moderation, PII checks, schema/format validation), and action gates
(approval required before destructive tool calls). They are policy enforcement,
distinct from the model's own alignment. They complement
[PII masking](/ai-engineering/security/mitigations/pii-masking.md) on the output path and are
typically enforced at the [MCP gateway](/ai-engineering/enterprise/mcp-gateway.md).

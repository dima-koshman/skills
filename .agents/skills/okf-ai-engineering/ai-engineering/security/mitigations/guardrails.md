---
type: Technique
title: Guardrails
description: Input/output controls that constrain LLM behavior to a safe, policy-compliant envelope.
---

Guardrails are the deterministic and model-based controls wrapped around an LLM
call to keep behavior inside a safe envelope: input filters (jailbreak/
[injection](/security/risks/agent-goal-hijack.md) detection, topic limits), output
filters (moderation, PII checks, schema/format validation), and action gates
(approval required before destructive tool calls). They are policy enforcement,
distinct from the model's own alignment. They complement
[PII masking](/security/mitigations/pii-masking.md) on the output path and are
typically enforced at the [MCP gateway](/enterprise/mcp-gateway.md).

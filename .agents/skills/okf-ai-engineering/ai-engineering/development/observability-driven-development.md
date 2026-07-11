---
type: Technique
title: Observability-Driven AI-Assisted Development
description: A development loop where AI agents use real runtime telemetry as evidence for diagnosis, remediation, and verification.
---

Observability-driven AI-assisted development makes runtime evidence part of the
software-development loop. An [agent](/agents/agent.md) retrieves traces, logs,
metrics, exceptions, and evaluation results through [tools](/harness/tools.md),
correlates them with the code and current task, proposes or implements a bounded
change, and verifies the result. Observability is therefore not only for human
dashboards and alerts; it becomes queryable [context](/context/context-engineering.md)
for development agents.

# Core loop

1. **Instrument** the application so important operations, failures, costs, and
   outcomes produce structured telemetry with environment, version, and
   correlation identifiers.
2. **Observe** real behavior in production, staging, tests, and evaluations.
3. **Retrieve** a bounded evidence window through an observability API, CLI, or
   [MCP](/context/mcp.md) server rather than pasting dashboard screenshots or
   unbounded logs into the agent context.
4. **Correlate** signals across systems and map representative events to code,
   configuration, deployments, and existing work items.
5. **Diagnose** root-cause candidates, separating actionable defects from
   expected behavior, external failures, instrumentation gaps, and insufficient
   evidence.
6. **Change** the smallest coherent unit of code, configuration, tests, or
   instrumentation that addresses the supported cause.
7. **Verify** with a reproduction, automated tests, static checks, and a safe
   re-query of the relevant telemetry when the behavior can be exercised.
8. **Learn** by retaining the evidence, decision, and result in issues, pull
   requests, runbooks, evaluations, or durable agent instructions.

The loop is evidence-driven rather than fully autonomous: telemetry informs the
agent's reasoning, but review and deployment controls remain independent gates.

# Operating modes

**Reactive investigation** starts from a reported symptom, failed test, alert,
or trace. The agent narrows the time window, inspects a representative execution,
reproduces the behavior where possible, and fixes the supported root cause during
the active coding or debugging session.

**Proactive retrospection** periodically scans a fixed, non-overlapping runtime
window for repeated exceptions, failed child operations, latency or cost outliers,
and observability gaps. Findings are clustered by root cause and reconciled with
the existing backlog before an agent opens or implements work. A durable
checkpoint records the last fully triaged window so recurring sweeps neither skip
nor silently forget telemetry.

# Complementary evidence

LLM and agent traces expose prompts, model responses, tool calls, trajectories,
latency, token use, and cost. Products such as
[LangSmith](/observability/langsmith.md) and
[Langfuse](/observability/langfuse.md) answer what an AI system saw, decided, and
did.

Application observability exposes standard logs, spans, metrics, exceptions,
database and HTTP activity, and infrastructure health. OpenTelemetry-compatible
systems such as [Logfire](https://logfire.pydantic.dev/docs/) answer what the
software and its environment experienced.

Neither layer replaces the other. A successful top-level agent response can
contain a failed tool call, while an application exception may not explain the
model decision that led to it. Correlation should prefer shared trace or request
identifiers; when none exists, timestamp, environment, operation, and failure
text provide only probabilistic linkage and must be labeled accordingly.

[LangSmith Evals](/observability/langsmith-evals.md) and comparable evaluation
systems add outcome evidence. A production trace can become a regression example,
and a verified fix can be tested across a dataset rather than only against the
single observed failure.

# Required capabilities

- Structured, sufficiently detailed instrumentation at both the AI and
  application layers.
- Stable environment, release, operation, and correlation attributes.
- Read-only, queryable observability interfaces available to the coding agent,
  preferably with schema discovery and deep links to representative evidence.
- Explicit time bounds, result limits, and progressive queries that summarize
  before fetching full traces or stack traces.
- Access to the relevant code, configuration, tests, and work ledger so evidence
  can be connected to a change rather than merely summarized.
- Separate permissions for reading telemetry, editing code, creating work items,
  deploying, and mutating production.
- Verification gates that distinguish test evidence, pre-deployment telemetry,
  and post-deployment confirmation.

# Guardrails and failure modes

- **Telemetry is incomplete evidence.** Missing spans or unattributed errors are
  observability gaps, not proof that a component is healthy or faulty.
- **Correlation can be false.** Do not claim identity across systems without a
  shared identifier; record confidence when correlating indirectly.
- **Noise can create busywork.** Cluster repeated events into root causes and
  deduplicate against existing issues and pull requests.
- **Sensitive data can leak.** Redact or minimize prompts, payloads, credentials,
  and personal data before they reach telemetry or an agent context.
- **Telemetry is untrusted input.** Logs, exceptions, model payloads, and tool
  results may contain attacker-controlled instructions. Treat them as diagnostic
  data and independently verify any suggested action to prevent
  [agent goal hijack](/security/risks/agent-goal-hijack.md).
- **Unbounded retrieval wastes context and money.** Query narrow windows, aggregate
  first, and fetch representative details only as needed.
- **A plausible diagnosis is not verification.** Require a reproduction or other
  causal evidence, targeted tests, review, and relevant telemetry checks.
- **Read access must not imply production authority.** Agents may inspect safely;
  deployment, destructive operations, and checkpoint advancement require explicit
  policy and completion criteria.

# Implementation pattern

One practical implementation pairs an LLM-specific tracer such as LangSmith with
an OpenTelemetry backend such as Logfire, exposes both through scoped CLI or MCP
tools, and gives a coding agent project-specific instructions for identifiers,
environments, query constraints, and signal ownership. This is one realization of
the technique, not a dependency on those products: the invariant is a controlled
path from real behavior to retrievable evidence, bounded change, and verified
learning.

# Citations

- [OpenTelemetry observability primer](https://opentelemetry.io/docs/concepts/observability-primer/)
- [LangSmith observability concepts](https://docs.langchain.com/langsmith/observability-concepts)
- [Logfire MCP server](https://logfire.pydantic.dev/docs/how-to-guides/mcp-server/)
- [Model Context Protocol](https://modelcontextprotocol.io/)

---
type: Overview
title: AI Engineering Knowledge Base
description: A vendor-neutral concept graph for building enterprise AI platforms — gateway, agents, security, and lifecycle.
tags: [overview, enterprise, ai-engineering]
timestamp: 2026-07-04T00:00:00Z
---

A curated, vendor-neutral knowledge graph of the concepts behind building
enterprise-grade AI services — an AI platform, an MCP gateway, and a PII masker.
The notes are written for a practitioner: senior-level framing, key design
considerations, and vetted sources — not beginner explainers, not vendor
tutorials, not model training.

## Map

- **Context** — the protocols the platform is built on:
  [MCP](/context/mcp.md) and the [Open Knowledge Format](/context/okf.md).
- **Enterprise** — the control plane: the [LLM Gateway](/enterprise/llm-gateway.md)
  and the [MCP Gateway](/enterprise/mcp-gateway.md).
- **Agents** — [Agent Architecture](/agents/agent-architecture.md),
  [deepagents](/agents/deepagents.md), the [Agent Harness](/agents/harness.md),
  and [Programmatic Tools & Code Mode](/agents/programmatic-tools.md).
- **Observability** — [tracing](/observability/observability.md) with
  [LangSmith](/observability/langsmith.md) and [Langfuse](/observability/langfuse.md).
- **Evaluation** — [evals & LLM-as-judge](/evaluation/evals.md),
  operationalized via [LangSmith Evals](/evaluation/langsmith-evals.md).
- **Security** — the [OWASP Agentic Top 10](/security/threats/asi01-agent-goal-hijack.md)
  threats, and the controls that contain them:
  [Guardrails](/security/controls/guardrails.md) and [PII Masking](/security/controls/pii-masking.md).

## How to use

Explore the graph on the right or the tree on the left; each concept links to
its neighbors and to the anchoring project work
([Bir MCP](https://gitlab.com/koshmandk/bir_mcp),
[agents](https://github.com/dima-koshman/agents)). Change history lives in the log.

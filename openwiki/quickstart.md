---
type: navigation concept
title: Quickstart
description: Routes readers from the AI-engineering and software-engineering subject maps to the architecture, context, integration, security, observability, distributed-systems, and reliability concepts needed to apply these notes. Use it as a reading path, not as a substitute for current primary evidence.
tags: [navigation, quickstart, ai-engineering, software-engineering, architecture, reliability]
sources:
  - id: openwiki-source-d9d6175b74c75f794b5598b1
    resource: repo://wiki/ai-engineering/ai-engineering.md
  - id: openwiki-source-a0b8980de7acf45593bae1f5
    resource: repo://wiki/ai-engineering/context/openwiki.md
  - id: openwiki-source-5820d936195e5a813ce751e1
    resource: repo://wiki/software-engineering/development.md
generated: { by: "openwiki/0.7.0", at: "2026-10-03T14:38:54.195Z" }
---

# Quickstart

This wiki has two starting points. Choose the subject area that matches the problem, then follow the cross-cutting path that explains how to design, integrate, operate, and improve the system.

## 1. Choose a subject area

### AI engineering

Start with the [AI Engineering map](../wiki/ai-engineering/ai-engineering.md) for model-facing concepts and their neighboring notes. It covers:

- **Agents and execution** — agent architectures, concrete agents, the harness, subagents, and workflows.
- **Context and capabilities** — context engineering, memory, RAG, MCP, the Open Knowledge Format, and client-, provider-, and frontend-side tools.
- **Enterprise boundaries** — LLM and MCP gateways.
- **Quality and risk** — tracing, evaluations, and agent-security risks and mitigations.

For the synthesized architecture view, continue to [Agent Systems Architecture](architecture/agent-systems.md). It explains the division of responsibility between the model, harness, tools, state, subagents, and scripted workflows.

### Software engineering

Start with the [Software Engineering map](../wiki/software-engineering/development.md) for general distributed-systems and service-engineering material. It organizes the subject into:

- **Communication** — Protocol Buffers contracts and gRPC RPCs.
- **Infrastructure** — service meshes and data, control, and management planes.
- **Reliability** — simplicity as a design and operating principle.
- **Learning** — practical exercises and structured training resources.

For the synthesized systems view, continue to [Distributed Communication and Service Infrastructure](software-engineering/distributed-systems.md), then use [Software Reliability and Learning Practice](software-engineering/reliability-and-learning.md) when the question is how to reduce complexity or learn from operational feedback.

## 2. Follow the cross-cutting path

The links below are the shortest route through the concepts that connect both subject areas:

1. **Architecture and control flow** — Read [Agent Systems Architecture](architecture/agent-systems.md) to locate the model loop, harness decisions, tool boundaries, state, limits, and delegation. This is the best first stop when you need to understand who owns a decision or failure.
2. **Context and durable knowledge** — Read [Context, Memory, and Knowledge Retrieval](concepts/context-and-knowledge.md) to distinguish working context, memory, RAG, MCP resources, and durable wiki knowledge. It is the right stop when deciding what to pre-synthesize, retrieve at query time, or treat as authoritative.
3. **Reusable capabilities** — Read [Agent Skills and Tooling](concepts/skills-and-tooling.md) when packaging behavior or exposing tools. Use it to reason about progressive disclosure, invocation cost, scope, and trust.
4. **Providers and interoperability** — Read [Model Providers and Agent Protocols](integrations/models-and-protocols.md) when connecting a model, gateway, or agent protocol. This is the integration boundary between providers, protocols, enterprise gateways, and the harness.
5. **Operations and risk** — Read [Agent Security, Observability, and Evaluation](operations/security-and-observability.md) before deploying capabilities. It connects threat categories and mitigations with runtime controls, telemetry, tracing, evaluations, and feedback loops.
6. **Service boundaries** — Read [Distributed Communication and Service Infrastructure](software-engineering/distributed-systems.md) for interface contracts, RPC traffic, control/data-plane separation, and mesh boundaries around services.
7. **Maintenance and improvement** — Read [Knowledge Maintenance and Provenance](operations/maintenance-and-provenance.md) for source snapshots, citations, freshness, version pins, and generated-page lifecycle; then read [Software Reliability and Learning Practice](software-engineering/reliability-and-learning.md) for simplicity and observability-driven learning.

## 3. Apply the notes safely

OpenWiki generates agent-facing Markdown from local knowledge. Connectors first create deterministic raw snapshots and manifests; source-specific runs then synthesize pages while those raw artifacts remain available for provenance checks. Generated summaries are useful routing and context, but they remain leads for concrete engineering work: current source files, Git history, tests, and other primary evidence take precedence.

The practical loop is therefore:

1. Use this page and the subject maps to find the relevant concept.
2. Follow the linked synthesized page for terminology, boundaries, and trade-offs.
3. Verify implementation or operational decisions against the cited primary source, current code, tests, and runtime evidence.
4. Return to the operations and maintenance pages when freshness, provenance, security, or observability changes the decision.

For OpenWiki background and the primary project reference, see the [OpenWiki source note](../wiki/ai-engineering/context/openwiki.md) and its [OpenWiki repository](https://github.com/langchain-ai/openwiki).

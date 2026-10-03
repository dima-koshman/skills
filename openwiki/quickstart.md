---
type: navigation concept
title: Quickstart
description: Routes readers from the AI-engineering and software-engineering maps through architecture, context, integration, operations, distributed systems, and reliability. Use it as a task-routing path; verify concrete decisions against current primary evidence.
tags: [navigation, quickstart, ai-engineering, software-engineering, architecture, reliability]
sources:
  - id: openwiki-source-d9d6175b74c75f794b5598b1
    resource: repo://wiki/ai-engineering/ai-engineering.md
  - id: openwiki-source-a0b8980de7acf45593bae1f5
    resource: repo://wiki/ai-engineering/context/openwiki.md
  - id: openwiki-source-14513c346c57990de07c91eb
    resource: repo://wiki/ai-engineering/development/observability-driven-development.md
  - id: openwiki-source-a9508fe272f48955fedb194b
    resource: repo://wiki/software-engineering/communication/grpc.md
  - id: openwiki-source-61badaafbd42557c4bdf8d15
    resource: repo://wiki/software-engineering/communication/protobuf.md
  - id: openwiki-source-5820d936195e5a813ce751e1
    resource: repo://wiki/software-engineering/development.md
  - id: openwiki-source-711fcd86217ba6d6b7c209ff
    resource: repo://wiki/software-engineering/infrastructure/service-mesh.md
  - id: openwiki-source-44a3a287089221f50d654ce9
    resource: repo://wiki/software-engineering/reliability/simplicity.md
generated: { by: "openwiki/0.7.0", at: "2026-10-03T16:27:35.648Z" }
verified:
  - by: openwiki/0.7.0
    at: 2026-10-03T16:27:35.648Z
---

# Quickstart

Use this page as a routing map, not as a subject encyclopedia. Start with the
map closest to the task, then follow the cross-cutting path for ownership,
boundaries, operations, and learning.

## 1. Choose a subject map

### AI engineering

Start with the [AI Engineering map](../wiki/ai-engineering/ai-engineering.md).
It is organized around:

- **Agents and execution** — agent architecture, concrete agents, harnesses,
  subagents, and workflows.
- **Context and capabilities** — context engineering, memory, RAG, MCP, the
  Open Knowledge Format, and client-, provider-, and frontend-side tools.
- **Enterprise boundaries** — LLM and MCP gateways.
- **Quality and risk** — tracing, evaluations, and agent-security risks and
  mitigations.

For the synthesized architecture view, read [Agent Systems
Architecture](architecture/agent-systems.md). Use it when you need to locate
the model loop, harness decisions, tools, state, limits, or delegation.

### Software engineering

Start with the [Software Engineering map](../wiki/software-engineering/development.md)
for service and distributed-systems material. Its route is:

- **Communication** — [Protocol Buffers](../wiki/software-engineering/communication/protobuf.md)
  for schema and wire contracts, then [gRPC](../wiki/software-engineering/communication/grpc.md)
  for typed RPCs, streaming, deadlines, cancellation, and status handling.
- **Infrastructure** — [service meshes](../wiki/software-engineering/infrastructure/service-mesh.md)
  and [data, control, and management planes](../wiki/software-engineering/infrastructure/planes.md).
- **Reliability** — [simplicity](../wiki/software-engineering/reliability/simplicity.md)
  as a design and operating principle.
- **Learning** — practical exercises and structured training resources in the map.

For the synthesized systems view, read [Distributed Communication and Service
Infrastructure](software-engineering/distributed-systems.md), then [Software
Reliability and Learning Practice](software-engineering/reliability-and-learning.md).

## 2. Follow the cross-cutting path

These stops connect both maps and are usually the shortest route for a new
design, integration, incident, or change:

1. **Architecture and control flow** — [Agent Systems Architecture](architecture/agent-systems.md)
   identifies who owns decisions, state, limits, delegation, and failures.
2. **Context and durable knowledge** — [Context, Memory, and Knowledge Retrieval](concepts/context-and-knowledge.md)
   separates working context, memory, RAG, MCP resources, and durable wiki knowledge.
3. **Reusable capabilities** — [Agent Skills and Tooling](concepts/skills-and-tooling.md)
   covers packaging, progressive disclosure, invocation cost, scope, and trust.
4. **Providers and interoperability** — [Model Providers and Agent Protocols](integrations/models-and-protocols.md)
   is the boundary between providers, protocols, enterprise gateways, and the harness.
5. **Operations and risk** — [Agent Security, Observability, and Evaluation](operations/security-and-observability.md)
   connects threats and mitigations with runtime controls, telemetry, tracing, and evaluation.
6. **Service boundaries** — [Distributed Communication and Service Infrastructure](software-engineering/distributed-systems.md)
   covers contracts, RPC traffic, plane separation, mesh boundaries, and distributed failure trade-offs.
7. **Maintenance and improvement** — [Knowledge Maintenance and Provenance](operations/maintenance-and-provenance.md)
   covers snapshots, manifests, citations, freshness, version pins, and generated-page lifecycle; then
   [Software Reliability and Learning Practice](software-engineering/reliability-and-learning.md)
   connects simplicity with observability-driven development and structured learning.

## 3. Apply the notes safely

OpenWiki connectors first create deterministic raw snapshots and manifests;
source-specific runs then synthesize pages while those raw artifacts remain
available for provenance checks. Generated pages are useful routing and context,
but generated summaries are leads, not authority: current source files, tests,
Git history, and runtime evidence take precedence for concrete engineering work.

Use this loop:

1. Find the relevant concept through this page or a subject map.
2. Read the linked synthesized page for terminology, boundaries, and trade-offs.
3. Check the cited primary source, current code, tests, Git history, and runtime
   evidence before changing implementation or operations.
4. Return to the operations and maintenance pages when freshness, provenance,
   security, or observability affects the decision.

For the project background, see the [OpenWiki source note](../wiki/ai-engineering/context/openwiki.md)
and its [OpenWiki repository](https://github.com/langchain-ai/openwiki).

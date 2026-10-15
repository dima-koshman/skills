---
type: navigation concept
title: Quickstart
description: A compact task-routing map for the AI-agent ecosystem, model, development, security, and software-engineering foundations pages. Use it to choose a subject route, then follow the cross-cutting path and verify consequential conclusions against primary evidence.
tags: [navigation, quickstart, ai-engineering, software-engineering, architecture, operations]
verified:
  - by: openwiki/0.7.2
    at: 2026-10-11T10:13:45.493Z
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
generated: { by: "openwiki/0.7.2", at: "2026-10-11T10:13:45.493Z" }
---

# Quickstart

Use this page as a routing map, not as a subject encyclopedia. Start with the map
closest to the question, then follow the cross-cutting route for architecture,
concepts, workflows, integrations, operations, and evidence review.

## 1. Choose a subject route

### AI engineering

Begin with the [AI Engineering source map](../wiki/ai-engineering.md).
It is broader than agent execution and covers models and decision models, context,
tools and enterprise boundaries, agents and harnesses, development, observability
and evaluation, and security.

Use the synthesized pages according to the question:

- **Agent identity and coordination** — [Agent Ecosystem and Coordination](architecture/agent-ecosystem.md)
  maps agent roles, peer coordination, interoperability, and the operational
  differences among concrete coding agents.
- **Execution architecture** — [Agent Systems Architecture](architecture/agent-systems.md)
  follows the model loop, harness ownership, tools, context, state, limits,
  delegation, gateways, and termination.
- **Models and selection** — [Model Architecture and Selection](concepts/model-landscape.md)
  consolidates model architectures, decision models, providers, capabilities, and
  selection trade-offs.
- **Security and operations** — [Agent Security, Observability, and Evaluation](operations/security-and-observability.md)
  routes risks, controls, telemetry, tracing, and evaluation together.
- **AI-native delivery** — [AI-Native Development Workflow](workflows/ai-native-development.md)
  follows planning, implementation, review, testing, observability, and feedback,
  while keeping engineering accountability distinct from model assistance.

The source notes remain the authority for what was actually documented; synthesized
pages provide a navigable interpretation and pointers for further checking.

### Software engineering

Begin with the [Software Engineering source map](../wiki/software-engineering.md).
It remains distinct from model-specific AI notes and organizes general development
and distributed-systems concerns:

- **Architecture and change practice** — [Software Architecture and Development Practice](software-engineering/architecture-and-development.md)
  helps choose boundaries, communication styles, patterns, and change strategies.
- **Distributed-systems foundations** — [Distributed Systems Foundations and Designs](software-engineering/distributed-systems/foundations.md)
  is the reading route for consistency, replication, storage, coordination, and
  failure trade-offs.
- **Reliability and learning** — [Software Reliability and Learning Practice](software-engineering/reliability-and-learning.md)
  connects service objectives, toil, simplicity, observability, and structured
  learning.
- **Frontend boundary** — [HTMX and Server-Rendered Interactivity](software-engineering/frontend/htmx.md)
  covers HTML-driven browser interaction and its backend contract.

For source-level detail, the map also routes to Protocol Buffers and gRPC for
communication contracts, service meshes and plane separation for infrastructure,
and the learning materials under the software-engineering map.

## 2. Follow the cross-cutting route

After choosing a subject, use this sequence when a task crosses boundaries:

1. **Architecture and control flow** — start with [Agent Systems Architecture](architecture/agent-systems.md)
   for ownership, lifecycle, state, limits, delegation, effects, observations, and
   failure behavior; use [Software Architecture and Development Practice](software-engineering/architecture-and-development.md)
   for general component and change boundaries.
2. **Concepts and knowledge** — use [Context, Memory, and Knowledge Retrieval](concepts/context-and-knowledge.md)
   for working context, memory, RAG, MCP resources, and durable knowledge; use
   [Model Architecture and Selection](concepts/model-landscape.md) for model choice.
3. **Workflow and reusable capability** — use [AI-Native Development Workflow](workflows/ai-native-development.md)
   for the delivery lifecycle and [Agent Skills and Tooling](concepts/skills-and-tooling.md)
   for packaging, disclosure, invocation cost, scope, and trust.
4. **Integrations and service boundaries** — use [Model Providers and Agent Protocols](integrations/models-and-protocols.md)
   for providers, protocols, gateways, and harness boundaries; use [Distributed
   Systems Foundations and Designs](software-engineering/distributed-systems/foundations.md)
   for consistency, replication, coordination, storage, and failure trade-offs.
5. **Operations and risk** — use [Agent Security, Observability, and Evaluation](operations/security-and-observability.md)
   for agentic threats, guardrails, telemetry, tracing, and evaluation; use
   [Software Reliability and Learning Practice](software-engineering/reliability-and-learning.md)
   for objectives, toil, simplicity, and operational learning.
6. **Evidence and maintenance** — use [Knowledge Maintenance and Provenance](operations/maintenance-and-provenance.md)
   for snapshots, manifests, citations, freshness, version pins, source disagreement,
   and generated-page status.

## 3. Apply the notes safely

Generated summaries are subordinate to source notes and primary evidence. They are
not an application implementation, a substitute for current code, or proof that an
external source is correct. A source-note claim indicates what the note says; it
does not independently verify the underlying source. OpenWiki connectors create
deterministic raw snapshots and manifests before source-specific synthesis, so the
raw artifacts remain useful for provenance checks.

Use this loop:

1. Follow the subject and cross-cutting links above.
2. Read the synthesized page for terminology, ownership boundaries, lifecycle,
   trade-offs, and likely evidence locations.
3. Inspect the cited source notes, current code, focused tests, Git history, and
   runtime evidence before changing implementation or operations.
4. Return to [Knowledge Maintenance and Provenance](operations/maintenance-and-provenance.md)
   when freshness, provenance, source disagreement, generated-page status, or
   verification affects the decision.

A new synthesis or generation event does not make an old snapshot current. Preserve
source identity, capture time, manifest and configuration, review status, and stale
or superseded boundaries so readers can distinguish navigation material from
verified evidence.

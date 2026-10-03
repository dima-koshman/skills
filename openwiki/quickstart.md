---
type: navigation concept
title: Quickstart
description: Routes readers through the AI-engineering and software-engineering maps, then to synthesized architecture, concepts, integrations, operations, and systems guidance. Use it to choose an investigation path and to find the primary evidence that must be checked before implementation or operational decisions.
tags: [navigation, quickstart, ai-engineering, software-engineering, architecture, operations]
verified:
  - by: openwiki/0.7.0
    at: 2026-10-03T18:46:29.040Z
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
generated: { by: "openwiki/0.7.0", at: "2026-10-03T18:46:29.040Z" }
---

# Quickstart

Use this page as a task-routing map, not as a subject encyclopedia. Start with the
map closest to the question, then follow the cross-cutting route for boundaries,
control flow, operations, and evidence review.

## 1. Choose a subject map

### AI engineering

Start with the [AI Engineering map](../wiki/ai-engineering/ai-engineering.md),
the primary source-note map for this subject area. Its scope is broader than
agents alone:

- **Models and decisions** — LLM architecture and decision models such as Jev
  and CLM.
- **Context** — MCP, Open Knowledge Format, RAG, context engineering, and
  memory.
- **Tools and enterprise boundaries** — client/provider/frontend tools, the LLM
  gateway, and the MCP gateway.
- **Agents and execution** — agent architecture, peer agents, concrete agents,
  harnesses, subagents, and workflows.
- **Development** — the AI-native SDLC and observability-driven development.
- **Observability, evaluation, and security** — tracing, evaluations, agentic
  risks, guardrails, and masking.

Use the synthesized [Agent Systems Architecture](architecture/agent-systems.md)
when the task involves the model loop, harness ownership, tools, context, state,
limits, delegation, gateways, or termination. The synthesized page is a routing
and reasoning aid; the linked source notes remain the authority for what was
actually documented.

### Software engineering

Start with the [Software Engineering map](../wiki/software-engineering/development.md)
for general software-development and distributed-systems concerns, kept distinct
from model-specific AI notes. Route by the map's concern:

- **Learning** — [LabEx](../wiki/software-engineering/learning/labex.md) for practical
  exercises and [Linux Foundation Training](../wiki/software-engineering/learning/linux-foundation.md)
  for a structured Kubernetes introduction.
- **Reliability** — [SRE](../wiki/software-engineering/reliability/sre.md), including
  [toil](../wiki/software-engineering/reliability/toil.md) and
  [simplicity](../wiki/software-engineering/reliability/simplicity.md).
- **Communication** — [Protocol Buffers](../wiki/software-engineering/communication/protobuf.md)
  for schemas and wire contracts, then [gRPC](../wiki/software-engineering/communication/grpc.md)
  for the RPC layer built on them.
- **Frontend** — [htmx](../wiki/software-engineering/frontend/htmx.md) for
  interactivity in server-rendered HTML without a JavaScript framework.
- **Infrastructure** — [service meshes](../wiki/software-engineering/infrastructure/service-mesh.md)
  and [data, control, and management planes](../wiki/software-engineering/infrastructure/planes.md).

For a synthesized route through service boundaries and distributed failure
trade-offs, read [Distributed Communication and Service Infrastructure](software-engineering/distributed-systems.md),
then [Software Reliability and Learning Practice](software-engineering/reliability-and-learning.md).

## 2. Follow the cross-cutting route

Both subject maps meet at these generated pages:

1. **Architecture and control flow** — [Agent Systems Architecture](architecture/agent-systems.md)
   identifies ownership of decisions, run state, limits, delegation, effects,
   observations, and failures.
2. **Context and durable knowledge** — [Context, Memory, and Knowledge Retrieval](concepts/context-and-knowledge.md)
   distinguishes working context, memory, RAG, MCP resources, and durable wiki
   knowledge.
3. **Reusable capabilities** — [Agent Skills and Tooling](concepts/skills-and-tooling.md)
   covers packaging, progressive disclosure, invocation cost, scope, and trust.
4. **Providers and interoperability** — [Model Providers and Agent Protocols](integrations/models-and-protocols.md)
   covers provider boundaries, protocols, enterprise gateways, and the harness.
5. **Operations and risk** — [Agent Security, Observability, and Evaluation](operations/security-and-observability.md)
   connects threats and mitigations with runtime controls, telemetry, tracing,
   and evaluation.
6. **Service boundaries** — [Distributed Communication and Service Infrastructure](software-engineering/distributed-systems.md)
   covers contracts, RPC traffic, plane separation, mesh boundaries, and
   distributed failure modes.
7. **Maintenance and improvement** — [Knowledge Maintenance and Provenance](operations/maintenance-and-provenance.md)
   covers snapshots, manifests, citations, freshness, version pins, and the
   generated-page lifecycle; [Software Reliability and Learning Practice](software-engineering/reliability-and-learning.md)
   connects simplicity with observability-driven development and structured
   learning.

## 3. Apply the notes safely

Generated pages provide derived routing and context. They do not replace primary
source files, tests, Git history, or runtime checks. A source-note claim is an
indication of what a note says, not independent verification of the underlying
external source.

Use this loop:

1. Find the relevant subject and cross-cutting page through the routes above.
2. Read the generated page for terminology, ownership boundaries, lifecycle,
   trade-offs, and likely evidence locations.
3. Inspect the cited primary source, current code, focused tests, Git history,
   and runtime evidence before changing implementation or operations.
4. Return to [Knowledge Maintenance and Provenance](operations/maintenance-and-provenance.md)
   when freshness, provenance, source disagreement, generated-page status, or
   verification affects the decision.

The maintenance rule is simple: a new synthesis or generation event does not make
an old snapshot current. Preserve source identity, capture time, manifest and
configuration, review status, and stale or superseded boundaries so a later reader
can distinguish navigation material from evidence.

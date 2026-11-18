---
type: Knowledge Area
title: Software Engineering
description: Personal knowledge base for general software development and distributed-systems concepts.
tags:
- software-engineering
related:
- /ai-engineering.md
- /software-engineering/architecture/architectural-patterns.md
- /software-engineering/distributed-systems.md
- /software-engineering/learning.md
- /software-engineering/reliability/sre.md
- /software-engineering/reliability/toil.md
- /software-engineering/architecture/protobuf.md
- /software-engineering/architecture/grpc.md
- /software-engineering/frontend.md
- /software-engineering/infrastructure/service-mesh.md
- /software-engineering/infrastructure/planes.md
- /software-engineering/source-control.md
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-18T13:00:00+04:00'
topics:
- /software-engineering/architecture.md
- /software-engineering/distributed-systems.md
- /software-engineering/frontend.md
- /software-engineering/infrastructure.md
- /software-engineering/learning.md
- /software-engineering/planning.md
- /software-engineering/reliability.md
- /software-engineering/source-control.md
---

Concepts behind building and operating distributed systems, kept separate from
the model-specific material in the [AI engineering notes](/ai-engineering.md). Written for a
senior practitioner: design framing, trade-offs, and vetted primary sources —
not tutorials.

## Map

- **Architecture and communication** — [architectural patterns](/software-engineering/architecture/architectural-patterns.md)
  for component boundaries, communication styles, and trade-offs, with selected
  chapters from Architectural Metapatterns and complementary primary sources; and how services define contracts:
  [Protocol Buffers](/software-engineering/architecture/protobuf.md) for the wire format and schema,
  [gRPC](/software-engineering/architecture/grpc.md) for the RPC layer built on it.
- **Distributed systems** — [reading map](/software-engineering/distributed-systems.md)
  for Designing Data-Intensive Applications, Google File System, MapReduce,
  Bigtable, Dynamo, Raft, and Spanner, with publication versions, selected
  sections, and public download links; plus case studies of
  [TAO](/software-engineering/distributed-systems/tao.md),
  [OpenAI Habitat](/software-engineering/distributed-systems/openai-habitat.md) and
  [Cosmos DB partitioning](/software-engineering/distributed-systems/cosmos-db-partitioning.md).
- **Learning** — [LabEx](/software-engineering/learning.md#labex) for practical exercises and
  [Linux Foundation Training](/software-engineering/learning.md#linux-foundation-training) for a structured
  Kubernetes introduction.
- **Reliability** — [Site Reliability Engineering](/software-engineering/reliability/sre.md), Google's
  book on SLOs, error budgets, toil, and incident practice, with two chapters in
  depth: [toil](/software-engineering/reliability/toil.md) and [simplicity](/software-engineering/reliability/sre.md#simplicity).
- **Frontend** — [htmx](/software-engineering/frontend.md#htmx) for interactivity in server-rendered
  HTML without a JavaScript framework.
- **Infrastructure** — the layer around the services: the
  [service mesh](/software-engineering/infrastructure/service-mesh.md), and the
  [data, control, and management planes](/software-engineering/infrastructure/planes.md) that
  describe how such systems are decomposed, plus
  [OS CPU scheduling](/software-engineering/infrastructure/cpu-scheduling.md) and what makes
  [ports 22, 80 and 443](/software-engineering/infrastructure/network-ports.md) special.
- **Planning** — how work is shaped, sized and committed to:
  [Shape Up](/software-engineering/planning/shape-up.md)'s appetite (fixed time, variable scope)
  versus estimates, [shaping an idea into a pitch](/software-engineering/planning/shaping.md), and
  [responding to raw ideas](/software-engineering/planning/responding-to-raw-ideas.md).
- **Source control** — repository strategy:
  [monorepo vs polyrepo](/software-engineering/source-control.md#monorepo-vs-polyrepo), with
  Google's, Meta's and Anthropic's scaling stories and the case against.

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
- /software-engineering/learning/labex.md
- /software-engineering/learning/linux-foundation.md
- /software-engineering/reliability/sre.md
- /software-engineering/reliability/toil.md
- /software-engineering/reliability/simplicity.md
- /software-engineering/communication/protobuf.md
- /software-engineering/communication/grpc.md
- /software-engineering/frontend/htmx.md
- /software-engineering/infrastructure/service-mesh.md
- /software-engineering/infrastructure/planes.md
generated:
  by: codex/gpt-6
  at: '2026-10-15T15:23:06+04:00'
topics:
- /software-engineering/architecture.md
- /software-engineering/communication.md
- /software-engineering/distributed-systems.md
- /software-engineering/frontend.md
- /software-engineering/infrastructure.md
- /software-engineering/learning.md
- /software-engineering/reliability.md
---

Concepts behind building and operating distributed systems, kept separate from
the model-specific material in the [AI engineering notes](/ai-engineering.md). Written for a
senior practitioner: design framing, trade-offs, and vetted primary sources —
not tutorials.

## Map

- **Architecture** — [architectural patterns](/software-engineering/architecture/architectural-patterns.md)
  for component boundaries, communication styles, and trade-offs, with selected
  chapters from Architectural Metapatterns and complementary primary sources.
- **Distributed systems** — [reading map](/software-engineering/distributed-systems.md)
  for Designing Data-Intensive Applications, Google File System, MapReduce,
  Bigtable, Dynamo, Raft, and Spanner, with publication versions, selected
  sections, and public download links.
- **Learning** — [LabEx](/software-engineering/learning/labex.md) for practical exercises and
  [Linux Foundation Training](/software-engineering/learning/linux-foundation.md) for a structured
  Kubernetes introduction.
- **Reliability** — [Site Reliability Engineering](/software-engineering/reliability/sre.md), Google's
  book on SLOs, error budgets, toil, and incident practice, with two chapters in
  depth: [toil](/software-engineering/reliability/toil.md) and [simplicity](/software-engineering/reliability/simplicity.md).
- **Communication** — how services define contracts and talk to each other:
  [Protocol Buffers](/software-engineering/communication/protobuf.md) for the wire format and schema,
  [gRPC](/software-engineering/communication/grpc.md) for the RPC layer built on it.
- **Frontend** — [htmx](/software-engineering/frontend/htmx.md) for interactivity in server-rendered
  HTML without a JavaScript framework.
- **Infrastructure** — the layer around the services: the
  [service mesh](/software-engineering/infrastructure/service-mesh.md), and the
  [data, control, and management planes](/software-engineering/infrastructure/planes.md) that
  describe how such systems are decomposed.

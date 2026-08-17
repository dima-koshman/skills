---
type: Overview
title: Development
description: Personal knowledge base for general software development and distributed-systems concepts.
---

Concepts behind building and operating distributed systems, kept separate from
the model-specific material in the `okf-ai-engineering` bundle. Written for a
senior practitioner: design framing, trade-offs, and vetted primary sources —
not tutorials.

# Map

- **Communication** — how services define contracts and talk to each other:
  [Protocol Buffers](/communication/protobuf.md) for the wire format and schema,
  [gRPC](/communication/grpc.md) for the RPC layer built on it.
- **Infrastructure** — the layer around the services: the
  [service mesh](/infrastructure/service-mesh.md), and the
  [data, control, and management planes](/infrastructure/planes.md) that
  describe how such systems are decomposed.

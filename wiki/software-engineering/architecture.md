---
type: Knowledge Area
title: Architecture and Communication
description: "Component boundaries, communication styles and dependency trade-offs, and the service contracts that implement them: Protocol Buffers and gRPC."
tags:
- software-engineering
- architecture
parent: /software-engineering.md
topics:
- /software-engineering/architecture/architectural-patterns.md
- /software-engineering/architecture/grpc.md
- /software-engineering/architecture/protobuf.md
status: draft
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-18T12:00:00+04:00'
---

How a system is split into components and how they talk. [Architectural patterns](/software-engineering/architecture/architectural-patterns.md) cover the choices; [Protocol Buffers](/software-engineering/architecture/protobuf.md) and [gRPC](/software-engineering/architecture/grpc.md) are the concrete contracts for service-to-service calls.

## Topics

- [Architectural Patterns](/software-engineering/architecture/architectural-patterns.md) — Choose component boundaries, communication styles, and dependency directions according to the forces acting on a system.
- [gRPC](/software-engineering/architecture/grpc.md) — RPC framework using Protocol Buffers as its IDL to generate client and server stubs — a service-to-service alternative to REST.
- [Protocol Buffers](/software-engineering/architecture/protobuf.md) — Language-neutral binary serialization for small structured records — schema-first `.proto` definitions compiled into native bindings.

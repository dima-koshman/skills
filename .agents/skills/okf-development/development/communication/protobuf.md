---
type: Standard
title: Protocol Buffers
description: Language-neutral binary serialization for small structured records — schema-first `.proto` definitions compiled into native bindings.
resource: https://protobuf.dev
---

Protocol Buffers ("protobuf") are Google's mechanism for serializing structured
data across languages and platforms — in the project's own framing, "like JSON,
except it's smaller and faster, and it generates native language bindings." The
schema is the artifact: you declare messages in a `.proto` file, and the `protoc`
compiler emits accessors, serializers, and parsers for each target language at
build time. That generated code is what application code touches, so the schema
is enforced by the compiler rather than by convention or runtime validation.

The design property that matters most in practice is **schema evolution through
field numbers**. Each field carries a permanently assigned number that is written
on the wire instead of its name, and that number must never be reused. This buys
compatibility in both directions: old code reads new messages by ignoring
unrecognized fields, and new code reads old messages by applying defaults for
absent ones. Producers and consumers can therefore be deployed independently —
the property that makes protobuf viable as a service contract rather than merely
a wire encoding, and the foundation [gRPC](/communication/grpc.md) builds on.

The same field-number encoding is why messages are **not self-describing**: a
payload cannot be interpreted without its `.proto`. This is the central trade
against JSON. You gain compactness and parse speed and lose the ability to
inspect traffic with generic tooling — which pushes schema distribution (a
registry, a shared repo, or a build dependency) from a nicety to a requirement,
and makes debugging harder at exactly the boundaries a
[service mesh](/infrastructure/service-mesh.md) is watching.

Language support is direct from `protoc` for C++, C#, Java, Kotlin, Objective-C,
PHP, Python, and Ruby; Go and Dart come via plugins, and other languages exist as
third-party implementations. Beyond the long-standing proto2 and proto3 syntaxes,
the project is moving to **editions** (2023, 2024), which replace the
syntax-version split with per-feature settings so behavior can evolve without a
new syntax generation.

# When not to use it

The project documents its own limits, and they are worth respecting rather than
discovering: messages larger than a few megabytes, large multi-dimensional
floating-point arrays, non-object-oriented scientific languages, already
compressed data, and any context requiring a formal standards body. Add one
operational caveat from the spec — the same message can have many valid binary
encodings, so serialized bytes must never be compared, hashed, or signed as a
proxy for message equality.

# Resources

- [Protocol Buffers overview](https://protobuf.dev/overview/)
- [Language guide (editions)](https://protobuf.dev/programming-guides/editions/)
- [Encoding — the wire format](https://protobuf.dev/programming-guides/encoding/)

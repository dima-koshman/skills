---
type: Standard
title: gRPC
description: RPC framework using Protocol Buffers as its IDL to generate client and server stubs — a service-to-service alternative to REST.
resource: https://grpc.io
---

gRPC is a remote procedure call framework that uses
[Protocol Buffers](/communication/protobuf.md) as its interface definition
language: a `.proto` file declares both the payload messages *and* the service —
its methods, their request types, and their response types. From that single
definition, codegen produces a client **stub** and a server skeleton, so calling
a remote service is a typed method call in the caller's language and implementing
one is filling in an interface. The contract is compiler-checked on both sides,
which is the substantive difference from REST, where the contract lives in
documentation or an OpenAPI file that nothing forces the code to match.

Four call shapes fall out of the streaming model, all over HTTP/2:

| Type | Shape |
| --- | --- |
| Unary | One request, one response — the ordinary function call |
| Server streaming | One request, a stream of responses |
| Client streaming | A stream of requests, one response |
| Bidirectional streaming | Independent streams both ways, read and written in any order |

Bidirectional streaming is the capability with no clean REST equivalent, and
it is often the reason a service ends up on gRPC at all.

The framework also standardizes the operational concerns that REST leaves to each
team to reinvent. **Deadlines** are first-class — a client specifies how long it
will wait, the deadline propagates, and expiry surfaces as `DEADLINE_EXCEEDED`
rather than a hung connection. **Cancellation** lets either side end an RPC
immediately. **Channels** represent the connection to a server and carry
configuration such as compression. **Metadata** is the key-value sidecar for
call context like auth tokens. **Status codes** are a fixed enum, so failure
handling is uniform across every service instead of per-endpoint HTTP semantics.

# Trade-offs against REST

gRPC is optimized for service-to-service traffic and pays for it at the edges.
Browsers cannot speak it natively — that requires grpc-web plus a proxy — so
public and browser-facing APIs usually stay REST. The binary framing that makes
it efficient also makes it opaque to `curl`, generic log tooling, and casual
inspection. And the schema must be distributed to every consumer, which is a
build-and-release concern, not just a coding one.

Its shape aligns well with a [service mesh](/infrastructure/service-mesh.md):
because gRPC keeps long-lived HTTP/2 connections and multiplexes calls over them,
naive connection-level load balancing distributes badly, and request-level
balancing in the mesh's [data plane](/infrastructure/planes.md) is the standard
fix. Istio load-balances gRPC as a first-class protocol for this reason.

# Resources

- [gRPC core concepts](https://grpc.io/docs/what-is-grpc/core-concepts/)
- [Introduction to gRPC](https://grpc.io/docs/what-is-grpc/introduction/)
- [Status codes and their use](https://grpc.io/docs/guides/status-codes/)

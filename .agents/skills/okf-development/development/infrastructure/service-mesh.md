---
type: Technique
title: Service Mesh
description: A dedicated infrastructure layer handling service-to-service routing, security, reliability, and observability outside application code.
---

A service mesh is a distributed infrastructure layer that takes over the concerns
every service-to-service call shares — routing, security, reliability, traffic
policy, and observability — and moves them out of the application. The problems
are real whether or not you adopt a mesh; the question a mesh answers is *where
they live*. Without one, each service imports a library that does retries,
timeouts, mTLS, circuit breaking, and trace propagation, which means every
language in the fleet needs its own implementation and every policy change is a
redeploy of everything. A mesh relocates that logic into proxies alongside the
workloads, so it is configured once and applies uniformly, including to services
whose source you do not control.

Architecturally a mesh is the textbook
[data-plane/control-plane split](/infrastructure/planes.md): proxies carry the
actual request traffic, and a controller compiles operator intent into proxy
configuration and pushes it out.

# Istio

[Istio](https://istio.io) is the reference implementation and the clearest way to
see the shape. It "layers transparently onto existing distributed applications" —
transparently being the operative claim, since application code is unchanged.

- **Data plane** — in **sidecar mode**, an Envoy proxy runs in each pod and
  intercepts all of its traffic, giving full L7 control. In **ambient mode**, a
  per-node L4 proxy (`ztunnel`) handles identity and encryption, with optional
  per-namespace L7 proxies (*waypoints*) added only where richer policy is
  needed — materially less overhead when most workloads only need mTLS.
- **Control plane** — `istiod` watches the services and dynamically programs
  proxy behavior as rules and the environment change.

What that buys: automatic load balancing for HTTP, [gRPC](/communication/grpc.md),
WebSocket, and TCP, with fine-grained routing, retries, failover, and fault
injection; mutual TLS with identity-based authentication and authorization
between services; and automatic metrics, logs, and traces for all traffic
including cluster ingress and egress. The observability property is the one teams
most often underrate — it arrives without instrumenting a single service.

# Cost

A mesh is not free and is frequently adopted too early. Every call gains a proxy
hop and its latency; the control plane is another distributed system to operate,
upgrade, and debug; and failures acquire a new and unfamiliar layer to
investigate. The sidecar-versus-ambient choice is largely a bet on that cost —
comprehensive features against lighter per-node overhead. A mesh earns its place
at the point where the number of services, languages, or compliance requirements
makes per-service libraries the more expensive option.

# Resources

- [What is Istio?](https://istio.io/latest/docs/overview/what-is-istio/)
- [Istio ambient mode](https://istio.io/latest/docs/ambient/overview/)
- [Envoy proxy](https://www.envoyproxy.io/)
- [Linkerd](https://linkerd.io/) — a deliberately smaller alternative

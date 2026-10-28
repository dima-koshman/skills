---
type: Concept
title: Service Mesh
description: A dedicated infrastructure layer handling service-to-service routing, security, reliability,
  and observability outside application code.
tags:
- software-engineering
- infrastructure
parent: /software-engineering/infrastructure.md
related:
- /software-engineering/infrastructure/planes.md
- /software-engineering/communication/grpc.md
- /software-engineering/reliability/metastable-failures.md
- /ai-engineering/enterprise/llm-gateway.md
- /software-engineering/distributed-systems/openai-habitat.md
uses: /software-engineering/infrastructure/planes.md
implementation_example: Istio
data_plane_modes:
- sidecar
- ambient
sources:
- id: ref-1
  resource: https://istio.io
  title: Istio
- id: ref-2
  resource: https://istio.io/latest/docs/overview/what-is-istio/
  title: What is Istio?
- id: ref-3
  resource: https://istio.io/latest/docs/ambient/overview/
  title: Istio ambient mode
- id: ref-4
  resource: https://www.envoyproxy.io/
  title: Envoy proxy
- id: ref-5
  resource: https://linkerd.io/
  title: Linkerd
- id: istio-traffic
  resource: https://istio.io/latest/docs/concepts/traffic-management/
  title: Istio traffic management concepts (read 2026-10-16)
- id: envoy-circuit-breaking
  resource: https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/circuit_breaking
  title: Envoy circuit breaking (read 2026-10-16)
- id: envoy-adaptive-concurrency
  resource: https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/adaptive_concurrency_filter
  title: Envoy adaptive concurrency filter (read 2026-10-16)
- id: envoy-router
  resource: https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/router_filter
  title: Envoy router filter (read 2026-10-16)
- id: istio-ambient-start
  resource: https://istio.io/latest/docs/ambient/getting-started/
  title: Istio ambient mode getting started (Istio 1.31.2, read 2026-10-16)
- id: orbstack-k8s
  resource: https://docs.orbstack.dev/kubernetes/
  title: OrbStack Kubernetes docs (read 2026-10-16)
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-10-16T17:30:00+04:00'
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
[data-plane/control-plane split](/software-engineering/infrastructure/planes.md): proxies carry the
actual request traffic, and a controller compiles operator intent into proxy
configuration and pushes it out.

## Istio

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

What that buys: automatic load balancing for HTTP, [gRPC](/software-engineering/communication/grpc.md),
WebSocket, and TCP, with fine-grained routing, retries, failover, and fault
injection; mutual TLS with identity-based authentication and authorization
between services; and automatic metrics, logs, and traces for all traffic
including cluster ingress and egress. The observability property is the one teams
most often underrate — it arrives without instrumenting a single service.

## Resilience: what a mesh can and cannot own

A mesh is a good single place for the mechanical defenses against
[metastable failures](/software-engineering/reliability/metastable-failures.md), but not all of them.

| Defense | Mesh can own it | What stays in the application |
| --- | --- | --- |
| Timeouts | Yes, but Istio's HTTP timeout is off by default; set one explicitly[^istio-traffic] | Its own timeouts must be consistent with the mesh's |
| Retries | Yes. Istio retries HTTP twice by default; plain Envoy retries only when configured. Envoy recommends retry budgets so retry volume cannot explode[^istio-traffic][^envoy-router][^envoy-circuit-breaking] | Turn off library and SDK retries, or the layers multiply. Istio warns app and mesh policies "work independently, and therefore might conflict"[^istio-traffic] |
| Circuit breaking | Yes: connection, pending-request and retry limits per host or cluster[^envoy-circuit-breaking] | Fallback behavior when calls fail: applications "must handle the failure"[^istio-traffic] |
| Load shedding | Partly: Envoy's adaptive concurrency filter lowers the in-flight limit when latency rises above a measured baseline, at the cost of some 503s while it re-measures[^envoy-adaptive-concurrency] | Shedding based on what the proxy can't see: CPU, internal queues, request cost |
| Dropping doomed work | Partly: Envoy sends the remaining time budget upstream in `x-envoy-expected-rq-timeout-ms` and cancels requests that time out[^envoy-router] | The service must read the deadline and stop work on cancellation; otherwise it keeps computing for nobody |
| Prioritization, degradation, recover-friendly caching | No | Which requests matter more, what to serve degraded, read-through vs look-aside caching |

A mesh also helps when a service runs **many small processes**, as Python services often do. A proxy can
pool connections across them, upgrade HTTP/1 to HTTP/2 so many requests share one connection, and apply
rate limits and circuit breakers to the pod's total traffic instead of each process's slice. OpenAI's
Habitat used Envoy this way. See [OpenAI Habitat](/software-engineering/distributed-systems/openai-habitat.md).

So a mesh makes stable systems *easier* — one policy for every service, in every language — but not
automatic. Its main hazard is a hidden extra retry layer: adding Istio to services that already retry
adds two more attempts per call by default.

**For LLM traffic,** requests last seconds to minutes, stream, and vary a thousandfold in cost, so request
counts are a poor load measure. Token-based limits, budgets and model-level retries belong in an
[LLM gateway](/ai-engineering/enterprise/llm-gateway.md), which plays the mesh's role for model calls.

## Running it locally

On a laptop, ambient mode is the lighter choice: one `ztunnel` per node instead of an Envoy sidecar per
pod. L7 policies (retries, timeouts, fault injection) need a waypoint proxy for the
namespace.[^istio-ambient-start] OrbStack's single-node cluster works, with two CNI path flags on
`istioctl install`:[^orbstack-k8s]

```bash
istioctl install --set profile=ambient --skip-confirmation \
  --set values.cni.cniBinDir=/var/lib/rancher/k3s/data/current/bin/ \
  --set values.cni.cniConfDir=/var/lib/rancher/k3s/agent/etc/cni/net.d
kubectl label namespace default istio.io/dataplane-mode=ambient
istioctl waypoint apply -n default --enroll-namespace   # for L7 policy
```

Most clusters also need the Kubernetes Gateway API CRDs installed first.[^istio-ambient-start] OrbStack
makes Services reachable from the Mac directly, LoadBalancers under `*.k8s.orb.local`.[^orbstack-k8s]

## Cost

A mesh is not free and is frequently adopted too early. Every call gains a proxy
hop and its latency; the control plane is another distributed system to operate,
upgrade, and debug; and failures acquire a new and unfamiliar layer to
investigate. The sidecar-versus-ambient choice is largely a bet on that cost —
comprehensive features against lighter per-node overhead. A mesh earns its place
at the point where the number of services, languages, or compliance requirements
makes per-service libraries the more expensive option.

## Resources

- [What is Istio?](https://istio.io/latest/docs/overview/what-is-istio/)
- [Istio ambient mode](https://istio.io/latest/docs/ambient/overview/)
- [Envoy proxy](https://www.envoyproxy.io/)
- [Linkerd](https://linkerd.io/) — a deliberately smaller alternative

[^istio-traffic]: Istio traffic management concepts.
[^envoy-circuit-breaking]: Envoy docs, circuit breaking.
[^envoy-adaptive-concurrency]: Envoy docs, adaptive concurrency filter.
[^envoy-router]: Envoy docs, router filter.
[^istio-ambient-start]: Istio docs, ambient mode getting started.
[^orbstack-k8s]: OrbStack docs, Kubernetes.

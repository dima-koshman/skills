---
type: Reference
title: OpenAI Habitat
description: How OpenAI scaled its online storage layer to 70M+ requests per second for 1B+ weekly users — a library turned
  Python service turned Rust service with a deliberately narrow API in front of Azure Cosmos DB, and a round trip from
  shared to dedicated and back to shared database containers.
tags:
- software-engineering
- distributed-systems
- storage
- multi-tenancy
- python
parent: /software-engineering/distributed-systems.md
related:
- /software-engineering/distributed-systems/tao.md
- /software-engineering/distributed-systems/cosmos-db-partitioning.md
- /software-engineering/reliability/metastable-failures.md
- /software-engineering/infrastructure/service-mesh.md
- /software-engineering/distributed-systems/raft.md
publication: 'Jon Lee, Chaomin Yu, Ben Ries, Hrachya Hakobyan (OpenAI), **Rapidly scaling online storage to serve over 1
  billion ChatGPT users**, Parts I and II, OpenAI Engineering blog, 2026-09-11 and 2026-10-23.'
sources:
- id: part1
  resource: https://openai.com/index/scaling-storage-one-billion-users-part-one/
  title: Rapidly scaling online storage to serve over 1 billion ChatGPT users (Part I)
  author: Jon Lee, Chaomin Yu, Ben Ries
  last_modified: '2026-09-11T00:00:00Z'
- id: part2
  resource: https://openai.com/index/scaling-storage-one-billion-users-part-two/
  title: Rapidly scaling online storage to serve over 1 billion ChatGPT users (Part II)
  author: Jon Lee, Hrachya Hakobyan, Chaomin Yu
  last_modified: '2026-10-23T00:00:00Z'
- id: grpc-lb
  resource: https://grpc.io/blog/grpc-load-balancing/
  title: gRPC Load Balancing
  author: makdharma (Google)
  last_modified: '2017-06-15T00:00:00Z'
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-10-28T10:00:00+04:00'
verified:
- by: claude-code/claude-opus-5-5
  at: '2026-10-28T10:00:00+04:00'
---

Habitat is OpenAI's online storage platform: the layer every product (ChatGPT, API, Codex) calls to read and
write its data. It handles more than 70 million requests per second for over 1 billion weekly users across
almost 40 regions and serves more than 500 PB.[^part1] It sits in front of Azure Cosmos DB, an in-house
store, Valkey caches and blob storage, and handles routing, authorization, encryption, rate limiting,
caching and data residency so product engineers don't have to.[^part1]

The two posts are a case study in growing >10× a year for three years: "a series of tactical decisions and
sequencing", buying time for foundational work instead of building it all up front.[^part1] The stated
order of priorities: make it reliable, then fast, then cheap.[^part2]

## Timeline

| When | Shape | Why it changed |
| --- | --- | --- |
| DevDay 2023 | Python client library inside ChatGPT's server, one Cosmos DB database | Product engineers shouldn't manage databases[^part1] |
| Mid-2025 | Python service behind Envoy | Library changes needed days of coordinated rollouts across dozens of services; one team rolled back to a buggy client and caused the outage the change was meant to prevent[^part1] |
| Peak of Python | >20M RPS; second-largest service at OpenAI by core count | — |
| Q2 2026 | Rust rewrite by 2 engineers with Codex and GPT‑5.5; serves 95% of traffic | 6× less CPU, 15× less memory, lower average and tail latency[^part1] |
| 2026 | Global read p50 down from ~120 ms to ~10 ms | Replicating critical data near users, in-region caching, the Rust rewrite[^part2] |
| In development | In-house exabyte-scale store: Rockset's RocksDB Cloud core plus [Raft](/software-engineering/distributed-systems/raft.md) replication | Replicating bulky data more cheaply, at lower peak QPS[^part2] |

## Lessons

### Python first, Rust later — as a planned debt

The team knew Python would not survive 100× scale and called the Python service "a strategic incursion of
technical debt": the goal at the time was unblocking product teams and stabilizing the platform, not
efficiency.[^part1] They also bet that their own coding models would make the eventual rewrite cheap, and
say the bet paid off.[^part1]

Python's ">20M RPS" is not a free ride. They ran very many processes, each with low concurrency, and the
service became one of the biggest compute consumers in the company. The real lesson: Python can carry a
high-throughput proxy **if you pay for it in cores**, and that is a sensible trade only while developer
speed matters more than cost, with the rewrite planned from the start.

### Watch the event loop, not just CPU

Asyncio gives concurrency, not CPU parallelism. Habitat does CPU work on the request path (routing,
compression, encryption, checksums) and in background tasks (health checks, shadowing, hedging). In p99
traces, Cosmos DB answered fast but requests waited for their coroutine to get the CPU back.[^part1]

- **Measure loop lag.** Schedule a background task periodically and record how late it runs. They saw
  delays of hundreds of milliseconds, sometimes seconds.[^part1]
- **Keep per-process concurrency low and scale out processes** instead.[^part1]
- **Profile periodic work.** Statsig polled feature flags every minute without jitter and parsed a config
  holding every service's rules, so all 8 workers in a pod stalled at once. Fix: smaller config, longer
  interval, jitter.[^part1]

### Connection pools can cause metastable failures

aiohttp's `TCPConnector` reuses connections LIFO. After a burst, connections to *slow* server processes
come back to the pool last, so they get picked first, which sends more work to the processes that were
already struggling. Some processes saw 5–10× average concurrency and stayed degraded until restarted,
long after the bursty client stopped — a [metastable failure](/software-engineering/reliability/metastable-failures.md).
Capping connection lifetime limited it; FIFO reuse fixed it and also cut steady-state variance.[^part1]
Facebook hit the same loop in 2014 with TAO's MRU pool and congested network links.
Today they rely on Istio and Envoy for pooling and load-aware balancing.[^part1]

### Put fan-in in the proxy

Many small Python processes make thundering herds easy: deploys churn connections, and a connection leak
saturated a NAT gateway.[^part1] Envoy pools connections across processes, upgrades Python's HTTP/1 to
HTTP/2, extends connection lifetimes, and is where rate limits and circuit breakers live, because those are
"less effective in each standalone Python process" — each process only sees its own slice of traffic.[^part1]
Their example: 6 concurrent requests from 6 pods need 18 open connections direct, 6 through an Envoy
HTTP/1 pool, 1 over HTTP/2.[^part1]

HTTP/2 saves *connections*, not work: many requests share one connection as separate streams. The cost is
that a connection-level (L4) balancer forwards that whole connection to one backend; only an L7 balancer
spreads the streams.[^grpc-lb] See [Service Mesh](/software-engineering/infrastructure/service-mesh.md).

### A narrow API keeps load predictable

Habitat exposes a NoSQL API of client-defined **objects and edges**, inspired by
[TAO](/software-engineering/distributed-systems/tao.md). There are no arbitrary queries, no joins and no
traversals beyond an object's direct edges.[^part1] The aim is "simple, predictable, constant-work
requests"; requests with unpredictable fan-out "complicate isolation, load balancing, and introduce
latency cliffs".[^part1] On Postgres, one new expensive query on a hot path was a recurring cause of
outages, and reviewing every query stopped scaling with the org.[^part1]

An object and its edges live in one partition; the objects edges point to may be in another account in
another region, so traversals are slow by design.[^part1] Teams that need rich queries get an escape hatch:
change data capture (CDC) streams into a Rockset instance each team scales itself.[^part1]

The narrow API and the move to a service are separate decisions. The library already had a small set of
operations; the service was about central rollout, observability, and one chokepoint for access control
and audit.[^part1]

### Partitioning is not isolation

See [Cosmos DB partitioning](/software-engineering/distributed-systems/cosmos-db-partitioning.md) for the
mechanics. Three problems from Phase I, when all use cases shared one container per account:[^part2]

- **Shared logical keys.** Clients chose partition keys, so many products used `user_id` and shared that
  key's limits.
- **Noisy neighbors.** Limits are enforced per physical partition, which holds many logical keys, so a
  niche feature's load could break login and signup.
- **Weak partitions.** A container's throughput is split evenly across its physical partitions. Storage
  growth splits partitions without adding throughput, so each partition's share shrinks while traffic
  stays flat.

### Single-tenancy moves capacity planning to every team

Phase II gave critical use cases dedicated containers, plus a script that raised each container's
throughput as its partition count grew. Outages shrank from site-wide to single-feature.[^part2] But a
dedicated container loses **stable aggregate growth**: a launch going from 1K to 1M RU/s is 5% of a shared
container's headroom but 10,000% of a fresh 10K RU/s container's.[^part2] Every product team had to forecast
and pre-scale, many forgot, and launch days became SEVs.[^part2] "No lone, central team doing planning
resulted in many teams planning poorly."[^part2]

### Multi-tenancy needs explicit controls

Phase III went back to one shared container, with features built together with the Azure team:[^part2]

- **Hot-key throttling** — throttle the hottest keys first, so one key can't take a physical partition.
- **QoS priorities** — offline work (bulk inserts, extracts) is throttled before interactive traffic.
- **Improved serverless mode** — up to 10K RU/s per physical partition, and splits triggered by RU usage as
  well as storage. This removed manual throughput scaling.

They report no provisioning or noisy-neighbor incidents in the months since.[^part2]

### At this scale, "managed" means co-managed

Their largest Cosmos DB account holds tens of PB and serves >20M QPS. A late-2024 regional power outage
showed failover would take hours; failing back a month later caused a connection stampede on the original
region's gateway.[^part2] Now both teams share dashboards, test on a production-sized non-production account,
and can page each other directly.[^part2]

### Reads: place, replicate, cache

Over 90% of requests are reads.[^part2]

1. Store data near users where capacity allows; often it doesn't, and storage competes with serving compute
   for datacenter space and power.
2. Replicate only small, latency-critical datasets (such as auth metadata) widely, some to all 40 regions.
3. Cache everything else in Valkey near compute, and invalidate from Cosmos DB's change feed within
   seconds — the TAO approach, instead of choosing between short and long TTLs.[^part2]

[^part1]: OpenAI, Part I, 2026-09-11.
[^part2]: OpenAI, Part II, 2026-10-23.
[^grpc-lb]: gRPC blog, 2017-06-15: "With HTTP/2, LB can distribute the streams from one client among multiple backends" (L7); L4 copies the connection's frames to one backend.

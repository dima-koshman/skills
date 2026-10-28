---
type: Concept
title: Cosmos DB Partitioning
description: How Azure Cosmos DB maps many logical partitions (one per partition-key value) onto few physical
  partitions, why per-key limits are ceilings rather than guarantees, and why partitioning alone does not isolate tenants.
tags:
- software-engineering
- distributed-systems
- storage
- multi-tenancy
parent: /software-engineering/distributed-systems.md
related:
- /software-engineering/distributed-systems/openai-habitat.md
- /software-engineering/distributed-systems/dynamo.md
- /software-engineering/distributed-systems/bigtable.md
sources:
- id: partitioning
  resource: https://learn.microsoft.com/en-us/azure/cosmos-db/partitioning
  title: Partitioning and horizontal scaling in Azure Cosmos DB
  author: Microsoft
  last_modified: '2026-10-05T22:14:00Z'
- id: resource-model
  resource: https://learn.microsoft.com/en-us/azure/cosmos-db/resource-model
  title: Databases, containers, and items in Azure Cosmos DB
  author: Microsoft
  last_modified: '2026-08-25T17:18:00Z'
- id: habitat2
  resource: https://openai.com/index/scaling-storage-one-billion-users-part-two/
  title: Rapidly scaling online storage to serve over 1 billion ChatGPT users (Part II)
  author: Jon Lee, Hrachya Hakobyan, Chaomin Yu
  last_modified: '2026-10-23T00:00:00Z'
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-10-28T10:00:00+04:00'
verified:
- by: claude-code/claude-opus-5-5
  at: '2026-10-28T10:00:00+04:00'
stale_after: '2027-10-28T00:00:00+04:00'
---

## Account, database, container

| Level | What it is |
| --- | --- |
| **Account** | Has a DNS name, a set of regions and a default consistency level.[^resource-model] |
| **Database** | A namespace grouping containers. It can hold throughput shared by up to 25 containers.[^resource-model] |
| **Container** | Where data lives: a schema-agnostic set of items with one **partition key**, its own throughput (unless shared), indexing policy, TTL and change feed. It is a *collection* in the MongoDB API, a *table* in Cassandra and Table, a *graph* in Gremlin.[^resource-model] |
| **Item** | A document, row, or node/edge, unique by `id` within its logical partition.[^resource-model] |

So a container is roughly "a table", and it is also the unit you provision and scale. Throughput is in
**request units per second (RU/s)**, a normalized cost of reads, writes and queries.

## Logical vs physical partitions

- A **logical partition** is all items with the same partition-key value. There's no limit on how many
  exist. Each holds up to 20 GB and is the scope of transactions.[^partitioning]
- A **physical partition** is an internal, replicated server-side shard: up to 10,000 RU/s and 50 GB. One
  physical partition holds many logical partitions.[^partitioning]
- Keys are **hashed**, and the hash space is divided evenly across physical partitions. When throughput or
  storage grows, a physical partition **splits**. Every logical partition still stays whole on one
  physical partition.[^partitioning]
- The container's provisioned RU/s is **divided evenly** among its physical partitions.[^partitioning] With
  18,000 RU/s and 3 physical partitions, all keys on one partition share 6,000 RU/s.[^partitioning]

### Consequences

1. **The per-key limit is a ceiling, not a guarantee.** A key "can use 10K RU/s" only if nothing else on its
   physical partition is busy and the partition actually has 10K. In practice keys share the partition's
   budget.[^habitat2]
2. **Splits can lower per-partition throughput.** If storage growth splits partitions while provisioned
   RU/s stays the same, each partition gets a smaller share. OpenAI calls these **weak partitions**: limits
   fall below demand while traffic is flat.[^habitat2] This is a throughput budget, not a latency SLO.
3. **Noisy neighbors survive partitioning.** Unrelated keys hashed to the same physical partition share its
   budget. And if different products use the same key (`user_id`), they share even the logical
   partition.[^habitat2]

## Why logical and physical don't line up

The mismatch is by design:

- **Cardinality.** There are millions of keys and few physical partitions. One physical partition per key
  is far too much overhead, so many keys must share.
- **The unit of movement is a key range.** A split moves hash ranges, never part of a key. One hot key always
  lands on one partition, with whatever neighbors share it.
- **Placement ignores load.** Hashing spreads keys evenly by count, not by traffic. Hot keys come and go
  faster than any static mapping can follow.
- **Budget is set per container.** RU/s is set per container and split evenly, while the load sits on
  particular keys. Until OpenAI's custom serverless mode, splits were driven by storage, not by request
  load.[^habitat2]

The usual fixes either avoid sharing or control it:

| Approach | What you get | What it costs |
| --- | --- | --- |
| Better keys: high cardinality, synthetic or hierarchical keys[^partitioning] | Even spread | Depends on access patterns; keys are immutable |
| Dedicated containers (single-tenancy) | Own physical partitions per use case | Every team plans capacity; launches jump from 0 to 1M[^habitat2] |
| Shared container with controls: hot-key throttling, priority QoS, load-based splits[^habitat2] | Pooled headroom and central planning | Needs the database to support those controls |

[^partitioning]: Microsoft Learn, partitioning, updated 2026-10-05.
[^resource-model]: Microsoft Learn, resource model, updated 2026-08-25.
[^habitat2]: OpenAI, Habitat Part II, 2026-10-23.

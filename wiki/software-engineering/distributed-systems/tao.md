---
type: Reference
title: TAO
description: Facebook's read-optimized, geographically distributed graph store — a fixed objects-and-associations API
  served by a two-tier cache over sharded MySQL, replacing client-side memcache logic.
tags:
- software-engineering
- distributed-systems
- caching
parent: /software-engineering/distributed-systems.md
related:
- /software-engineering/distributed-systems/openai-habitat.md
- /software-engineering/reliability/metastable-failures.md
- /software-engineering/distributed-systems/bigtable.md
publication: 'Nathan Bronson and colleagues, **TAO: Facebook''s Distributed Data Store for the Social Graph**, USENIX ATC
  2013.'
sources:
- id: tao
  resource: https://www.usenix.org/system/files/conference/atc13/atc13-bronson.pdf
  title: 'TAO: Facebook''s Distributed Data Store for the Social Graph (PDF)'
  author: Nathan Bronson, Zach Amsden, George Cabrera, et al.
  last_modified: '2013-06-26T00:00:00Z'
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-10-28T10:00:00+04:00'
verified:
- by: claude-code/claude-opus-5-5
  at: '2026-10-28T10:00:00+04:00'
---

Reference: Nathan Bronson and colleagues,
**TAO: Facebook's Distributed Data Store for the Social Graph**, USENIX ATC 2013.

TAO serves Facebook's social graph through a small, fixed set of queries. It handled "a billion reads and
millions of writes each second", with a sampled workload of 99.8% reads.[^tao] Nathan Bronson, its first
author, later co-wrote the [metastable failures](/software-engineering/reliability/metastable-failures.md) paper.
TAO's own connection pool to MySQL caused one: a two-year network link imbalance described on that page.

## Key ideas

- **Objects and associations.** Objects are typed nodes; associations are typed, timestamped edges
  `(id1, atype, id2)`. Queries are fixed: get specific edges, count edges, page through an edge list by
  position or by time.[^tao]
- **Colocate an object with its outgoing edges.** An association lives on the shard of its `id1`, so each
  association query hits one server. The object at the other end usually lives elsewhere.[^tao]
- **The cache owns the logic.** Facebook started with MySQL plus memcache as a lookaside cache, with the
  caching logic in PHP client code. That made edge lists inefficient, made thundering herds hard to avoid
  ("control logic is run on clients that don't communicate with each other"), and made read-after-write
  consistency expensive. A fixed API let them move that logic into the cache service.[^tao]
- **Leaders and followers.** Clients talk to a nearby follower tier. Misses and writes go to the one leader
  for that shard, which serializes writes and protects the database from herds.[^tao]
- **Invalidations ride replication.** Invalidation and refill messages are embedded in the MySQL
  replication stream, so a region's caches are invalidated only after its replica has the new data.[^tao]
- **Availability over consistency.** TAO is eventually consistent, with read-after-write for clients that
  share a cache tier.[^tao]

## Compared with Habitat

[OpenAI Habitat](/software-engineering/distributed-systems/openai-habitat.md) cites TAO for two things: the
objects-and-edges API and CDC-driven cache invalidation. The paths are alike as well: both began as a
client-side abstraction and became a service once client-side logic proved too hard to change and control.

| | TAO (2013) | Habitat (2026) |
| --- | --- | --- |
| Data model | Objects and associations, fixed queries | Objects and edges, direct edges only |
| Store | Sharded MySQL | Azure Cosmos DB, in-house store |
| Cache | Write-through leader/follower tiers that implement the API | Lookaside Valkey cache near compute |
| Invalidation | Messages in the MySQL replication stream | Cosmos DB change feed |
| Edge lists | Range and time queries, counts | No traversal beyond direct edges |

## Read selectively

Read **§2 Background** for why lookaside caching failed them, **§4 Architecture** for sharding, tiers and
regions, and **§6 Production workload** for the read/write mix.

[^tao]: Bronson et al., USENIX ATC 2013.

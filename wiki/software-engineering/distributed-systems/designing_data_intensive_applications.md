---
type: Reference
title: Designing Data-Intensive Applications
description: Martin Kleppmann's guide to the trade-offs behind reliable storage and data processing.
tags:
- software-engineering
- distributed-systems
parent: /software-engineering/distributed-systems.md
related:
- /software-engineering/architecture/architectural-patterns.md
- /software-engineering/distributed-systems/dynamo.md
- /software-engineering/distributed-systems/raft.md
- /software-engineering/distributed-systems/spanner.md
- /software-engineering/distributed-systems/map_reduce.md
- /software-engineering/distributed-systems/bigtable.md
sources:
- id: ref-1
  resource: https://dataintensive.net/
  title: Author's book site
- id: ref-2
  resource: https://dataintensive.net/buy.html
  title: Ebook purchase and download options
generated:
  by: codex/gpt-6
  at: '2026-10-15T15:23:06+04:00'
---

The inspected copy is the **sixth early release, 2016-07-11**, with 491 PDF
pages. It predates the finished first edition; chapter numbering below follows
this draft. Its contents end with Stream Processing, so it should not be
treated as a complete current edition.

## Why read it

Use Designing Data-Intensive Applications to connect database internals with
application-visible behavior:
replication lag, concurrency, schema compatibility, partial failure, and
derived data. It complements the vocabulary in
[architectural patterns](/software-engineering/architecture/architectural-patterns.md) with the
mechanisms that make a design correct or fragile.

## Selected chapters in the inspected draft

| Chapter | Focus |
| --- | --- |
| 3 — Storage and Retrieval | Indexes, LSM-trees, B-trees, and analytical storage |
| 4 — Encoding and Evolution | Compatibility across schemas, services, and messages |
| 5–6 — Replication; Partitioning | Replica behavior, conflict handling, placement, and hot spots |
| 7 — Transactions | Isolation, lost updates, write skew, and serializability |
| 8 — The Trouble with Distributed Systems | Partial failure, timeouts, unreliable clocks, and process pauses |
| 9 — Consistency and Consensus | Linearizability, ordering, atomic commit, and consensus |
| 10–11 — Batch Processing; Stream Processing | Derived data, logs, CDC, and processing guarantees |

For backend and agent-platform design, start with chapters 8, 9, and 7. For
ingestion and analytics, start with 3, 10, and 11. These priorities are a
suggested reading route, not the book's prescribed order.

## Internet access

- [Author's book site](https://dataintensive.net/) — overview and publisher links.
- [Ebook purchase and download options](https://dataintensive.net/buy.html) — the author links to paid PDF/EPUB editions; this is not a free full-book download.

Related papers: [Dynamo](/software-engineering/distributed-systems/dynamo.md), [Raft](/software-engineering/distributed-systems/raft.md), [Spanner](/software-engineering/distributed-systems/spanner.md),
[MapReduce](/software-engineering/distributed-systems/map_reduce.md), and [Bigtable](/software-engineering/distributed-systems/bigtable.md).

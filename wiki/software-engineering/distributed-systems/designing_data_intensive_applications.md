# Designing Data-Intensive Applications

Martin Kleppmann's guide to the trade-offs behind reliable storage and data processing.

The inspected copy is the **sixth early release, 2016-07-11**, with 491 PDF
pages. It predates the finished first edition; chapter numbering below follows
this draft. Its contents end with Stream Processing, so it should not be
treated as a complete current edition.

## Why read it

Use Designing Data-Intensive Applications to connect database internals with
application-visible behavior:
replication lag, concurrency, schema compatibility, partial failure, and
derived data. It complements the vocabulary in
[architectural patterns](../architecture/architectural-patterns.md) with the
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

Related papers: [Dynamo](dynamo.md), [Raft](raft.md), [Spanner](spanner.md),
[MapReduce](map_reduce.md), and [Bigtable](bigtable.md).

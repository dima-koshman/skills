---
type: Knowledge Area
title: Distributed Systems
aliases:
- Designing Data-Intensive Applications
- Google File System
- MapReduce
- Bigtable
- Dynamo
- Raft
- Spanner
description: A reading map of classic papers and books on storage, replication, consensus and large-scale data processing,
  with notes on each, plus case studies of production storage systems.
tags:
- software-engineering
- distributed-systems
parent: /software-engineering.md
related:
- /software-engineering/architecture/architectural-patterns.md
- /software-engineering/reliability/sre.md
- /software-engineering/architecture/protobuf.md
- /software-engineering/infrastructure/planes.md
status: draft
sources:
- id: ref-1
  resource: https://dataintensive.net/
  title: Author's book site
- id: ref-2
  resource: https://dataintensive.net/buy.html
  title: Ebook purchase and download options
- id: google_file_system-ref-1
  resource: https://storage.googleapis.com/gweb-research2023-media/pubtools/4446.pdf
  title: Download paper (PDF, Google)
- id: google_file_system-ref-2
  resource: https://research.google/pubs/the-google-file-system/
  title: Publication page
- id: map_reduce-ref-1
  resource: https://storage.googleapis.com/gweb-research2023-media/pubtools/4449.pdf
  title: Download paper (PDF, Google)
- id: map_reduce-ref-2
  resource: https://research.google/pubs/mapreduce-simplified-data-processing-on-large-clusters/
  title: Publication page
- id: bigtable-ref-1
  resource: https://storage.googleapis.com/gweb-research2023-media/pubtools/4443.pdf
  title: Download paper (PDF, Google)
- id: bigtable-ref-2
  resource: https://research.google/pubs/bigtable-a-distributed-storage-system-for-structured-data/
  title: Publication page
- id: dynamo-ref-1
  resource: https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf
  title: Download paper (PDF, coauthor Werner Vogels)
- id: raft-ref-1
  resource: https://raft.github.io/raft.pdf
  title: Download extended paper (PDF, authors' site)
- id: raft-ref-2
  resource: https://raft.github.io/
  title: 'Raft project: visualizations, talks, and further papers'
- id: spanner-ref-1
  resource: https://research.google/pubs/spanner-googles-globally-distributed-database/
  title: 2013 journal article
- id: spanner-ref-2
  resource: https://www.usenix.org/system/files/conference/osdi12/osdi12-final-16.pdf
  title: Download OSDI 2012 conference paper (PDF, USENIX)
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-18T12:00:00+04:00'
topics:
- /software-engineering/distributed-systems/cosmos-db-partitioning.md
- /software-engineering/distributed-systems/openai-habitat.md
- /software-engineering/distributed-systems/tao.md
---

These sources explain the mechanisms behind the choices in
[architectural patterns](/software-engineering/architecture/architectural-patterns.md). They belong
to software engineering even when the resulting systems support AI workloads.
Each note links to a publisher or author download and identifies the relevant
publication version. Links checked: 2026-10-11.

## Reading map

| Source | Main question |
| --- | --- |
| [Designing Data-Intensive Applications](/software-engineering/distributed-systems.md#designing-data-intensive-applications) | How do storage and processing choices affect reliability and correctness? |
| [Google File System](/software-engineering/distributed-systems.md#google-file-system) | How should a filesystem handle large files and routine machine failures? |
| [MapReduce](/software-engineering/distributed-systems.md#mapreduce) | What can a batch-processing runtime automate? |
| [Bigtable](/software-engineering/distributed-systems.md#bigtable) | How do keys and data layout shape a distributed store? |
| [Dynamo](/software-engineering/distributed-systems.md#dynamo) | What happens when writes remain available during failures? |
| [Raft](/software-engineering/distributed-systems.md#raft) | How do replicas agree on a sequence of commands? |
| [Spanner](/software-engineering/distributed-systems.md#spanner) | How can geographically distributed transactions preserve external consistency? |
| [TAO](/software-engineering/distributed-systems/tao.md) | How does a fixed graph API let a cache tier own consistency and herd protection? |
| [OpenAI Habitat](/software-engineering/distributed-systems/openai-habitat.md) | How does a storage layer survive >10× yearly growth, and when is multi-tenancy worth it? |
| [Cosmos DB Partitioning](/software-engineering/distributed-systems/cosmos-db-partitioning.md) | Why don't logical partitions get the limits and isolation they seem to promise? |

## Suggested route

Start with the failure and consistency chapters in Designing Data-Intensive
Applications. Then compare Dynamo with Raft, followed by Spanner. For
data-engineering work, read Google File System, MapReduce, and Bigtable together
to see how storage and computation fit together. For online serving at scale,
read TAO, then OpenAI Habitat, which borrows TAO's data model and cache
invalidation.

Treat the papers as historical designs with explicit workload assumptions.
Their implementation details and measurements describe the published systems;
they do not establish the behavior of current managed products.

Related notes: [SRE](/software-engineering/reliability/sre.md),
[simplicity](/software-engineering/reliability/sre.md#simplicity), and
[Protocol Buffers](/software-engineering/architecture/protobuf.md).

## Paper notes

Short notes on each classic source: the key ideas and which sections to read first.

### Designing Data-Intensive Applications

Martin Kleppmann's guide to the trade-offs behind reliable storage and data processing.

The inspected copy is the **sixth early release, 2016-07-11**, with 491 PDF
pages. It predates the finished first edition; chapter numbering below follows
this draft. Its contents end with Stream Processing, so it should not be
treated as a complete current edition.

#### Why read it

Use Designing Data-Intensive Applications to connect database internals with
application-visible behavior:
replication lag, concurrency, schema compatibility, partial failure, and
derived data. It complements the vocabulary in
[architectural patterns](/software-engineering/architecture/architectural-patterns.md) with the
mechanisms that make a design correct or fragile.

#### Selected chapters in the inspected draft

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

#### Internet access

- [Author's book site](https://dataintensive.net/) — overview and publisher links.
- [Ebook purchase and download options](https://dataintensive.net/buy.html) — the author links to paid PDF/EPUB editions; this is not a free full-book download.

Related papers: [Dynamo](/software-engineering/distributed-systems.md#dynamo), [Raft](/software-engineering/distributed-systems.md#raft), [Spanner](/software-engineering/distributed-systems.md#spanner),
[MapReduce](/software-engineering/distributed-systems.md#mapreduce), and [Bigtable](/software-engineering/distributed-systems.md#bigtable).

### Google File System

A filesystem designed around large data workloads and routine hardware failure.

**Publication:** Sanjay Ghemawat, Howard Gobioff, and Shun-Tak Leung, **The Google File System**, SOSP 2003.

Reference: Sanjay Ghemawat, Howard Gobioff, and Shun-Tak Leung,
**The Google File System**, SOSP 2003.

#### Key ideas

- A master owns metadata; chunkservers store replicated file chunks. Clients
  obtain locations from the master and transfer data directly to chunkservers.
- Large chunks and an append-heavy workload shape the design. It is not a
  general-purpose POSIX filesystem with familiar consistency in every case.
- Leases coordinate mutation order. Record append can produce duplicates,
  leaving applications responsible for handling them.

#### Read selectively

Read **Design Overview**, especially the consistency model, then
**System Interactions** and **Fault Tolerance and Diagnosis**.
Ask which guarantees belong to storage and which remain application work.

Compare the metadata/data split with
[control and data planes](/software-engineering/infrastructure/planes.md), then read
[MapReduce](/software-engineering/distributed-systems.md#mapreduce) and [Bigtable](/software-engineering/distributed-systems.md#bigtable).

#### Resources

- [Download paper (PDF, Google)](https://storage.googleapis.com/gweb-research2023-media/pubtools/4446.pdf)
- [Publication page](https://research.google/pubs/the-google-file-system/)

### MapReduce

A programming model and runtime for fault-tolerant parallel batch processing.

**Publication:** Jeffrey Dean and Sanjay Ghemawat, **MapReduce: Simplified Data Processing on Large Clusters**, OSDI 2004.

Reference: Jeffrey Dean and Sanjay Ghemawat,
**MapReduce: Simplified Data Processing on Large Clusters**, OSDI 2004.

#### Key ideas

- Map emits intermediate key/value pairs; shuffle groups values by key; reduce
  processes each group.
- The runtime owns input partitioning, scheduling, communication, and worker
  failure recovery. Data locality reduces network traffic.
- Backup tasks address slow workers. Re-execution makes side effects and
  determinism important parts of the processing contract.

#### Read selectively

Start with **Programming Model** and **Implementation**, particularly fault
tolerance, locality, and backup tasks. Read the side-effects discussion before
assuming that retrying a task is harmless.

For ingestion design, ask whether stages can be replayed safely and what state
must survive a worker failure. Compare with [Google File System](/software-engineering/distributed-systems.md#google-file-system)
and the [batch and stream processing chapters](/software-engineering/distributed-systems.md#designing-data-intensive-applications)
in Designing Data-Intensive Applications.

#### Resources

- [Download paper (PDF, Google)](https://storage.googleapis.com/gweb-research2023-media/pubtools/4449.pdf)
- [Publication page](https://research.google/pubs/mapreduce-simplified-data-processing-on-large-clusters/)

### Bigtable

A distributed sorted store whose data layout is part of the application design.

**Publication:** Fay Chang and colleagues, **Bigtable: A Distributed Storage System for Structured Data**, OSDI 2006.

Reference: Fay Chang and colleagues,
**Bigtable: A Distributed Storage System for Structured Data**, OSDI 2006.

#### Key ideas

- The data model is a sparse sorted map indexed by row, column, and timestamp.
  Row-key choices determine locality and range-scan behavior.
- Tablets partition row ranges. Column families organize related columns;
  operations on one row are atomic.
- Google File System provides persistent storage, while Chubby supplies coordination.
  Memtables, SSTables, and compaction support the storage engine.

#### Read selectively

Start with **Data Model**, **Building Blocks**, and **Implementation**, then
**Lessons**. Pay attention to how workload and key design affect distribution
and operational complexity.

Compare [Google File System](/software-engineering/distributed-systems.md#google-file-system) for the storage substrate,
[Dynamo](/software-engineering/distributed-systems.md#dynamo) for a
different partitioning and consistency approach, and [Spanner](/software-engineering/distributed-systems.md#spanner) for
distributed transactions.

#### Resources

- [Download paper (PDF, Google)](https://storage.googleapis.com/gweb-research2023-media/pubtools/4443.pdf)
- [Publication page](https://research.google/pubs/bigtable-a-distributed-storage-system-for-structured-data/)

### Dynamo

An availability-oriented key-value store that exposes conflict resolution to applications.

**Publication:** Giuseppe DeCandia and colleagues, **Dynamo: Amazon's Highly Available Key-value Store**, SOSP 2007.

Reference: Giuseppe DeCandia and colleagues,
**Dynamo: Amazon's Highly Available Key-value Store**, SOSP 2007.

#### Key ideas

- Consistent hashing partitions and replicates keys across nodes.
- Vector clocks track versions; reads may expose concurrent versions for
  application-assisted reconciliation.
- Sloppy quorums and hinted handoff support availability during temporary
  failures. Merkle trees support background replica repair.

#### Read selectively

Read **System Architecture**, especially versioning and failure handling,
then **Experiences and Lessons Learned**. Ask what the application must do when
a write succeeds but replicas disagree.

Compare with [Raft](/software-engineering/distributed-systems.md#raft) and [Spanner](/software-engineering/distributed-systems.md#spanner): they solve different
agreement and transaction problems. This note describes the 2007 Dynamo
design; use separate documentation for current DynamoDB guarantees.

#### Resources

- [Download paper (PDF, coauthor Werner Vogels)](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf)

### Raft

Consensus for a replicated log, organized around leader election, replication, and safety.

**Publication:** Diego Ongaro and John Ousterhout, **In Search of an Understandable Consensus Algorithm (Extended Version)**, May 20, 2014. The inspected copy is the 18-page extended paper.

Reference: Diego Ongaro and John Ousterhout,
**In Search of an Understandable Consensus Algorithm (Extended Version)**,
May 20, 2014. The inspected copy is the 18-page extended paper.

#### Key ideas

- A leader orders log entries; terms and voting rules constrain elections.
- Commitment and election restrictions preserve the history applied by
  replicated state machines.
- Availability requires a communicating majority. Losing that majority can
  stop progress while safety remains intact.

#### Read selectively

Start with **Replicated State Machines**, Figure 2, and **The Raft Consensus
Algorithm**, especially safety. Then read **Client Interaction**: agreement
on a log does not by itself remove duplicate client requests.

Use [Dynamo](/software-engineering/distributed-systems.md#dynamo) to contrast conflict-tolerant replication and
[Spanner](/software-engineering/distributed-systems.md#spanner) to distinguish consensus from distributed transaction
coordination. The Spanner paper uses Paxos, not Raft.

#### Resources

- [Download extended paper (PDF, authors' site)](https://raft.github.io/raft.pdf)
- [Raft project: visualizations, talks, and further papers](https://raft.github.io/)

### Spanner

A globally replicated database combining transactions with explicit clock uncertainty.

**Publication:** James C. Corbett and colleagues, **Spanner: Google's Globally Distributed Database**, ACM TOCS 31(3), Article 8, August 2013. The inspected copy is this 22-page journal article.

Reference: James C. Corbett and colleagues,
**Spanner: Google's Globally Distributed Database**, ACM TOCS 31(3),
Article 8, August 2013. The inspected copy is this 22-page journal article.

#### Key ideas

- Paxos groups provide synchronous replication; transactions can span groups.
- TrueTime exposes a bounded time interval. Commit-wait uses that uncertainty
  to support externally consistent transaction ordering.
- Snapshot reads and multiversion storage separate some read work from
  concurrent updates. These guarantees depend on the system's stated assumptions.

#### Read selectively

Read **TrueTime**, **Concurrency Control**, and **Evaluation**. Compare the
cost of waiting and coordination with [Dynamo](/software-engineering/distributed-systems.md#dynamo), then use
[Raft](/software-engineering/distributed-systems.md#raft) to review the underlying consensus problem.

#### Resources

- [2013 journal article](https://research.google/pubs/spanner-googles-globally-distributed-database/)
- [Download OSDI 2012 conference paper (PDF, USENIX)](https://www.usenix.org/system/files/conference/osdi12/osdi12-final-16.pdf) — an earlier version, distinct from the inspected journal copy.

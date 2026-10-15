---
type: Knowledge Area
title: Distributed Systems
description: Reading notes on storage, replication, consensus, and large-scale data processing.
tags:
- software-engineering
parent: /software-engineering.md
related:
- /software-engineering/architecture/architectural-patterns.md
- /software-engineering/distributed-systems/designing_data_intensive_applications.md
- /software-engineering/distributed-systems/google_file_system.md
- /software-engineering/distributed-systems/map_reduce.md
- /software-engineering/distributed-systems/bigtable.md
- /software-engineering/distributed-systems/dynamo.md
- /software-engineering/distributed-systems/raft.md
- /software-engineering/distributed-systems/spanner.md
- /software-engineering/reliability/sre.md
- /software-engineering/reliability/simplicity.md
- /software-engineering/communication/protobuf.md
generated:
  by: codex/gpt-6
  at: '2026-10-15T15:23:06+04:00'
topics:
- /software-engineering/distributed-systems/bigtable.md
- /software-engineering/distributed-systems/designing_data_intensive_applications.md
- /software-engineering/distributed-systems/dynamo.md
- /software-engineering/distributed-systems/google_file_system.md
- /software-engineering/distributed-systems/map_reduce.md
- /software-engineering/distributed-systems/raft.md
- /software-engineering/distributed-systems/spanner.md
---

These sources explain the mechanisms behind the choices in
[architectural patterns](/software-engineering/architecture/architectural-patterns.md). They belong
to software engineering even when the resulting systems support AI workloads.
Each note links to a publisher or author download and identifies the relevant
publication version. Links checked: 2026-10-11.

## Reading map

| Source | Main question |
| --- | --- |
| [Designing Data-Intensive Applications](/software-engineering/distributed-systems/designing_data_intensive_applications.md) | How do storage and processing choices affect reliability and correctness? |
| [Google File System](/software-engineering/distributed-systems/google_file_system.md) | How should a filesystem handle large files and routine machine failures? |
| [MapReduce](/software-engineering/distributed-systems/map_reduce.md) | What can a batch-processing runtime automate? |
| [Bigtable](/software-engineering/distributed-systems/bigtable.md) | How do keys and data layout shape a distributed store? |
| [Dynamo](/software-engineering/distributed-systems/dynamo.md) | What happens when writes remain available during failures? |
| [Raft](/software-engineering/distributed-systems/raft.md) | How do replicas agree on a sequence of commands? |
| [Spanner](/software-engineering/distributed-systems/spanner.md) | How can geographically distributed transactions preserve external consistency? |

## Suggested route

Start with the failure and consistency chapters in Designing Data-Intensive
Applications. Then compare Dynamo with Raft, followed by Spanner. For
data-engineering work, read Google File System, MapReduce, and Bigtable together
to see how storage and computation fit together.

Treat the papers as historical designs with explicit workload assumptions.
Their implementation details and measurements describe the published systems;
they do not establish the behavior of current managed products.

Related notes: [SRE](/software-engineering/reliability/sre.md),
[simplicity](/software-engineering/reliability/simplicity.md), and
[Protocol Buffers](/software-engineering/communication/protobuf.md).

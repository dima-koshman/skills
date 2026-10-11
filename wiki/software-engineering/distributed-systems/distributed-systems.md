# Distributed Systems

Reading notes on storage, replication, consensus, and large-scale data processing.

These sources explain the mechanisms behind the choices in
[architectural patterns](../architecture/architectural-patterns.md). They belong
to software engineering even when the resulting systems support AI workloads.
Each note links to a publisher or author download and identifies the relevant
publication version. Links checked: 2026-10-11.

## Reading map

| Source | Main question |
| --- | --- |
| [Designing Data-Intensive Applications](designing_data_intensive_applications.md) | How do storage and processing choices affect reliability and correctness? |
| [Google File System](google_file_system.md) | How should a filesystem handle large files and routine machine failures? |
| [MapReduce](map_reduce.md) | What can a batch-processing runtime automate? |
| [Bigtable](bigtable.md) | How do keys and data layout shape a distributed store? |
| [Dynamo](dynamo.md) | What happens when writes remain available during failures? |
| [Raft](raft.md) | How do replicas agree on a sequence of commands? |
| [Spanner](spanner.md) | How can geographically distributed transactions preserve external consistency? |

## Suggested route

Start with the failure and consistency chapters in Designing Data-Intensive
Applications. Then compare Dynamo with Raft, followed by Spanner. For
data-engineering work, read Google File System, MapReduce, and Bigtable together
to see how storage and computation fit together.

Treat the papers as historical designs with explicit workload assumptions.
Their implementation details and measurements describe the published systems;
they do not establish the behavior of current managed products.

Related notes: [SRE](../reliability/sre.md),
[simplicity](../reliability/simplicity.md), and
[Protocol Buffers](../communication/protobuf.md).

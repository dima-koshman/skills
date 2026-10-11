# Bigtable

A distributed sorted store whose data layout is part of the application design.

Reference: Fay Chang and colleagues,
**Bigtable: A Distributed Storage System for Structured Data**, OSDI 2006.

## Key ideas

- The data model is a sparse sorted map indexed by row, column, and timestamp.
  Row-key choices determine locality and range-scan behavior.
- Tablets partition row ranges. Column families organize related columns;
  operations on one row are atomic.
- Google File System provides persistent storage, while Chubby supplies coordination.
  Memtables, SSTables, and compaction support the storage engine.

## Read selectively

Start with **Data Model**, **Building Blocks**, and **Implementation**, then
**Lessons**. Pay attention to how workload and key design affect distribution
and operational complexity.

Compare [Google File System](google_file_system.md) for the storage substrate,
[Dynamo](dynamo.md) for a
different partitioning and consistency approach, and [Spanner](spanner.md) for
distributed transactions.

## Resources

- [Download paper (PDF, Google)](https://storage.googleapis.com/gweb-research2023-media/pubtools/4443.pdf)
- [Publication page](https://research.google/pubs/bigtable-a-distributed-storage-system-for-structured-data/)

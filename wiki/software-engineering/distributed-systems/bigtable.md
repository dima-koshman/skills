---
type: Reference
title: Bigtable
description: A distributed sorted store whose data layout is part of the application design.
tags:
- software-engineering
- distributed-systems
parent: /software-engineering/distributed-systems.md
related:
- /software-engineering/distributed-systems/google_file_system.md
- /software-engineering/distributed-systems/dynamo.md
- /software-engineering/distributed-systems/spanner.md
publication: 'Fay Chang and colleagues, **Bigtable: A Distributed Storage System for Structured Data**,
  OSDI 2006.'
sources:
- id: ref-1
  resource: https://storage.googleapis.com/gweb-research2023-media/pubtools/4443.pdf
  title: Download paper (PDF, Google)
- id: ref-2
  resource: https://research.google/pubs/bigtable-a-distributed-storage-system-for-structured-data/
  title: Publication page
generated:
  by: codex/gpt-6
  at: '2026-10-15T15:23:06+04:00'
---

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

Compare [Google File System](/software-engineering/distributed-systems/google_file_system.md) for the storage substrate,
[Dynamo](/software-engineering/distributed-systems/dynamo.md) for a
different partitioning and consistency approach, and [Spanner](/software-engineering/distributed-systems/spanner.md) for
distributed transactions.

## Resources

- [Download paper (PDF, Google)](https://storage.googleapis.com/gweb-research2023-media/pubtools/4443.pdf)
- [Publication page](https://research.google/pubs/bigtable-a-distributed-storage-system-for-structured-data/)

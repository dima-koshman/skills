---
type: Reference
title: MapReduce
description: A programming model and runtime for fault-tolerant parallel batch processing.
tags:
- software-engineering
- distributed-systems
parent: /software-engineering/distributed-systems.md
related:
- /software-engineering/distributed-systems/google_file_system.md
- /software-engineering/distributed-systems/designing_data_intensive_applications.md
publication: 'Jeffrey Dean and Sanjay Ghemawat, **MapReduce: Simplified Data Processing on Large Clusters**,
  OSDI 2004.'
sources:
- id: ref-1
  resource: https://storage.googleapis.com/gweb-research2023-media/pubtools/4449.pdf
  title: Download paper (PDF, Google)
- id: ref-2
  resource: https://research.google/pubs/mapreduce-simplified-data-processing-on-large-clusters/
  title: Publication page
generated:
  by: codex/gpt-6
  at: '2026-10-15T15:23:06+04:00'
---

Reference: Jeffrey Dean and Sanjay Ghemawat,
**MapReduce: Simplified Data Processing on Large Clusters**, OSDI 2004.

## Key ideas

- Map emits intermediate key/value pairs; shuffle groups values by key; reduce
  processes each group.
- The runtime owns input partitioning, scheduling, communication, and worker
  failure recovery. Data locality reduces network traffic.
- Backup tasks address slow workers. Re-execution makes side effects and
  determinism important parts of the processing contract.

## Read selectively

Start with **Programming Model** and **Implementation**, particularly fault
tolerance, locality, and backup tasks. Read the side-effects discussion before
assuming that retrying a task is harmless.

For ingestion design, ask whether stages can be replayed safely and what state
must survive a worker failure. Compare with [Google File System](/software-engineering/distributed-systems/google_file_system.md)
and the [batch and stream processing chapters](/software-engineering/distributed-systems/designing_data_intensive_applications.md)
in Designing Data-Intensive Applications.

## Resources

- [Download paper (PDF, Google)](https://storage.googleapis.com/gweb-research2023-media/pubtools/4449.pdf)
- [Publication page](https://research.google/pubs/mapreduce-simplified-data-processing-on-large-clusters/)

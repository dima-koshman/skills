---
type: Reference
title: Google File System
description: A filesystem designed around large data workloads and routine hardware failure.
tags:
- software-engineering
- distributed-systems
parent: /software-engineering/distributed-systems.md
related:
- /software-engineering/infrastructure/planes.md
- /software-engineering/distributed-systems/map_reduce.md
- /software-engineering/distributed-systems/bigtable.md
publication: Sanjay Ghemawat, Howard Gobioff, and Shun-Tak Leung, **The Google File System**, SOSP 2003.
sources:
- id: ref-1
  resource: https://storage.googleapis.com/gweb-research2023-media/pubtools/4446.pdf
  title: Download paper (PDF, Google)
- id: ref-2
  resource: https://research.google/pubs/the-google-file-system/
  title: Publication page
generated:
  by: codex/gpt-6
  at: '2026-10-15T15:23:06+04:00'
---

Reference: Sanjay Ghemawat, Howard Gobioff, and Shun-Tak Leung,
**The Google File System**, SOSP 2003.

## Key ideas

- A master owns metadata; chunkservers store replicated file chunks. Clients
  obtain locations from the master and transfer data directly to chunkservers.
- Large chunks and an append-heavy workload shape the design. It is not a
  general-purpose POSIX filesystem with familiar consistency in every case.
- Leases coordinate mutation order. Record append can produce duplicates,
  leaving applications responsible for handling them.

## Read selectively

Read **Design Overview**, especially the consistency model, then
**System Interactions** and **Fault Tolerance and Diagnosis**.
Ask which guarantees belong to storage and which remain application work.

Compare the metadata/data split with
[control and data planes](/software-engineering/infrastructure/planes.md), then read
[MapReduce](/software-engineering/distributed-systems/map_reduce.md) and [Bigtable](/software-engineering/distributed-systems/bigtable.md).

## Resources

- [Download paper (PDF, Google)](https://storage.googleapis.com/gweb-research2023-media/pubtools/4446.pdf)
- [Publication page](https://research.google/pubs/the-google-file-system/)

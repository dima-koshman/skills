# Google File System

A filesystem designed around large data workloads and routine hardware failure.

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
[control and data planes](../infrastructure/planes.md), then read
[MapReduce](map_reduce.md) and [Bigtable](bigtable.md).

## Resources

- [Download paper (PDF, Google)](https://storage.googleapis.com/gweb-research2023-media/pubtools/4446.pdf)
- [Publication page](https://research.google/pubs/the-google-file-system/)

# MapReduce

A programming model and runtime for fault-tolerant parallel batch processing.

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
must survive a worker failure. Compare with [Google File System](google_file_system.md)
and the [batch and stream processing chapters](designing_data_intensive_applications.md)
in Designing Data-Intensive Applications.

## Resources

- [Download paper (PDF, Google)](https://storage.googleapis.com/gweb-research2023-media/pubtools/4449.pdf)
- [Publication page](https://research.google/pubs/mapreduce-simplified-data-processing-on-large-clusters/)

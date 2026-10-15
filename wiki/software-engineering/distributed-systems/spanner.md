---
type: Reference
title: Spanner
description: A globally replicated database combining transactions with explicit clock uncertainty.
tags:
- software-engineering
- distributed-systems
parent: /software-engineering/distributed-systems.md
related:
- /software-engineering/distributed-systems/dynamo.md
- /software-engineering/distributed-systems/raft.md
publication: 'James C. Corbett and colleagues, **Spanner: Google''s Globally Distributed Database**, ACM
  TOCS 31(3), Article 8, August 2013. The inspected copy is this 22-page journal article.'
sources:
- id: ref-1
  resource: https://research.google/pubs/spanner-googles-globally-distributed-database/
  title: 2013 journal article
- id: ref-2
  resource: https://www.usenix.org/system/files/conference/osdi12/osdi12-final-16.pdf
  title: Download OSDI 2012 conference paper (PDF, USENIX)
generated:
  by: codex/gpt-6
  at: '2026-10-15T15:23:06+04:00'
---

Reference: James C. Corbett and colleagues,
**Spanner: Google's Globally Distributed Database**, ACM TOCS 31(3),
Article 8, August 2013. The inspected copy is this 22-page journal article.

## Key ideas

- Paxos groups provide synchronous replication; transactions can span groups.
- TrueTime exposes a bounded time interval. Commit-wait uses that uncertainty
  to support externally consistent transaction ordering.
- Snapshot reads and multiversion storage separate some read work from
  concurrent updates. These guarantees depend on the system's stated assumptions.

## Read selectively

Read **TrueTime**, **Concurrency Control**, and **Evaluation**. Compare the
cost of waiting and coordination with [Dynamo](/software-engineering/distributed-systems/dynamo.md), then use
[Raft](/software-engineering/distributed-systems/raft.md) to review the underlying consensus problem.

## Resources

- [2013 journal article](https://research.google/pubs/spanner-googles-globally-distributed-database/)
- [Download OSDI 2012 conference paper (PDF, USENIX)](https://www.usenix.org/system/files/conference/osdi12/osdi12-final-16.pdf) — an earlier version, distinct from the inspected journal copy.

---
type: Reference
title: Raft
description: Consensus for a replicated log, organized around leader election, replication, and safety.
tags:
- software-engineering
- distributed-systems
parent: /software-engineering/distributed-systems.md
related:
- /software-engineering/distributed-systems/dynamo.md
- /software-engineering/distributed-systems/spanner.md
publication: Diego Ongaro and John Ousterhout, **In Search of an Understandable Consensus Algorithm (Extended
  Version)**, May 20, 2014. The inspected copy is the 18-page extended paper.
sources:
- id: ref-1
  resource: https://raft.github.io/raft.pdf
  title: Download extended paper (PDF, authors' site)
- id: ref-2
  resource: https://raft.github.io/
  title: 'Raft project: visualizations, talks, and further papers'
generated:
  by: codex/gpt-6
  at: '2026-10-15T15:23:06+04:00'
---

Reference: Diego Ongaro and John Ousterhout,
**In Search of an Understandable Consensus Algorithm (Extended Version)**,
May 20, 2014. The inspected copy is the 18-page extended paper.

## Key ideas

- A leader orders log entries; terms and voting rules constrain elections.
- Commitment and election restrictions preserve the history applied by
  replicated state machines.
- Availability requires a communicating majority. Losing that majority can
  stop progress while safety remains intact.

## Read selectively

Start with **Replicated State Machines**, Figure 2, and **The Raft Consensus
Algorithm**, especially safety. Then read **Client Interaction**: agreement
on a log does not by itself remove duplicate client requests.

Use [Dynamo](/software-engineering/distributed-systems/dynamo.md) to contrast conflict-tolerant replication and
[Spanner](/software-engineering/distributed-systems/spanner.md) to distinguish consensus from distributed transaction
coordination. The Spanner paper uses Paxos, not Raft.

## Resources

- [Download extended paper (PDF, authors' site)](https://raft.github.io/raft.pdf)
- [Raft project: visualizations, talks, and further papers](https://raft.github.io/)

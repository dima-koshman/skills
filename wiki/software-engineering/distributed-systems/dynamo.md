---
type: Reference
title: Dynamo
description: An availability-oriented key-value store that exposes conflict resolution to applications.
tags:
- software-engineering
- distributed-systems
parent: /software-engineering/distributed-systems.md
related:
- /software-engineering/distributed-systems/raft.md
- /software-engineering/distributed-systems/spanner.md
publication: 'Giuseppe DeCandia and colleagues, **Dynamo: Amazon''s Highly Available Key-value Store**,
  SOSP 2007.'
sources:
- id: ref-1
  resource: https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf
  title: Download paper (PDF, coauthor Werner Vogels)
generated:
  by: codex/gpt-6
  at: '2026-10-15T15:23:06+04:00'
---

Reference: Giuseppe DeCandia and colleagues,
**Dynamo: Amazon's Highly Available Key-value Store**, SOSP 2007.

## Key ideas

- Consistent hashing partitions and replicates keys across nodes.
- Vector clocks track versions; reads may expose concurrent versions for
  application-assisted reconciliation.
- Sloppy quorums and hinted handoff support availability during temporary
  failures. Merkle trees support background replica repair.

## Read selectively

Read **System Architecture**, especially versioning and failure handling,
then **Experiences and Lessons Learned**. Ask what the application must do when
a write succeeds but replicas disagree.

Compare with [Raft](/software-engineering/distributed-systems/raft.md) and [Spanner](/software-engineering/distributed-systems/spanner.md): they solve different
agreement and transaction problems. This note describes the 2007 Dynamo
design; use separate documentation for current DynamoDB guarantees.

## Resources

- [Download paper (PDF, coauthor Werner Vogels)](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf)

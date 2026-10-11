# Dynamo

An availability-oriented key-value store that exposes conflict resolution to applications.

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

Compare with [Raft](raft.md) and [Spanner](spanner.md): they solve different
agreement and transaction problems. This note describes the 2007 Dynamo
design; use separate documentation for current DynamoDB guarantees.

## Resources

- [Download paper (PDF, coauthor Werner Vogels)](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf)

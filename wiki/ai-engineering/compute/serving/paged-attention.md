---
type: Concept
title: "PagedAttention"
aliases:
- "Paged Attention"
- "Paged KV Cache"
description: "A block table maps logical token positions to noncontiguous KV blocks, reducing allocation waste and enabling flexible sharing."
tags:
- ai-engineering
- compute
- inference
- serving
parent: /ai-engineering/compute/serving.md
related:
- /ai-engineering/compute/serving/kv-cache.md
- /ai-engineering/compute/serving/continuous-batching.md
- /ai-engineering/compute/serving/prefix-caching.md
- /ai-engineering/compute/serving/flash-attention.md
sources:
- id: pagedattention
  resource: https://arxiv.org/abs/2309.06180
  title: "Efficient Memory Management for Large Language Model Serving with PagedAttention"
  author: "Woosuk Kwon et al."
generated:
  by: codex/gpt-6
  at: '2026-10-22T13:46:52+04:00'
---

## Mechanism

A request's [KV cache](/ai-engineering/compute/serving/kv-cache.md) grows as it generates tokens. Reserving a contiguous region for its maximum possible length wastes memory and creates fragmentation.

PagedAttention divides KV storage into fixed-size blocks. A block table maps the sequence's logical positions to physical blocks that need not be adjacent. Attention kernels follow that mapping, and the allocator adds blocks as needed. Read-only blocks can be shared; branching generation can use copy-on-write.[^pagedattention]

## Benefit and cost

Less reserved and fragmented memory leaves room for more live sequences, which can improve serving throughput. The system pays for block tables, indirection and block-aware kernels; partially filled final blocks still waste some space.

Paging manages **where** exact KV entries live. It does not inherently reduce their numeric precision, select fewer tokens to attend to, or move them to CPU memory. CPU/disk transfer is [offloading](/ai-engineering/compute/serving/kv-cache-offloading.md).

## Relation to FlashAttention

[FlashAttention](/ai-engineering/compute/serving/flash-attention.md) reduces attention's memory traffic through tiling and on-chip computation. PagedAttention addresses KV layout and allocation. These ideas can coexist; implementation names do not imply mutually exclusive attention algorithms.[^pagedattention]

[^pagedattention]: Woosuk Kwon et al., [Efficient Memory Management for Large Language Model Serving with PagedAttention](https://arxiv.org/abs/2309.06180).

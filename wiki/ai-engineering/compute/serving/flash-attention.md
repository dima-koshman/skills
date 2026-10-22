---
type: Concept
title: "FlashAttention"
aliases:
- "IO-aware Attention"
description: "Tiled attention keeps intermediates on chip and avoids materializing the full attention-score matrix in GPU memory."
tags:
- ai-engineering
- compute
- inference
- serving
parent: /ai-engineering/compute/serving.md
related:
- /ai-engineering/compute/serving/paged-attention.md
- /ai-engineering/compute/serving/kernel-fusion.md
- /ai-engineering/compute/serving/prefill-decode.md
- /ai-engineering/compute/serving/grouped-query-attention.md
- /ai-engineering/compute/performance-regimes.md
sources:
- id: flashattention
  resource: https://arxiv.org/abs/2205.14135
  title: "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness"
  author: "Tri Dao et al."
generated:
  by: codex/gpt-6
  at: '2026-10-22T13:46:52+04:00'
---

## Mechanism

A straightforward attention implementation writes a large matrix of pairwise scores to high-bandwidth memory, then reads it again for softmax and value aggregation. FlashAttention tiles the computation, keeping working data in on-chip memory and updating softmax statistics incrementally.

It computes dense attention without materializing the full score matrix in GPU memory. The core idea is reducing data movement across the memory hierarchy, rather than approximating attention.[^flashattention]

## What improves

Lower memory traffic and fewer large intermediate allocations can make attention faster and enable longer sequences. This particularly matters when many query positions are processed, as in prefill and training.

“Exact attention” refers to the mathematical operation rather than bitwise equality across floating-point implementations. Dense attention's pairwise arithmetic still grows quadratically with sequence length; saving intermediate memory does not remove that work.

## Distinctions

[PagedAttention](/ai-engineering/compute/serving/paged-attention.md) manages KV blocks. [GQA](/ai-engineering/compute/serving/grouped-query-attention.md) changes the model's KV-head sharing. FlashAttention changes how attention computation is executed. A serving backend can combine these ideas; the best kernel depends on hardware, shapes and whether the workload is prefill or decode.[^flashattention]

[^flashattention]: Tri Dao et al., [FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness](https://arxiv.org/abs/2205.14135).

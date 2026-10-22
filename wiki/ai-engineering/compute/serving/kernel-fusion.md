---
type: Concept
title: "Kernel Fusion"
aliases:
- "Operator Fusion"
- "Fused Kernels"
description: "Execute multiple operations inside one GPU kernel to reduce launch overhead and avoid writing intermediate tensors to global memory."
tags:
- ai-engineering
- compute
- inference
- serving
parent: /ai-engineering/compute/serving.md
related:
- /ai-engineering/compute/serving/flash-attention.md
- /ai-engineering/compute/serving/cuda-graphs.md
- /ai-engineering/compute/serving/quantization.md
- /ai-engineering/compute/performance-regimes.md
- /ai-engineering/compute/compilers.md
sources:
- id: triton-softmax
  resource: https://triton-lang.org/main/getting-started/tutorials/02-fused-softmax.html
  title: "Fused Softmax"
  author: "Triton"
generated:
  by: codex/gpt-6
  at: '2026-10-22T13:46:52+04:00'
---

## Mechanism

Separate GPU operations often write an intermediate result to global memory, then launch another kernel that reads it back. Fusion performs the operations together so intermediate values can remain in registers or on-chip memory.

Softmax illustrates the idea: finding a maximum, subtracting it, exponentiating, reducing and normalizing can avoid repeatedly reading and writing the same row. Triton's tutorial demonstrates a fused implementation for rows that fit the kernel's on-chip working set.[^triton-softmax]

## When it helps

Fusion is valuable for bandwidth-bound sequences of small operations and can reduce launch overhead too. In inference, normalization, activation and related elementwise steps are natural opportunities. Compilers can generate fused kernels; carefully tuned libraries provide others.

## Trade-offs

A larger fused kernel can require more registers or shared memory, lowering occupancy or spilling values back to global memory. Layout constraints and oversized working sets can make fusion slower. “Fewer kernels” is therefore a hypothesis to profile, not sufficient evidence of a speedup.

[FlashAttention](/ai-engineering/compute/serving/flash-attention.md) applies IO-aware computation to attention; [CUDA Graphs](/ai-engineering/compute/serving/cuda-graphs.md) reduce repeated submission overhead without inherently combining operations.[^triton-softmax]

[^triton-softmax]: Triton, [Fused Softmax](https://triton-lang.org/main/getting-started/tutorials/02-fused-softmax.html).

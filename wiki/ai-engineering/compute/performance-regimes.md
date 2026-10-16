---
type: Concept
title: Compute, Memory and Overhead Bound
description: A slow model is limited by one of three things — math throughput, memory bandwidth, or host-side
  overhead — and each needs a different fix.
tags:
- ai-engineering
- compute
- gpu
parent: /ai-engineering/compute.md
related:
- /ai-engineering/compute/simd-simt.md
- /ai-engineering/compute/cuda.md
sources:
- id: horace-brrr
  resource: https://horace.io/brrr_intro.html
  title: Making Deep Learning Go Brrrr From First Principles
  author: Horace He
  last_modified: '2022-03-15T00:00:00Z'
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-10-16T16:00:00+04:00'
---

Horace He splits a model's runtime into three parts: the math itself, moving data through GPU memory,
and everything else the host does around it. Find which one dominates before you optimize, because a
fix for one does nothing for the others.[^horace-brrr]

| Regime | What the time goes to | Symptom | What helps |
| --- | --- | --- | --- |
| **Compute-bound** | The math units (tensor cores) are busy | Large matmuls near the chip's peak FLOPS | Lower precision, better kernels, more or faster chips |
| **Memory-bound** | Moving tensors between GPU memory (HBM) and the compute units | Elementwise ops, normalizations, small-batch decode: units wait for data | Operator fusion (load once, do several ops), keeping data in on-chip memory |
| **Overhead-bound** | The host: Python, framework dispatch, kernel launches | Doubling the batch barely changes runtime; GPU utilization is low | Bigger batches, fewer and larger ops, `torch.compile`, CUDA graphs |

## Overhead in detail

Overhead is time the GPU sits idle while the CPU prepares the next piece of work. It comes from:

- **The interpreter:** Python decides what to do next, one operation at a time.
- **The framework:** PyTorch picks a kernel for each op's dtype and device, and records autograd
  bookkeeping.
- **Kernel launches:** each launch has a fixed cost, regardless of how little the kernel does.

The GPU runs asynchronously, so overhead is hidden as long as the CPU queues work faster than the GPU
finishes it. With small ops the GPU wins that race and waits. The test: if a bigger batch costs almost no
extra time, the work wasn't what took the time.[^horace-brrr]

## Memory bandwidth and fusion

Most non-matmul operations do a few FLOPs per value loaded, so they spend their time on memory traffic.
Fusing several such ops into one kernel reads the data once and writes it once, instead of a round
trip per op. For these ops, cutting memory traffic matters more than adding compute.[^horace-brrr]

[^horace-brrr]: Horace He, 2022; resubmitted to Hacker News in May 2026 (199 points).

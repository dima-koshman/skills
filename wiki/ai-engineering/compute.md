---
type: Knowledge Area
title: AI Compute
description: How AI workloads run on hardware — inference and serving techniques, GPU and NPU programming models, performance limits, compilers, CUDA, Mojo and MAX.
tags:
- ai-engineering
- compute
parent: /ai-engineering.md
topics:
- /ai-engineering/compute/gpu-sharing.md
- /ai-engineering/compute/npu.md
- /ai-engineering/compute/performance-regimes.md
- /ai-engineering/compute/serving.md
- /ai-engineering/compute/simd-simt.md
- /ai-engineering/compute/software-stack.md
- /ai-engineering/compute/unified-memory.md
sources:
- id: modular-blog
  resource: https://www.modular.com/blog
  title: Modular blog
- id: lattner-series
  resource: https://www.modular.com/democratizing-ai-compute
  title: Democratizing AI Compute (Chris Lattner, 11 parts, Jan–Jun 2025)
- id: gpu-puzzles
  resource: https://puzzles.modular.com/
  title: Mojo GPU Puzzles
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-18T12:00:00+04:00'
---

The layer under the model: how its math becomes instructions on a GPU or another accelerator, and why
the software for that layer looks the way it does. Started 2026-10-16 while learning Mojo and MAX.

## Topics

### Hardware and performance

- [Compute, Memory and Overhead Bound](/ai-engineering/compute/performance-regimes.md) — the three things that
  can limit a model's speed, and how to tell which one you have.
- [SIMD and SIMT](/ai-engineering/compute/simd-simt.md) — vector instructions vs NVIDIA's per-thread model, and
  where Mojo sits.
- [Neural Processing Unit (NPU)](/ai-engineering/compute/npu.md) — accelerators built only for neural networks,
  and why GPU code doesn't port to them unchanged.
- [Unified CPU-GPU Memory](/ai-engineering/compute/unified-memory.md) — Apple silicon, MI300A and Grace Hopper:
  shared memory without merging the processors, and its bandwidth and capacity trade.

### [GPU sharing and scheduling](/ai-engineering/compute/gpu-sharing.md)

- [Why GPU Scheduling Differs from CPU Scheduling](/ai-engineering/compute/gpu-sharing/gpu-scheduling.md) — on-chip state,
  free warp switching and late preemption.
- [NVIDIA Multi-Process Service (MPS)](/ai-engineering/compute/gpu-sharing/mps.md) — how processes share a GPU natively,
  and what MPS adds so their kernels can run at the same time.
- [NVIDIA Multi-Instance GPU (MIG)](/ai-engineering/compute/gpu-sharing/mig.md) — hardware partitioning of one GPU, and how
  far its isolation goes.
- [NVIDIA Run:ai](/ai-engineering/compute/gpu-sharing/run-ai.md) — GPU scheduling, quotas and fractions on Kubernetes.
- [Sharing Accelerators Across Vendors](/ai-engineering/compute/gpu-sharing/accelerator-sharing.md) — what AMD, Apple and
  Google TPUs offer instead of MPS and MIG.

### [Software stack](/ai-engineering/compute/software-stack.md)

- [LLVM and MLIR](/ai-engineering/compute/software-stack/compilers.md) — the compiler infrastructure Mojo is built on.
- [CUDA Ecosystem](/ai-engineering/compute/software-stack/cuda.md) — why NVIDIA's software stack won, and the attempts to break
  it.
- [Mojo](/ai-engineering/compute/software-stack/mojo.md) — Modular's Python-like systems language for CPUs, GPUs and other
  accelerators.
- [MAX](/ai-engineering/compute/software-stack/max.md) — Modular's serving and modeling framework built on Mojo kernels.

### [Serving](/ai-engineering/compute/serving.md)

- [LLM Inference and Serving](/ai-engineering/compute/serving.md) — inference phases, KV memory,
  batching, attention kernels, quantization, disaggregation and GPU parallelism.

## Learning path

1. The mental model first: [Compute, Memory and Overhead Bound](/ai-engineering/compute/performance-regimes.md).
2. Why the stack looks as it does: parts 3, 8 and 9 of Lattner's series.[^lattner-series]
3. Hands-on: Mojo GPU Puzzles, from thread indexing to tensor cores.[^gpu-puzzles]
4. Follow Modular's releases and engineering posts.[^modular-blog]

[^lattner-series]: Democratizing AI Compute series index.
[^gpu-puzzles]: Mojo GPU Puzzles.
[^modular-blog]: Modular blog.

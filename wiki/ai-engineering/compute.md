---
type: Knowledge Area
title: AI Compute
description: How AI workloads run on hardware — inference and serving techniques, GPU and NPU programming models, performance limits, compilers, CUDA, Mojo and MAX.
tags:
- ai-engineering
- compute
parent: /ai-engineering.md
topics:
- /ai-engineering/compute/performance-regimes.md
- /ai-engineering/compute/simd-simt.md
- /ai-engineering/compute/npu.md
- /ai-engineering/compute/compilers.md
- /ai-engineering/compute/cuda.md
- /ai-engineering/compute/mojo.md
- /ai-engineering/compute/max.md
- /ai-engineering/compute/serving.md
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
  by: codex/gpt-6
  at: '2026-10-22T13:46:52+04:00'
---

The layer under the model: how its math becomes instructions on a GPU or another accelerator, and why
the software for that layer looks the way it does. Started 2026-10-16 while learning Mojo and MAX.

## Topics

- [Compute, Memory and Overhead Bound](/ai-engineering/compute/performance-regimes.md) — the three things that
  can limit a model's speed, and how to tell which one you have.
- [SIMD and SIMT](/ai-engineering/compute/simd-simt.md) — vector instructions vs NVIDIA's per-thread model, and
  where Mojo sits.
- [Neural Processing Unit (NPU)](/ai-engineering/compute/npu.md) — accelerators built only for neural networks,
  and why GPU code doesn't port to them unchanged.
- [LLVM and MLIR](/ai-engineering/compute/compilers.md) — the compiler infrastructure Mojo is built on.
- [CUDA Ecosystem](/ai-engineering/compute/cuda.md) — why NVIDIA's software stack won, and the attempts to break
  it.
- [Mojo](/ai-engineering/compute/mojo.md) — Modular's Python-like systems language for CPUs, GPUs and other
  accelerators.
- [MAX](/ai-engineering/compute/max.md) — Modular's serving and modeling framework built on Mojo kernels.
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

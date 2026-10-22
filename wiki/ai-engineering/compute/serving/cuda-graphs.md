---
type: Concept
title: "CUDA Graphs"
aliases:
- "CUDA Graph Replay"
description: "Capture and replay a compatible sequence of GPU operations to reduce repeated host dispatch and kernel-launch overhead."
tags:
- ai-engineering
- compute
- inference
- serving
parent: /ai-engineering/compute/serving.md
related:
- /ai-engineering/compute/serving/kernel-fusion.md
- /ai-engineering/compute/serving/continuous-batching.md
- /ai-engineering/compute/serving/prefill-decode.md
- /ai-engineering/compute/cuda.md
- /ai-engineering/compute/performance-regimes.md
sources:
- id: pytorch-cuda-graphs
  resource: https://pytorch.org/blog/accelerating-pytorch-with-cuda-graphs/
  title: "Accelerating PyTorch with CUDA Graphs"
  author: "PyTorch and NVIDIA"
- id: vllm-cuda-graphs
  resource: https://docs.vllm.ai/en/latest/design/cuda_graphs/
  title: "CUDA Graphs"
  author: "vLLM"
generated:
  by: codex/gpt-6
  at: '2026-10-22T13:46:52+04:00'
---

## Mechanism

Instead of having the CPU submit the same sequence of small operations repeatedly, capture a compatible execution into a CUDA graph and replay it. Inputs can change while the captured operation structure and required memory addresses remain suitable for replay.

The primary gain is less Python/framework/driver submission overhead. This is useful when GPU operations are short enough that host dispatch leaves gaps between them.[^pytorch-cuda-graphs]

## Constraints and cost

Graph-safe regions require controlled shapes, memory lifetimes and control flow. Capture has startup cost, and retained buffers consume memory. An inference engine must reconcile variable batch sizes and attention workloads with reusable execution shapes; vLLM documents its serving-specific graph modes.[^pytorch-cuda-graphs][^vllm-cuda-graphs]

A graph does not by itself reduce the mathematical work or fuse its kernels. If runtime is dominated by large matrix multiplication or KV reads, removing host overhead may have limited impact.

## Relation to fusion

[Kernel Fusion](/ai-engineering/compute/serving/kernel-fusion.md) combines operations to avoid launches and intermediate memory traffic. CUDA graphs replay a sequence more cheaply. They address overlapping but different costs and can be used together.

[^pytorch-cuda-graphs]: PyTorch and NVIDIA, [Accelerating PyTorch with CUDA Graphs](https://pytorch.org/blog/accelerating-pytorch-with-cuda-graphs/).
[^vllm-cuda-graphs]: vLLM, [CUDA Graphs](https://docs.vllm.ai/en/latest/design/cuda_graphs/).

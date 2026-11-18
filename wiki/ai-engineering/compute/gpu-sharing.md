---
type: Knowledge Area
title: GPU Sharing and Scheduling
description: 'How several workloads share one accelerator: GPU scheduling, MPS, MIG, Run:ai and other vendors''
  options.'
tags:
- ai-engineering
- compute
parent: /ai-engineering/compute.md
status: draft
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-18T12:00:00+04:00'
topics:
- /ai-engineering/compute/gpu-sharing/accelerator-sharing.md
- /ai-engineering/compute/gpu-sharing/gpu-scheduling.md
- /ai-engineering/compute/gpu-sharing/mig.md
- /ai-engineering/compute/gpu-sharing/mps.md
- /ai-engineering/compute/gpu-sharing/run-ai.md
---

How several processes, teams or tenants share one accelerator, from hardware partitions to time-slicing.

## Topics

- [Sharing Accelerators Across Vendors](/ai-engineering/compute/gpu-sharing/accelerator-sharing.md) — How NVIDIA, AMD, Apple and Google TPUs let several workloads use one chip, from hardware partitions to time-slicing to exclusive allocation.
- [Why GPU Scheduling Differs from CPU Scheduling](/ai-engineering/compute/gpu-sharing/gpu-scheduling.md) — GPUs switch between threads constantly but between programs rarely, because they keep tens of MB of thread state on-chip; data transfer is not the reason.
- [NVIDIA Multi-Instance GPU (MIG)](/ai-engineering/compute/gpu-sharing/mig.md) — Hardware partitioning of one GPU into up to seven isolated instances, each with its own compute, cache and memory path, on Ampere and newer data center GPUs.
- [NVIDIA Multi-Process Service (MPS)](/ai-engineering/compute/gpu-sharing/mps.md) — A CUDA runtime service that lets kernels from different processes run on a GPU at the same time, where native multi-process sharing only takes turns on the whole GPU.
- [NVIDIA Run:ai](/ai-engineering/compute/gpu-sharing/run-ai.md) — A Kubernetes platform for GPU scheduling, quotas and fractional GPU sharing across teams, open source since October 2026, with KAI Scheduler as its scheduling engine.

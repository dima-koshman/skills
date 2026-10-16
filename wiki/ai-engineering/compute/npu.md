---
type: Concept
title: Neural Processing Unit (NPU)
description: A hardware accelerator built specifically for neural-network math, usually low-precision and
  power-efficient, programmed with explicit memory movement rather than the GPU's thread model; Google's TPU is
  one, and GPU Tensor Cores are the same idea as a unit inside a GPU.
tags:
- ai-engineering
- compute
parent: /ai-engineering/compute.md
related:
- /ai-engineering/compute/simd-simt.md
- /ai-engineering/compute/mojo.md
- /ai-engineering/compute/cuda.md
sources:
- id: wikipedia-npu
  resource: https://en.wikipedia.org/wiki/Neural_processing_unit
  title: Neural processing unit (Wikipedia)
- id: modular-qualcomm-npu
  resource: https://www.modular.com/blog/modcon-qualcomm
  title: 'Modular and Qualcomm: Same code, new silicon'
  author: Ruyman Reyes, Kern Handa, Nicolas Miller et al. (Modular)
  last_modified: '2026-08-18T00:00:00Z'
- id: lattner-hw-software
  resource: https://www.modular.com/blog/democratizing-ai-compute-part-9-why-do-hw-companies-struggle-to-build-ai-software
  title: 'Democratizing AI Compute, part 9: Why do HW companies struggle to build AI software?'
  author: Chris Lattner
  last_modified: '2025-04-22T00:00:00Z'
- id: tpu-paper
  resource: https://arxiv.org/abs/1704.04760
  title: In-Datacenter Performance Analysis of a Tensor Processing Unit (ISCA 2017)
  author: Norman P. Jouppi, Cliff Young, Nishant Patil, David Patterson et al.
  last_modified: '2017-04-16T00:00:00Z'
- id: wikipedia-tpu
  resource: https://en.wikipedia.org/wiki/Tensor_Processing_Unit
  title: Tensor Processing Unit (Wikipedia)
- id: nvidia-tensor-cores-cuda9
  resource: https://developer.nvidia.com/blog/programming-tensor-cores-cuda-9/
  title: Programming Tensor Cores in CUDA 9
  author: Jeremy Appleyard, Scott Yokim (NVIDIA)
  last_modified: '2017-10-17T00:00:00Z'
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-10-16T17:00:00+04:00'
---

An NPU (also called an AI accelerator) is hardware designed to accelerate neural-network workloads. It
can be a standalone chip or part of a CPU or GPU, and it runs inference, training, or both.[^wikipedia-npu]

## NPU vs GPU

- **GPU:** a general parallel processor. It runs the CUDA or OpenCL thread model and has added
  low-precision matrix units since the late 2010s, which is why GPUs also serve as AI
  accelerators.[^wikipedia-npu]
- **NPU:** narrower. NPUs are often manycore or spatial designs that focus on low-precision arithmetic,
  new dataflow architectures, or in-memory computing. Consumer NPUs aim to be small and power-efficient
  while running small models at reasonable speed.[^wikipedia-npu]

Examples: Apple silicon's Neural Engine (via Core ML), Qualcomm's Hexagon in phones and the Cloud AI 100
card in data centers, Intel's NPU in Meteor Lake CPUs, Google's TPU in the cloud.[^wikipedia-npu][^modular-qualcomm-npu]

## TPUs and Tensor Cores

All three are hardware for one operation, multiply-accumulate over matrices. They differ in how much of
the chip is devoted to it.

| | Tensor Core | TPU | NPU |
| --- | --- | --- | --- |
| What it is | A unit inside each streaming multiprocessor of an NVIDIA GPU | A whole chip (ASIC) from Google | The category of neural-network accelerators |
| Since | Volta V100, 2017 | Used internally 2015, public 2016 | — |
| Around it | General SIMT cores that run everything else | Memory and simple control; little general-purpose logic | Varies: phone NPUs are small blocks in an SoC, data-center ones are cards |

- **Tensor Core.** Each Volta Tensor Core computes `D = A × B + C` on 4×4 matrices: FP16 inputs, FP16 or
  FP32 accumulation, 64 fused multiply-adds per clock. A warp uses several together for a 16×16×16
  multiply. They gave the V100 12× the FP32 throughput of the previous P100.[^nvidia-tensor-cores-cuda9] Large
  matmuls, the [compute-bound](/ai-engineering/compute/performance-regimes.md) part of a model, run on them.
- **TPU.** The first TPU's core was a 256×256 systolic array of 8-bit multipliers with 32-bit
  accumulators.[^wikipedia-tpu] That is 65,536 multiply-accumulate units, 92 TOPS peak. It was 15–30× faster
  than the CPUs and GPUs it was compared with (Haswell, K80). It had no caches or out-of-order execution,
  so its latency was deterministic, which suited 99th-percentile response-time targets.[^tpu-paper]
  Generations run from v1 (2015) to v7 Ironwood (2025), with v8 announced in April 2026. TPUs are
  available on Google Cloud and programmed through TensorFlow, JAX and PyTorch.[^wikipedia-tpu]
- **Systolic array.** A grid of multiply-accumulate cells that pass values to their neighbors each clock.
  Each operand is read from memory once and reused across a whole row or column, so the array stays busy
  without waiting on memory bandwidth.

The TPU is an NPU in the data-center class.[^wikipedia-tpu] GPUs and NPUs are converging: GPUs gained matrix
units (Tensor Cores), and NPUs carry vector units for everything else. Qualcomm's chip below has both,
HVX and HMX.

## What programming one looks like: Qualcomm Hexagon

Modular's port of MAX to Qualcomm's Cloud AI 100 shows the differences from a GPU:[^modular-qualcomm-npu]

- **SIMD, not SIMT.** Vector units (HVX) plus a matrix unit (HMX); work is dispatched to cores and
  threads, not grids and blocks. See [SIMD and SIMT](/ai-engineering/compute/simd-simt.md).
- **Explicit memory.** No unified memory and no cache hierarchy: data is tiled into on-chip memory (VTCM)
  and moved from DDR by explicit DMA.
- **Layouts.** The matrix unit needs a packed layout, and converting costs time; batch-1 decode used a
  vector GEMV kernel to skip the conversion.
- **Scale.** The card has 4 SoCs with 32 GB each. Gemma 4 31B in fp16 (~60 GB of weights) needed tensor
  parallelism across all four.

## Why NPUs struggle

Lattner argues that hardware companies treat software as overhead because "the chip is still the
product". Their software ends up built for demos and a few large customers, so each new chip lacks the
ecosystem developers need.[^lattner-hw-software] Mojo and MAX are Modular's bet that one portable stack can fill
that gap. Qualcomm, a chip company, now owns Modular (see [Mojo](/ai-engineering/compute/mojo.md)).

[^wikipedia-npu]: Wikipedia, Neural processing unit.
[^modular-qualcomm-npu]: Modular engineering blog, 2026-08-18.
[^lattner-hw-software]: Chris Lattner, 2025-04-22.
[^tpu-paper]: Jouppi et al., ISCA 2017.
[^wikipedia-tpu]: Wikipedia, Tensor Processing Unit.
[^nvidia-tensor-cores-cuda9]: NVIDIA Technical Blog, 2017-10-17.

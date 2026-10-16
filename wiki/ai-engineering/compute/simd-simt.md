---
type: Concept
title: SIMD and SIMT
description: Two ways to run one instruction over many data elements — explicit vector instructions (SIMD) vs
  NVIDIA's per-thread model on top of vector hardware (SIMT) — and why the difference matters for portable kernels.
tags:
- ai-engineering
- compute
- gpu
parent: /ai-engineering/compute.md
related:
- /ai-engineering/compute/npu.md
- /ai-engineering/compute/mojo.md
- /ai-engineering/compute/performance-regimes.md
sources:
- id: cuda-programming-model
  resource: https://docs.nvidia.com/cuda/cuda-programming-guide/01-introduction/programming-model.html
  title: CUDA Programming Guide 1.2, Programming Model (v13.4.2)
  author: NVIDIA
- id: mojo-gpu-fundamentals
  resource: https://max.modular.com/gpu/fundamentals
  title: GPU programming fundamentals (Mojo/MAX docs)
  author: Modular
- id: mojo-numeric-types
  resource: https://mojolang.org/docs/reference/numeric-types/
  title: Mojo numeric types reference
  author: Modular
- id: modular-qualcomm-npu
  resource: https://www.modular.com/blog/modcon-qualcomm
  title: 'Modular and Qualcomm: Same code, new silicon'
  author: Ruyman Reyes, Kern Handa, Nicolas Miller et al. (Modular)
  last_modified: '2026-08-18T00:00:00Z'
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-10-16T16:00:00+04:00'
---

Both apply one instruction to many data elements at once. They differ in what the programmer writes and
who handles lanes that need to do something different.

| | SIMD (single instruction, multiple data) | SIMT (single instruction, multiple threads) |
| --- | --- | --- |
| You write | Vector code: one instruction over a register of N values | Scalar code for one thread; you launch thousands |
| Width | Fixed by the register (e.g. 4, 8, 16 lanes) | No fixed data width in the model; hardware groups threads into warps |
| Control flow | One path; lanes that should differ are masked by hand | Each thread may branch; hardware masks inactive lanes |
| Addresses | Usually contiguous vector loads | Each thread computes its own address; the hardware merges them |
| Where | CPU AVX/NEON, Qualcomm Hexagon HVX | NVIDIA GPUs; AMD GPUs use the same model |

## How SIMT works

Threads in a block are grouped into **warps** of 32. A warp executes in SIMT fashion: all threads
progress through the kernel in lockstep, but each may follow its own control flow path. When threads in
a warp take different branches (**warp divergence**), the hardware runs each path in turn with the other
threads masked off.[^cuda-programming-model] Divergence is correct but slow: the warp pays for both paths.

## Is SIMT a higher-level SIMD?

Mostly yes. The execution units underneath are SIMD: one instruction drives 32 lanes. SIMT is the
programming and execution model on top. It is more than a compiler wrapper, because the hardware
supplies what makes the per-thread illusion cheap: lane masks for divergence, per-thread address
handling, and fast switching between warps to hide memory latency. In SIMD the compiler or programmer
does that work.[^cuda-programming-model]

## Why it matters for portable kernels

Qualcomm's Hexagon NPU is SIMD, not SIMT, and dispatches work to cores and threads rather than grids
and blocks. Modular could keep the model code the same when porting to it, but hand-wrote the heavy
kernels (matmul, attention) for the chip.[^modular-qualcomm-npu] A GPU kernel's structure assumes the SIMT
model, so it does not carry over unchanged.

## Where Mojo sits

Mojo exposes both:

- **SIMD is the base numeric type.** Mojo's numeric primitives are built on `SIMD` vectors; a `SIMD` with
  one element is a `Scalar`, and the width is a power of two and part of the type.[^mojo-numeric-types]
  On CPUs and the Hexagon NPU these lower to vector instructions.[^modular-qualcomm-npu]
- **GPU kernels use the SIMT model.** You write per-thread code using `thread_idx`, `block_idx` and
  `block_dim`, and launch it over a grid with `grid_dim` and `block_dim` through a `DeviceContext`. Warp
  size is 32 or 64 depending on the GPU.[^mojo-gpu-fundamentals]

[^cuda-programming-model]: NVIDIA CUDA Programming Guide, section 1.2.
[^mojo-gpu-fundamentals]: Modular docs, GPU programming fundamentals.
[^mojo-numeric-types]: Mojo numeric types reference.
[^modular-qualcomm-npu]: Modular engineering blog, 2026-08-18.

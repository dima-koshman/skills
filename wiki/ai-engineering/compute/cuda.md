---
type: Concept
title: CUDA Ecosystem
description: Why NVIDIA's CUDA became the default AI software stack, why chip companies struggle to match it,
  and the main attempts to break the lock-in — compilers, Python DSLs, Mojo, and NVIDIA's own CUDA Rust.
tags:
- ai-engineering
- compute
- gpu
parent: /ai-engineering/compute.md
related:
- /ai-engineering/compute/mojo.md
- /ai-engineering/compute/compilers.md
- /ai-engineering/compute/npu.md
- /ai-engineering/compute/simd-simt.md
sources:
- id: lattner-series
  resource: https://www.modular.com/democratizing-ai-compute
  title: Democratizing AI Compute (11 parts)
  author: Chris Lattner
- id: lattner-cuda-success
  resource: https://www.modular.com/blog/democratizing-ai-compute-part-3-how-did-cuda-succeed
  title: 'Democratizing AI Compute, part 3: How did CUDA succeed?'
  author: Chris Lattner
  last_modified: '2025-02-12T00:00:00Z'
- id: lattner-hw-software
  resource: https://www.modular.com/blog/democratizing-ai-compute-part-9-why-do-hw-companies-struggle-to-build-ai-software
  title: 'Democratizing AI Compute, part 9: Why do HW companies struggle to build AI software?'
  author: Chris Lattner
  last_modified: '2025-04-22T00:00:00Z'
- id: nvidia-cuda-rust
  resource: https://developer.nvidia.com/blog/introducing-cuda-rust-two-tracks-for-writing-gpu-kernels/
  title: 'Introducing CUDA Rust: Two Tracks for Writing GPU Kernels'
  author: Sri Koundinyan, Melih Elibol, Jonathan Bentz (NVIDIA)
  last_modified: '2026-09-08T00:00:00Z'
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-10-16T16:00:00+04:00'
---

"CUDA" is several things at once: a C++ dialect for GPU kernels, a runtime and driver, and a large set of
tuned libraries (cuBLAS, cuDNN) that frameworks like PyTorch call. Part 2 of Lattner's series unpacks
these layers.

## Why it won

Lattner's argument: less technical superiority than strategy. NVIDIA kept one backward-compatible GPU
line, so cheap gaming cards were an on-ramp for developers. Google and Meta, busy with their own products
and in-house chips, left low-level GPU tuning for PyTorch and TensorFlow to NVIDIA. When generative AI made
efficiency a cost problem, the industry's optimization work was already tied to CUDA.[^lattner-cuda-success]

## Why rivals struggle

At chip companies "the chip is still the product": software is overhead, built for demos and big-customer
deals rather than a broad platform. Each new hardware feature multiplies the software team's work while
leadership optimizes silicon cost and tapeout schedules.[^lattner-hw-software] See
[NPU](/ai-engineering/compute/npu.md).

## Attempts to break the lock-in

| Approach | Examples | Lattner's series covers |
| --- | --- | --- |
| Portable C++ standards | OpenCL, SYCL | part 5 |
| AI compilers | TVM, XLA | part 6 |
| Python embedded DSLs | Triton | part 7 |
| Compiler infrastructure | [MLIR](/ai-engineering/compute/compilers.md) | part 8 |
| A new language and stack | [Mojo](/ai-engineering/compute/mojo.md) and [MAX](/ai-engineering/compute/max.md) | parts 10–11 |

The series is written by Modular's CEO, so read parts 10–11 as advocacy.[^lattner-series]

## NVIDIA's own move: CUDA Rust (2026-09)

NVIDIA added native GPU kernels in Rust, compiled to PTX, on two tracks:[^nvidia-cuda-rust]

- **SIMT** (`cuda-oxide`): a custom rustc backend; per-thread code as in CUDA C++. Early alpha, pinned
  nightly toolchain.
- **Tile** (`cutile-rs`): stable Rust; you work on tiles of data and the compiler maps them onto the
  architecture. NVIDIA recommends starting here and dropping to SIMT for explicit control.

Both enforce aliasing rules at compile time. It answers the same need as Mojo — a safer, modern kernel
language — but stays NVIDIA-only. The tile model resembles Triton and Mojo's layout abstractions.

[^lattner-series]: Chris Lattner, Democratizing AI Compute, 2025.
[^lattner-cuda-success]: Chris Lattner, 2025-02-12.
[^lattner-hw-software]: Chris Lattner, 2025-04-22.
[^nvidia-cuda-rust]: NVIDIA Technical Blog, 2026-09-08.

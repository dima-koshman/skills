---
type: Knowledge Area
title: AI Software Stack
description: 'The software between models and chips: CUDA, LLVM and MLIR, Mojo and MAX.'
tags:
- ai-engineering
- compute
parent: /ai-engineering/compute.md
status: draft
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-18T12:00:00+04:00'
topics:
- /ai-engineering/compute/software-stack/compilers.md
- /ai-engineering/compute/software-stack/cuda.md
- /ai-engineering/compute/software-stack/max.md
- /ai-engineering/compute/software-stack/mojo.md
---

The software layer between a model and the chip, and the attempts to make it portable across vendors.

## Topics

- [LLVM and MLIR](/ai-engineering/compute/software-stack/compilers.md) — The compiler infrastructure under Mojo — LLVM's shared intermediate representation that decouples languages from chips, and MLIR's many-level IRs (dialects) that keep AI operations meaningful until late in compilation.
- [CUDA Ecosystem](/ai-engineering/compute/software-stack/cuda.md) — Why NVIDIA's CUDA became the default AI software stack, why chip companies struggle to match it, and the main attempts to break the lock-in — compilers, Python DSLs, Mojo, and NVIDIA's own CUDA Rust.
- [MAX](/ai-engineering/compute/software-stack/max.md) — Modular's AI serving and modeling framework — OpenAI-compatible model serving, a PyTorch-like Python modeling API, and Mojo kernels for CPUs, GPUs and ASICs without depending on CUDA or ROCm.
- [Mojo](/ai-engineering/compute/software-stack/mojo.md) — Modular's Python-like systems language for CPUs, GPUs and other accelerators, built on MLIR; 1.0 and open source (Apache 2.0) since August 2026, owned by Qualcomm.

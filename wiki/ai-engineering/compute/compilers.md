---
type: Concept
title: LLVM and MLIR
description: The compiler infrastructure under Mojo — LLVM's shared intermediate representation that decouples
  languages from chips, and MLIR's many-level IRs (dialects) that keep AI operations meaningful until late in
  compilation.
tags:
- ai-engineering
- compute
- compilers
parent: /ai-engineering/compute.md
related:
- /ai-engineering/compute/mojo.md
- /ai-engineering/compute/cuda.md
sources:
- id: aosa-llvm
  resource: https://aosabook.org/en/v1/llvm.html
  title: The Architecture of Open Source Applications (Volume 1), LLVM
  author: Chris Lattner
- id: mlir-paper
  resource: https://arxiv.org/abs/2002.11054
  title: 'MLIR: A Compiler Infrastructure for the End of Moore''s Law'
  author: Chris Lattner, Mehdi Amini, Uday Bondhugula et al.
  last_modified: '2020-02-25T00:00:00Z'
- id: lattner-mlir
  resource: https://www.modular.com/blog/democratizing-ai-compute-part-8-what-about-the-mlir-compiler-infrastructure
  title: 'Democratizing AI Compute, part 8: What about the MLIR compiler infrastructure?'
  author: Chris Lattner
  last_modified: '2025-04-08T00:00:00Z'
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-10-16T16:00:00+04:00'
---

## LLVM

LLVM, started by Chris Lattner, is a compiler toolkit built around one shared **intermediate
representation (IR)**:[^aosa-llvm]

1. A **front end** translates a language into LLVM IR (Clang for C/C++, also Rust and Swift).
2. Shared **optimizer** passes improve the IR.
3. A **back end** turns IR into machine code for a target: x86, ARM, NVIDIA PTX.

The split is the point: a new language gets every supported chip, and a new chip gets every language,
without writing N × M compilers.

## MLIR

LLVM IR is fixed and low-level: by the time code reaches it, "a matmul on two tensors" has become loops
over memory loads, and the optimizations that need the high-level view are no longer possible. MLIR
("Multi-Level IR") is a framework for defining many IRs, called **dialects**, each with its own operations
and types at its own level of abstraction: tensor ops, loops, GPU constructs, and at the bottom LLVM IR.
Code is lowered progressively from one dialect to the next.[^mlir-paper][^lattner-mlir]

Lattner's assessment (2025): MLIR succeeded technically and is embedded in nearly every major AI stack,
CUDA included, and it built an open community. It did not democratize AI compute, because dialects
multiplied before the core foundations were settled and competing companies fragmented its
governance.[^lattner-mlir]

## How Mojo uses them

[Mojo](/ai-engineering/compute/mojo.md) is built directly on MLIR: its built-in types are thin wrappers over
MLIR types and operations, and it compiles through MLIR to LLVM and then to machine code. Writing Mojo GPU
kernels needs the GPU programming model (threads, memory hierarchy, tiling), not MLIR internals. MLIR
depth matters for compiler work or defining low-level types.

## Reading order

1. The LLVM chapter of *The Architecture of Open Source Applications* (~30 min).[^aosa-llvm]
2. Lattner's part 8 on MLIR, for the history and what went wrong.[^lattner-mlir]
3. The MLIR paper, sections 1–3, for the design rationale.[^mlir-paper]
4. Optional, hands-on: the [MLIR Toy tutorial](https://mlir.llvm.org/docs/Tutorials/Toy/), which builds a
   dialect step by step.

[^aosa-llvm]: Chris Lattner, AOSA volume 1.
[^mlir-paper]: Lattner, Amini, Bondhugula et al., 2020.
[^lattner-mlir]: Chris Lattner, 2025-04-08.

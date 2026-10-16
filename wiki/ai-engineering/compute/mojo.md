---
type: Tool
title: Mojo
description: Modular's Python-like systems language for CPUs, GPUs and other accelerators, built on MLIR; 1.0
  and open source (Apache 2.0) since August 2026, owned by Qualcomm.
resource: https://mojolang.org/
tags:
- ai-engineering
- compute
- programming-language
parent: /ai-engineering/compute.md
related:
- /ai-engineering/compute/max.md
- /ai-engineering/compute/compilers.md
- /ai-engineering/compute/simd-simt.md
- /ai-engineering/compute/cuda.md
- /ai-engineering/compute/npu.md
sources:
- id: mojo-1-0-path
  resource: https://www.modular.com/blog/the-path-to-mojo-1-0
  title: The path to Mojo 1.0
  author: Modular
  last_modified: '2025-12-05T00:00:00Z'
- id: mojo-open-source
  resource: https://www.modular.com/blog/mojo-open-source
  title: Mojo is now open source!
  author: Modular
  last_modified: '2026-08-18T00:00:00Z'
- id: modular-blog
  resource: https://www.modular.com/blog
  title: Modular blog index (release and acquisition posts, read 2026-10-16)
- id: mojo-numeric-types
  resource: https://mojolang.org/docs/reference/numeric-types/
  title: Mojo numeric types reference
- id: mojo-gpu-fundamentals
  resource: https://max.modular.com/gpu/fundamentals
  title: GPU programming fundamentals (Mojo/MAX docs)
- id: structured-kernels
  resource: https://www.modular.com/blog/structured-mojo-kernels-part-1-peak-performance-half-the-code
  title: 'Structured Mojo Kernels, part 1: Peak performance, half the code'
  author: Fabio Riccardi (Modular)
  last_modified: '2026-03-05T00:00:00Z'
- id: nissen-critique
  resource: https://viralinstruction.com/posts/mojo/
  title: A look at the Mojo language for bioinformatics
  author: Jakob Nybo Nissen
  last_modified: '2024-02-09T00:00:00Z'
- id: hn-open-source
  resource: https://news.ycombinator.com/item?id=49358327
  title: Hacker News discussion of Mojo going open source (233 points)
  last_modified: '2026-08-19T00:00:00Z'
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-10-16T16:00:00+04:00'
---

Mojo is Modular's language for writing fast code — CPU code and GPU or accelerator kernels — with
Python-like syntax. It is built on [MLIR](/ai-engineering/compute/compilers.md) and is the language
[MAX](/ai-engineering/compute/max.md)'s kernels are written in.

## Timeline

| Date | Event |
| --- | --- |
| 2023-05 | Announced by Modular, the company Chris Lattner co-founded |
| 2024 | Standard library open-sourced[^mojo-open-source] |
| 2025-12 | "The path to Mojo 1.0" published[^mojo-1-0-path] |
| 2026-07-29 | Qualcomm completes its acquisition of Modular[^modular-blog] |
| 2026-08-11 | Mojo 1.0 released (Modular 26.5)[^modular-blog] |
| 2026-08-18 | Compiler and tooling open-sourced under Apache 2.0 with LLVM exceptions[^mojo-open-source] |

## Design decisions behind 1.0

From Modular's 1.0 plan:[^mojo-1-0-path]

- **Gated on features, not a date.** 1.0 shipped when the Phase 1 roadmap goals were done.
- **Stability first.** Semantic versioning and explicit stable/unstable markers, so packages built on
  stable APIs keep working across 1.x. The cost is slower change.
- **Deferred features.** Async, private members and some systems features were left out of 1.0;
  `match` and enums come in 1.x.
- **Breaking changes saved for 2.0,** behind a flag, with one compiler building both 1.x and 2.0
  packages, so migration can go package by package — explicitly to avoid a Python 2-to-3 split.

The compiler does not accept outside contributions yet; Modular aims to open them by the end of
2026.[^mojo-open-source]

## Programming model

- **SIMD everywhere.** Numeric primitives are `SIMD` vectors; `Float32` is `SIMD[DType.float32, 1]`, a
  `Scalar`.[^mojo-numeric-types]
- **GPU kernels in the SIMT model.** Per-thread code with `thread_idx` and `block_idx`, launched over a
  grid through a `DeviceContext` with `enqueue_function`.[^mojo-gpu-fundamentals] See
  [SIMD and SIMT](/ai-engineering/compute/simd-simt.md).
- **Compile-time metaprogramming** keeps abstractions free at runtime. Modular's structured-kernel
  design splits a kernel into data movement, pipeline and compute parts. It reports half the code at the
  same ~1,770 TFLOPS on an SM100 matmul — Modular's own benchmark on one kernel.[^structured-kernels]

## Criticism

- **Benchmark claims.** Jakob Nybo Nissen showed a well-known Mojo speedup came from the parsing
  algorithm, not the language: a Julia port matched it. He also found the syntax far from Python despite
  the branding (2024, before open-sourcing).[^nissen-critique]
- **Adoption.** On Hacker News, commenters argued that open-sourcing came too late and lost early
  momentum, that Qualcomm may not keep investing, and that the Python-superset promise is still
  unmet.[^hn-open-source]

[^mojo-1-0-path]: Modular, 2025-12-05.
[^mojo-open-source]: Modular, 2026-08-18.
[^modular-blog]: Modular blog index, read 2026-10-16.
[^mojo-numeric-types]: Mojo numeric types reference.
[^mojo-gpu-fundamentals]: Modular docs, GPU programming fundamentals.
[^structured-kernels]: Fabio Riccardi, 2026-03-05.
[^nissen-critique]: Jakob Nybo Nissen, 2024-02-09.
[^hn-open-source]: Hacker News, 2026-08-19.

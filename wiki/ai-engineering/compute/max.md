---
type: Tool
title: MAX
description: Modular's AI serving and modeling framework — OpenAI-compatible model serving, a PyTorch-like Python
  modeling API, and Mojo kernels for CPUs, GPUs and ASICs without depending on CUDA or ROCm.
resource: https://max.modular.com/intro
tags:
- ai-engineering
- compute
- serving
parent: /ai-engineering/compute.md
related:
- /ai-engineering/compute/mojo.md
- /ai-engineering/compute/npu.md
- /ai-engineering/compute/cuda.md
- /ai-engineering/enterprise/llm-gateway.md
- /ai-engineering/compute/serving.md
sources:
- id: max-intro
  resource: https://max.modular.com/intro
  title: 'MAX: A high-performance AI serving and modeling framework'
  author: Modular
- id: modular-qualcomm-npu
  resource: https://www.modular.com/blog/modcon-qualcomm
  title: 'Modular and Qualcomm: Same code, new silicon'
  author: Ruyman Reyes, Kern Handa, Nicolas Miller et al. (Modular)
  last_modified: '2026-08-18T00:00:00Z'
- id: mojo-open-source
  resource: https://www.modular.com/blog/mojo-open-source
  title: Mojo is now open source!
  author: Modular
  last_modified: '2026-08-18T00:00:00Z'
generated:
  by: codex/gpt-6
  at: '2026-10-22T13:46:52+04:00'
---

MAX is where [Mojo](/ai-engineering/compute/mojo.md) kernels turn into a product: a framework for serving and
building models across hardware.[^max-intro]

| Part | What it does |
| --- | --- |
| **Serving** | Runs hundreds of open models behind OpenAI-compatible inference APIs, started from the CLI or Docker |
| **Modeling** | PyTorch-like Python APIs, plus AI coding skills, for porting custom models |
| **Kernels** | One API library and hundreds of open-source Mojo kernels for CPUs, GPUs and ASICs |

MAX states that it does not depend on PyTorch, CUDA or ROCm, and lists NVIDIA, AMD and Apple silicon plus
CPUs and ASICs as targets.[^max-intro] Customizing MAX kernels or models still needs a prebuilt Mojo
compiler.[^mojo-open-source]

## Portability in practice

On Qualcomm's Cloud AI 100, the model definitions stayed the same and device selection went through a
device context, but matmul and attention kernels were hand-written for the NPU. GPT-2 went from 1.6×
slower than Qualcomm's PyTorch baseline to 6.7× faster after about three weeks of
optimization.[^modular-qualcomm-npu] So "same code" holds at the model and API level, not for the heaviest
kernels. See [NPU](/ai-engineering/compute/npu.md).

## Relation to an LLM gateway

The techniques used inside serving engines are mapped in
[LLM Inference and Serving](/ai-engineering/compute/serving.md), including KV-cache
management, batching, quantization and parallelism.

MAX is an inference server, like vLLM: it sits behind an [LLM gateway](/ai-engineering/enterprise/llm-gateway.md)
as one more OpenAI-compatible upstream, not in place of it.

[^max-intro]: Modular MAX documentation, read 2026-10-16.
[^modular-qualcomm-npu]: Modular engineering blog, 2026-08-18.
[^mojo-open-source]: Modular, 2026-08-18.

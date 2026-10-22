---
type: Concept
title: "Pipeline Parallelism"
aliases:
- "PP"
- "Inter-layer Model Parallelism"
description: "Place successive groups of model layers on different devices and pipeline requests or microbatches through the stages."
tags:
- ai-engineering
- compute
- inference
- serving
parent: /ai-engineering/compute/serving.md
related:
- /ai-engineering/compute/serving/tensor-parallelism.md
- /ai-engineering/compute/serving/data-parallelism.md
- /ai-engineering/compute/serving/continuous-batching.md
- /ai-engineering/compute/serving/prefill-decode-disaggregation.md
sources:
- id: modular-parallelism
  resource: https://handbook.modular.com/inference-optimization/data-tensor-pipeline-expert-hybrid-parallelism/
  title: "Data, tensor, pipeline, expert and hybrid parallelisms"
  author: "Modular"
- id: vllm-parallel
  resource: https://docs.vllm.ai/en/latest/serving/parallelism_scaling/
  title: "Parallelism and Scaling"
  author: "vLLM"
generated:
  by: codex/gpt-6
  at: '2026-10-22T13:46:52+04:00'
---

## Mechanism

Assign consecutive layer groups to stages on different devices. Activations travel from one stage to the next. Multiple requests or microbatches can occupy different stages simultaneously, like an assembly line.

This splits model memory without requiring the same within-layer communication pattern as [Tensor Parallelism](/ai-engineering/compute/serving/tensor-parallelism.md). Stage boundaries communicate less frequently, which can suit weaker interconnects.[^modular-parallelism]

## Trade-offs

An individual token still traverses the stages in order. Stages can sit idle during pipeline fill/drain or when another stage is slower: these idle periods are **pipeline bubbles**. Keeping several microbatches in flight improves utilization but complicates scheduling. Balance stages by execution time and memory, not only layer count.[^modular-parallelism]

vLLM supports combining TP and PP for models spanning nodes, and describes PP as useful for uneven layer splits or devices without fast NVLink connections.[^vllm-parallel]

## Distinction from PD disaggregation

Pipeline stages contain different **parts of the model**. [Prefill–Decode Disaggregation](/ai-engineering/compute/serving/prefill-decode-disaggregation.md) assigns different **phases of requests** to worker pools. Each phase can itself use pipeline or tensor parallelism.

[^modular-parallelism]: Modular, [Data, tensor, pipeline, expert and hybrid parallelisms](https://handbook.modular.com/inference-optimization/data-tensor-pipeline-expert-hybrid-parallelism/).
[^vllm-parallel]: vLLM, [Parallelism and Scaling](https://docs.vllm.ai/en/latest/serving/parallelism_scaling/).

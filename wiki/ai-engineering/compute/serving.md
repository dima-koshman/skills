---
type: Knowledge Area
title: LLM Inference and Serving
aliases:
- LLM Inferencing
- LLM Serving
description: A map of autoregressive inference phases, KV memory, scheduling, attention kernels, precision and distributed serving trade-offs.
tags:
- ai-engineering
- compute
- inference
- serving
parent: /ai-engineering/compute.md
related:
- /ai-engineering/compute/performance-regimes.md
- /ai-engineering/compute/max.md
- /ai-engineering/context/prompt-caching.md
topics:
- /ai-engineering/compute/serving/prefill-decode.md
- /ai-engineering/compute/serving/kv-cache.md
- /ai-engineering/compute/serving/serving-metrics.md
- /ai-engineering/compute/serving/continuous-batching.md
- /ai-engineering/compute/serving/chunked-prefill.md
- /ai-engineering/compute/serving/paged-attention.md
- /ai-engineering/compute/serving/prefix-caching.md
- /ai-engineering/compute/serving/speculative-decoding.md
- /ai-engineering/compute/serving/kv-cache-offloading.md
- /ai-engineering/compute/serving/prefill-decode-disaggregation.md
- /ai-engineering/compute/serving/quantization.md
- /ai-engineering/compute/serving/flash-attention.md
- /ai-engineering/compute/serving/grouped-query-attention.md
- /ai-engineering/compute/serving/cuda-graphs.md
- /ai-engineering/compute/serving/kernel-fusion.md
- /ai-engineering/compute/serving/tensor-parallelism.md
- /ai-engineering/compute/serving/pipeline-parallelism.md
- /ai-engineering/compute/serving/data-parallelism.md
- /ai-engineering/compute/serving/expert-parallelism.md
- /ai-engineering/compute/serving/context-parallelism.md
- /ai-engineering/compute/serving/inference-routing.md
sources:
- id: modular-handbook
  resource: https://handbook.modular.com/
  title: LLM Inference Handbook
  author: Modular
- id: vllm-tuning
  resource: https://docs.vllm.ai/en/latest/configuration/optimization/
  title: Optimization and Tuning
  author: vLLM
generated:
  by: codex/gpt-6
  at: '2026-10-22T13:46:52+04:00'
---

## Scope

**Inference** runs a trained model to produce predictions or generated output.
**Serving** manages requests around that execution: queues, scheduling, memory,
worker placement and streaming responses. This area focuses on autoregressive
Transformer generation; other architectures can need different techniques.

The wiki previously covered [MAX](/ai-engineering/compute/max.md), hardware
[performance regimes](/ai-engineering/compute/performance-regimes.md) and
[Prompt Caching](/ai-engineering/context/prompt-caching.md). The pages below add the
inference mechanisms behind them.

## Concept map

| Question | Concepts |
| --- | --- |
| What happens during a request? | [Prefill and Decode](/ai-engineering/compute/serving/prefill-decode.md), [Serving Metrics](/ai-engineering/compute/serving/serving-metrics.md) |
| Where does sequence state live? | [KV Cache](/ai-engineering/compute/serving/kv-cache.md), [PagedAttention](/ai-engineering/compute/serving/paged-attention.md), [Prefix Caching](/ai-engineering/compute/serving/prefix-caching.md), [KV Offloading](/ai-engineering/compute/serving/kv-cache-offloading.md) |
| How is work scheduled? | [Continuous Batching](/ai-engineering/compute/serving/continuous-batching.md), [Chunked Prefill](/ai-engineering/compute/serving/chunked-prefill.md), [Prefill–Decode Disaggregation](/ai-engineering/compute/serving/prefill-decode-disaggregation.md), [Cache-aware Routing](/ai-engineering/compute/serving/inference-routing.md) |
| How can token execution become cheaper? | [Speculative Decoding](/ai-engineering/compute/serving/speculative-decoding.md), [Quantization](/ai-engineering/compute/serving/quantization.md), [FlashAttention](/ai-engineering/compute/serving/flash-attention.md), [Kernel Fusion](/ai-engineering/compute/serving/kernel-fusion.md), [CUDA Graphs](/ai-engineering/compute/serving/cuda-graphs.md) |
| How does the model architecture affect KV memory? | [Grouped-Query and Multi-Query Attention](/ai-engineering/compute/serving/grouped-query-attention.md) |
| How is work distributed across GPUs? | [Tensor](/ai-engineering/compute/serving/tensor-parallelism.md), [Pipeline](/ai-engineering/compute/serving/pipeline-parallelism.md), [Data](/ai-engineering/compute/serving/data-parallelism.md), [Expert](/ai-engineering/compute/serving/expert-parallelism.md) and [Context Parallelism](/ai-engineering/compute/serving/context-parallelism.md) |

## Start from the bottleneck

Use this as a diagnostic reading order, not a universal tuning recipe:

1. Read **phases, metrics and KV cache** first. Decide whether the objective is
   interactive latency, aggregate throughput, memory capacity or goodput.
2. For repeated prompts, study **prefix caching and routing**.
3. For streaming stalls under load, study **batching, chunked prefill and phase
   disaggregation**.
4. For memory pressure, separate **weights, KV state and temporary activations**
   before choosing paging, quantization, offloading or sharding.
5. For low device utilization, distinguish **launch overhead, memory traffic and
   insufficient parallel work** before choosing graphs, fusion or speculation.

Techniques interact. Increasing concurrency may improve utilization while
increasing KV demand and latency. Benchmark combinations against the actual
request distribution rather than adding each optimization's advertised speedup.

## Sources and reading path

The **Modular handbook** is a useful first pass across the system, especially for
a conceptual map. Treat vendor capability claims and benchmark numbers as
specific to their configuration.[^modular-handbook]

Use **current engine documentation** for supported combinations and defaults;
vLLM's tuning guide connects token budgets and parallelism to workload choices.[^vllm-tuning]
The individual concepts also cite original sources: Orca for iteration scheduling,
PagedAttention for KV allocation, Sarathi-Serve for chunked prefill, FlashAttention
for IO-aware attention, and DistServe for phase disaggregation. These explain
design decisions; their historical speedups are not current engine rankings.

[^modular-handbook]: Modular, [LLM Inference Handbook](https://handbook.modular.com/), checked October 22, 2026.
[^vllm-tuning]: vLLM, [Optimization and Tuning](https://docs.vllm.ai/en/latest/configuration/optimization/), checked October 22, 2026.

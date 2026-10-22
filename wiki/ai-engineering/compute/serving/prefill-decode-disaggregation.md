---
type: Concept
title: "Prefill–Decode Disaggregation"
aliases:
- "PD Disaggregation"
- "Disaggregated Prefilling"
- "Split-phase Serving"
description: "Separate worker pools perform prompt processing and token generation, transferring KV state between independently tuned phases."
tags:
- ai-engineering
- compute
- inference
- serving
parent: /ai-engineering/compute/serving.md
related:
- /ai-engineering/compute/serving/prefill-decode.md
- /ai-engineering/compute/serving/kv-cache.md
- /ai-engineering/compute/serving/chunked-prefill.md
- /ai-engineering/compute/serving/serving-metrics.md
- /ai-engineering/compute/serving/inference-routing.md
- /ai-engineering/compute/serving/tensor-parallelism.md
sources:
- id: distserve
  resource: https://arxiv.org/abs/2401.09670
  title: "DistServe: Disaggregating Prefill and Decoding for Goodput-optimized Large Language Model Serving"
  author: "Yinmin Zhong et al."
- id: vllm-disagg
  resource: https://docs.vllm.ai/en/latest/features/disagg_prefill/
  title: "Disaggregated Prefilling"
  author: "vLLM"
generated:
  by: codex/gpt-6
  at: '2026-10-22T13:46:52+04:00'
---

## Mechanism

Prefill workers process prompts and hand their KV state to decode workers, which stream subsequent tokens. Separate pools can use different hardware allocations, parallelism degrees and scheduling policies.

The goal is to prevent long prompt processing from interrupting ongoing decode and to tune time to first token separately from streaming latency. DistServe studies this through **goodput**: how much traffic meets both phase-specific latency objectives.[^distserve]

## Trade-offs

KV handoff consumes bandwidth and adds a synchronization point. The deployment also needs routing, capacity balance between pools, transfer backpressure and failure handling. If transfer time dominates or one pool is underused, separation can lose to colocated serving.

vLLM's documentation explicitly warns that its disaggregated-prefill feature does not improve throughput. That is compatible with DistServe's goodput results: meeting latency objectives and maximizing unconstrained tokens/s are different goals.[^vllm-disagg][^distserve]

## Alternative and boundary

[Chunked Prefill](/ai-engineering/compute/serving/chunked-prefill.md) mitigates interference on shared workers without a separate decode pool. Compare it before accepting disaggregation's operational cost.

This is a split between **inference phases**, not [pipeline parallelism](/ai-engineering/compute/serving/pipeline-parallelism.md), which splits a model's layers across devices.

[^distserve]: Yinmin Zhong et al., [DistServe: Disaggregating Prefill and Decoding for Goodput-optimized Large Language Model Serving](https://arxiv.org/abs/2401.09670).
[^vllm-disagg]: vLLM, [Disaggregated Prefilling](https://docs.vllm.ai/en/latest/features/disagg_prefill/).

---
type: Concept
title: "Grouped-Query Attention"
aliases:
- "GQA"
- "Multi-Query Attention"
- "MQA"
description: "Multiple query heads share fewer key/value heads, reducing KV state and decode bandwidth through a model architecture choice."
tags:
- ai-engineering
- compute
- inference
- serving
parent: /ai-engineering/compute/serving.md
related:
- /ai-engineering/compute/serving/kv-cache.md
- /ai-engineering/compute/serving/flash-attention.md
- /ai-engineering/compute/serving/tensor-parallelism.md
- /ai-engineering/compute/serving/context-parallelism.md
sources:
- id: gqa
  resource: https://arxiv.org/abs/2305.13245
  title: "GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints"
  author: "Joshua Ainslie et al."
- id: vllm-cp
  resource: https://docs.vllm.ai/en/latest/serving/context_parallel_deployment/
  title: Context Parallel Deployment
  author: vLLM
generated:
  by: codex/gpt-6
  at: '2026-10-22T13:46:52+04:00'
---

## Mechanism

Ordinary multi-head attention gives each query head a corresponding key/value head. **Multi-query attention (MQA)** shares one KV head across all query heads. **Grouped-query attention (GQA)** uses an intermediate number: each group of query heads shares a KV head.

Fewer KV heads mean less state to store per token and fewer KV bytes to read during decode.[^gqa]

## Why the distinction matters

The [KV cache](/ai-engineering/compute/serving/kv-cache.md) memory estimate must use the number of KV heads. For the same layer count, head dimension and precision, eight KV heads require one quarter of the KV payload of 32 KV heads.

This is an architecture/checkpoint property, not a lossless runtime switch. The GQA paper describes uptraining existing multi-head checkpoints and studies the speed/quality compromise. A server cannot safely reinterpret an arbitrary checkpoint as MQA just by changing a flag.[^gqa]

## Trade-offs

Sharing KV heads reduces representational freedom; quality depends on how the model was trained or adapted. Fewer KV heads can also constrain straightforward head-based tensor sharding, making [context parallelism](/ai-engineering/compute/serving/context-parallelism.md) relevant when serving very long contexts across many devices.[^vllm-cp]

[^gqa]: Joshua Ainslie et al., [GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints](https://arxiv.org/abs/2305.13245).
[^vllm-cp]: vLLM, [Context Parallel Deployment](https://docs.vllm.ai/en/latest/serving/context_parallel_deployment/).

---
type: Concept
title: "Tensor Parallelism"
aliases:
- "TP"
- "Intra-layer Model Parallelism"
description: "Split tensors and layer computation across GPUs so a model replica can use their combined memory and compute."
tags:
- ai-engineering
- compute
- inference
- serving
parent: /ai-engineering/compute/serving.md
related:
- /ai-engineering/compute/serving/pipeline-parallelism.md
- /ai-engineering/compute/serving/data-parallelism.md
- /ai-engineering/compute/serving/context-parallelism.md
- /ai-engineering/compute/serving/grouped-query-attention.md
sources:
- id: megatron
  resource: https://arxiv.org/abs/1909.08053
  title: "Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism"
  author: "Mohammad Shoeybi et al."
- id: vllm-parallel
  resource: https://docs.vllm.ai/en/latest/serving/parallelism_scaling/
  title: "Parallelism and Scaling"
  author: "vLLM"
generated:
  by: codex/gpt-6
  at: '2026-10-22T13:46:52+04:00'
---

## Mechanism

Tensor parallelism shards computation **within** a model layer. GPUs compute pieces of matrix multiplications or attention heads and communicate to combine the results. Together they form one model replica rather than independent copies. Megatron-LM established a practical intra-layer sharding design; its original paper concerns training, while serving engines reuse the general strategy.[^megatron]

## When it helps

Use TP to fit a model and its runtime state across devices, or when reduced per-device work improves the latency of one replica. It works especially well with fast device-to-device links.

Frequent communication is the central cost. More shards mean smaller local operations plus synchronization, so latency does not improve linearly with GPU count. Architecture and supported kernels constrain valid sharding degrees.[^vllm-parallel]

## Alternatives

[Data Parallelism](/ai-engineering/compute/serving/data-parallelism.md) adds independent request capacity. [Pipeline Parallelism](/ai-engineering/compute/serving/pipeline-parallelism.md) splits layer ranges and communicates at stage boundaries. [Context Parallelism](/ai-engineering/compute/serving/context-parallelism.md) distributes sequence-related work and KV state. These dimensions can be combined, but each creates a different communication pattern.

[^megatron]: Mohammad Shoeybi et al., [Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism](https://arxiv.org/abs/1909.08053).
[^vllm-parallel]: vLLM, [Parallelism and Scaling](https://docs.vllm.ai/en/latest/serving/parallelism_scaling/).

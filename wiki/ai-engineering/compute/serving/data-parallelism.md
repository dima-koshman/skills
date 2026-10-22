---
type: Concept
title: "Inference Data Parallelism"
aliases:
- "DP"
- "Model Replication"
description: "Replicate model capacity across workers and route independent requests to different replicas to scale aggregate serving throughput."
tags:
- ai-engineering
- compute
- inference
- serving
parent: /ai-engineering/compute/serving.md
related:
- /ai-engineering/compute/serving/tensor-parallelism.md
- /ai-engineering/compute/serving/pipeline-parallelism.md
- /ai-engineering/compute/serving/expert-parallelism.md
- /ai-engineering/compute/serving/inference-routing.md
- /ai-engineering/compute/serving/prefix-caching.md
sources:
- id: vllm-dp
  resource: https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/
  title: "Data Parallel Deployment"
  author: "vLLM"
generated:
  by: codex/gpt-6
  at: '2026-10-22T13:46:52+04:00'
---

## Mechanism

For a dense model, run independent replicas and assign different requests or batches to each. A replica can itself span GPUs using tensor or pipeline parallelism. There are no training gradients to synchronize between these inference replicas.

**Calculated example:** four replicas with TP=2 use eight GPUs. Requests are distributed across the four replicas; each selected replica uses its pair of GPUs.[^vllm-dp]

## When it helps

Replication increases aggregate capacity and can reduce queueing when load is spread well. It does not by itself make the model computation for one request faster or allow an oversized model to fit within one replica.

The costs are duplicated weights and separate KV caches. A follow-up request sent to a cold replica may repeat prefill that a warm replica could skip. [Inference Routing](/ai-engineering/compute/serving/inference-routing.md) connects load balance with prefix locality.[^vllm-dp]

## MoE qualification

Not every product's DP mode is a set of fully independent complete models. In vLLM's MoE deployments, attention can be data-parallel while expert layers are sharded across a larger group, requiring coordination across ranks. Read the topology rather than assuming dense-model replication semantics apply unchanged.[^vllm-dp]

[^vllm-dp]: vLLM, [Data Parallel Deployment](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/).

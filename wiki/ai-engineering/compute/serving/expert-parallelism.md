---
type: Concept
title: "Expert Parallelism"
aliases:
- "EP"
- "MoE Expert Sharding"
description: "Place different mixture-of-experts networks on different GPUs and route token activations to the devices that own selected experts."
tags:
- ai-engineering
- compute
- inference
- serving
parent: /ai-engineering/compute/serving.md
related:
- /ai-engineering/compute/serving/data-parallelism.md
- /ai-engineering/compute/serving/tensor-parallelism.md
- /ai-engineering/compute/serving/prefill-decode-disaggregation.md
sources:
- id: vllm-ep
  resource: https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/
  title: "Expert Parallel Deployment"
  author: "vLLM"
generated:
  by: codex/gpt-6
  at: '2026-10-22T13:46:52+04:00'
---

## Mechanism

A mixture-of-experts (MoE) layer selects a subset of expert networks for each token. Expert parallelism places different experts on different GPUs. Token activations are dispatched to the selected experts and the results are combined, creating cross-device communication around the expert computation.

This distributes expert weights while retaining sparse per-token activation. It is distinct from [Tensor Parallelism](/ai-engineering/compute/serving/tensor-parallelism.md), which shards the tensors of a layer.[^vllm-ep]

## What makes it difficult

Routing can send many more tokens to some experts than others. The busiest expert devices can become bottlenecks while others wait. Dispatch/combine communication and the size of local expert batches also matter.

vLLM documents expert load balancing that redistributes mappings and can add redundant expert copies. Those copies consume memory that could otherwise hold KV state. Communication backends may be tuned differently for prefill throughput and decode latency.[^vllm-ep]

## Deployment implication

EP only applies to an architecture with experts; it is not a generic acceleration switch for dense models. Large deployments can combine data-parallel attention with expert-sharded feed-forward layers, so “number of replicas” alone does not describe their topology.

[^vllm-ep]: vLLM, [Expert Parallel Deployment](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/).

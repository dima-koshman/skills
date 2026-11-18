---
type: Concept
title: Inference Parallelism
aliases:
- Tensor Parallelism
- TP
- Intra-layer Model Parallelism
- Pipeline Parallelism
- PP
- Inter-layer Model Parallelism
- Inference Data Parallelism
- DP
- Model Replication
- Expert Parallelism
- EP
- MoE Expert Sharding
- Context Parallelism
- CP
- Prefill Context Parallelism
- Decode Context Parallelism
description: 'Five ways to spread one model''s serving work across GPUs, each splitting something different: tensors,
  layers, requests, experts or the sequence.'
tags:
- ai-engineering
- compute
- inference
- serving
parent: /ai-engineering/compute/serving.md
related:
- /ai-engineering/models/llm-architecture.md
- /ai-engineering/compute/serving/batching-and-scheduling.md
- /ai-engineering/compute/serving/prefill-decode-and-kv-cache.md
status: draft
sources:
- id: megatron
  resource: https://arxiv.org/abs/1909.08053
  title: 'Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism'
  author: Mohammad Shoeybi et al.
- id: vllm-parallel
  resource: https://docs.vllm.ai/en/latest/serving/parallelism_scaling/
  title: Parallelism and Scaling
  author: vLLM
- id: modular-parallelism
  resource: https://handbook.modular.com/inference-optimization/data-tensor-pipeline-expert-hybrid-parallelism/
  title: Data, tensor, pipeline, expert and hybrid parallelisms
  author: Modular
- id: vllm-dp
  resource: https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/
  title: Data Parallel Deployment
  author: vLLM
- id: vllm-ep
  resource: https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/
  title: Expert Parallel Deployment
  author: vLLM
- id: vllm-cp
  resource: https://docs.vllm.ai/en/latest/serving/context_parallel_deployment/
  title: Context Parallel Deployment
  author: vLLM
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-18T12:00:00+04:00'
---

Five ways to spread serving work across GPUs. Each one splits something different: tensors within a layer, layers, independent requests, mixture-of-experts experts, or one request's sequence.

## Tensor Parallelism

Split tensors and layer computation across GPUs so a model replica can use their combined memory and compute.

### Mechanism

Tensor parallelism shards computation **within** a model layer. GPUs compute pieces of matrix multiplications or attention heads and communicate to combine the results. Together they form one model replica rather than independent copies. Megatron-LM established a practical intra-layer sharding design; its original paper concerns training, while serving engines reuse the general strategy.[^megatron]

### When it helps

Use TP to fit a model and its runtime state across devices, or when reduced per-device work improves the latency of one replica. It works especially well with fast device-to-device links.

Frequent communication is the central cost. More shards mean smaller local operations plus synchronization, so latency does not improve linearly with GPU count. Architecture and supported kernels constrain valid sharding degrees.[^vllm-parallel]

### Alternatives

[Data Parallelism](/ai-engineering/compute/serving/parallelism.md#inference-data-parallelism) adds independent request capacity. [Pipeline Parallelism](/ai-engineering/compute/serving/parallelism.md#pipeline-parallelism) splits layer ranges and communicates at stage boundaries. [Context Parallelism](/ai-engineering/compute/serving/parallelism.md#context-parallelism) distributes sequence-related work and KV state. These dimensions can be combined, but each creates a different communication pattern.

## Pipeline Parallelism

Place successive groups of model layers on different devices and pipeline requests or microbatches through the stages.

### Mechanism

Assign consecutive layer groups to stages on different devices. Activations travel from one stage to the next. Multiple requests or microbatches can occupy different stages simultaneously, like an assembly line.

This splits model memory without requiring the same within-layer communication pattern as [Tensor Parallelism](/ai-engineering/compute/serving/parallelism.md#tensor-parallelism). Stage boundaries communicate less frequently, which can suit weaker interconnects.[^modular-parallelism]

### Trade-offs

An individual token still traverses the stages in order. Stages can sit idle during pipeline fill/drain or when another stage is slower: these idle periods are **pipeline bubbles**. Keeping several microbatches in flight improves utilization but complicates scheduling. Balance stages by execution time and memory, not only layer count.[^modular-parallelism]

vLLM supports combining TP and PP for models spanning nodes, and describes PP as useful for uneven layer splits or devices without fast NVLink connections.[^vllm-parallel]

### Distinction from PD disaggregation

Pipeline stages contain different **parts of the model**. [Prefill–Decode Disaggregation](/ai-engineering/compute/serving/batching-and-scheduling.md#prefilldecode-disaggregation) assigns different **phases of requests** to worker pools. Each phase can itself use pipeline or tensor parallelism.

## Inference Data Parallelism

Replicate model capacity across workers and route independent requests to different replicas to scale aggregate serving throughput.

### Mechanism

For a dense model, run independent replicas and assign different requests or batches to each. A replica can itself span GPUs using tensor or pipeline parallelism. There are no training gradients to synchronize between these inference replicas.

**Calculated example:** four replicas with TP=2 use eight GPUs. Requests are distributed across the four replicas; each selected replica uses its pair of GPUs.[^vllm-dp]

### When it helps

Replication increases aggregate capacity and can reduce queueing when load is spread well. It does not by itself make the model computation for one request faster or allow an oversized model to fit within one replica.

The costs are duplicated weights and separate KV caches. A follow-up request sent to a cold replica may repeat prefill that a warm replica could skip. [Inference Routing](/ai-engineering/compute/serving/batching-and-scheduling.md#cache-aware-inference-routing) connects load balance with prefix locality.[^vllm-dp]

### MoE qualification

Not every product's DP mode is a set of fully independent complete models. In vLLM's MoE deployments, attention can be data-parallel while expert layers are sharded across a larger group, requiring coordination across ranks. Read the topology rather than assuming dense-model replication semantics apply unchanged.[^vllm-dp]

## Expert Parallelism

Place different mixture-of-experts networks on different GPUs and route token activations to the devices that own selected experts.

### Mechanism

A mixture-of-experts (MoE) layer selects a subset of expert networks for each token. Expert parallelism places different experts on different GPUs. Token activations are dispatched to the selected experts and the results are combined, creating cross-device communication around the expert computation.

This distributes expert weights while retaining sparse per-token activation. It is distinct from [Tensor Parallelism](/ai-engineering/compute/serving/parallelism.md#tensor-parallelism), which shards the tensors of a layer.[^vllm-ep]

### What makes it difficult

Routing can send many more tokens to some experts than others. The busiest expert devices can become bottlenecks while others wait. Dispatch/combine communication and the size of local expert batches also matter.

vLLM documents expert load balancing that redistributes mappings and can add redundant expert copies. Those copies consume memory that could otherwise hold KV state. Communication backends may be tuned differently for prefill throughput and decode latency.[^vllm-ep]

### Deployment implication

EP only applies to an architecture with experts; it is not a generic acceleration switch for dense models. Large deployments can combine data-parallel attention with expert-sharded feed-forward layers, so “number of replicas” alone does not describe their topology.

## Context Parallelism

Distribute one request's sequence-related attention work or KV state across devices to handle long contexts and reduce per-device pressure.

### Mechanism

Context parallelism distributes work along the **sequence** dimension rather than simply splitting model weights or assigning independent requests.

During prefill, devices can process different query-token chunks and exchange the K/V information needed for attention. Some strategies gather full K/V; others circulate chunks to avoid keeping the entire sequence on each device.

During decode, devices can hold different portions of the long KV history and combine attention results. vLLM documents prefill and decode context parallelism separately.[^vllm-cp]

### When it matters

Long contexts can exceed a single device's KV capacity or make attention reads expensive even when weights fit. Head-based tensor sharding is also limited by the number of KV heads; GQA models can otherwise duplicate KV state at large TP degrees.

### Trade-offs

The saved memory or parallel attention work comes with communication and synchronization. Small contexts may offer too little work to amortize that overhead. Supported combinations depend on the engine and attention backend.

Context parallelism preserves access to the configured context. It does not mean truncating the prompt or replacing full attention with a sliding window. Those change what information the model directly attends to.[^vllm-cp]

[^megatron]: Mohammad Shoeybi et al., [Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism](https://arxiv.org/abs/1909.08053).
[^vllm-parallel]: vLLM, [Parallelism and Scaling](https://docs.vllm.ai/en/latest/serving/parallelism_scaling/).
[^modular-parallelism]: Modular, [Data, tensor, pipeline, expert and hybrid parallelisms](https://handbook.modular.com/inference-optimization/data-tensor-pipeline-expert-hybrid-parallelism/).
[^vllm-dp]: vLLM, [Data Parallel Deployment](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/).
[^vllm-ep]: vLLM, [Expert Parallel Deployment](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/).
[^vllm-cp]: vLLM, [Context Parallel Deployment](https://docs.vllm.ai/en/latest/serving/context_parallel_deployment/).

---
type: Concept
title: "Context Parallelism"
aliases:
- "CP"
- "Prefill Context Parallelism"
- "Decode Context Parallelism"
description: "Distribute one request's sequence-related attention work or KV state across devices to handle long contexts and reduce per-device pressure."
tags:
- ai-engineering
- compute
- inference
- serving
parent: /ai-engineering/compute/serving.md
related:
- /ai-engineering/compute/serving/kv-cache.md
- /ai-engineering/compute/serving/tensor-parallelism.md
- /ai-engineering/compute/serving/grouped-query-attention.md
- /ai-engineering/compute/serving/prefill-decode.md
sources:
- id: vllm-cp
  resource: https://docs.vllm.ai/en/latest/serving/context_parallel_deployment/
  title: "Context Parallel Deployment"
  author: "vLLM"
generated:
  by: codex/gpt-6
  at: '2026-10-22T13:46:52+04:00'
---

## Mechanism

Context parallelism distributes work along the **sequence** dimension rather than simply splitting model weights or assigning independent requests.

During prefill, devices can process different query-token chunks and exchange the K/V information needed for attention. Some strategies gather full K/V; others circulate chunks to avoid keeping the entire sequence on each device.

During decode, devices can hold different portions of the long KV history and combine attention results. vLLM documents prefill and decode context parallelism separately.[^vllm-cp]

## When it matters

Long contexts can exceed a single device's KV capacity or make attention reads expensive even when weights fit. Head-based tensor sharding is also limited by the number of KV heads; GQA models can otherwise duplicate KV state at large TP degrees.

## Trade-offs

The saved memory or parallel attention work comes with communication and synchronization. Small contexts may offer too little work to amortize that overhead. Supported combinations depend on the engine and attention backend.

Context parallelism preserves access to the configured context. It does not mean truncating the prompt or replacing full attention with a sliding window. Those change what information the model directly attends to.[^vllm-cp]

[^vllm-cp]: vLLM, [Context Parallel Deployment](https://docs.vllm.ai/en/latest/serving/context_parallel_deployment/).

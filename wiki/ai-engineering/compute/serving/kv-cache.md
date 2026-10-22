---
type: Concept
title: "KV Cache"
aliases:
- "Key-Value Cache"
- "Attention Cache"
description: "Cached attention keys and values avoid recomputing earlier tokens while making sequence length and concurrency consume serving memory."
tags:
- ai-engineering
- compute
- inference
- serving
parent: /ai-engineering/compute/serving.md
related:
- /ai-engineering/compute/serving/prefill-decode.md
- /ai-engineering/compute/serving/paged-attention.md
- /ai-engineering/compute/serving/prefix-caching.md
- /ai-engineering/compute/serving/kv-cache-offloading.md
- /ai-engineering/compute/serving/grouped-query-attention.md
- /ai-engineering/compute/serving/quantization.md
sources:
- id: hf-cache
  resource: https://huggingface.co/docs/transformers/main/cache_explanation
  title: "How caching works"
  author: "Hugging Face"
- id: modular-offloading
  resource: https://handbook.modular.com/inference-optimization/kv-cache-offloading/
  title: "KV cache offloading"
  author: "Modular"
generated:
  by: codex/gpt-6
  at: '2026-10-22T13:46:52+04:00'
---

## Mechanism

In causal Transformer attention, a past token's keys and values do not change when future tokens arrive. Store them once per attention layer, then reuse them at each decode step. New tokens append new K/V entries. The current query still attends over the retained history; caching does not make that attention work disappear.[^hf-cache]

## Memory model

For uniform, full-attention layers with equal key/value head dimensions, the unsharded payload is approximately:

```text
KV bytes = 2 × layers × KV heads × head dimension
             × bytes per element × total retained tokens across requests
```

Use **KV heads**, not query heads, for [GQA/MQA](/ai-engineering/compute/serving/grouped-query-attention.md). This estimate excludes allocator padding, metadata and distributed replication. Sliding-window, latent-attention and hybrid architectures need different accounting.[^hf-cache][^modular-offloading]

**Calculated example:** 32 layers × 8 KV heads × 128 dimensions × 2 bytes × 2 gives 128 KiB per retained token. An 8,192-token request needs about 1 GiB; 32 such requests need about 32 GiB, before overhead.

## Related optimizations

[Paging](/ai-engineering/compute/serving/paged-attention.md) reduces allocation waste; [prefix caching](/ai-engineering/compute/serving/prefix-caching.md) reuses state across requests; [offloading](/ai-engineering/compute/serving/kv-cache-offloading.md) changes its storage tier; [quantization](/ai-engineering/compute/serving/quantization.md) changes its representation. Ordinary within-request KV caching and cross-request prefix reuse are distinct.

[^hf-cache]: Hugging Face, [How caching works](https://huggingface.co/docs/transformers/main/cache_explanation).
[^modular-offloading]: Modular, [KV cache offloading](https://handbook.modular.com/inference-optimization/kv-cache-offloading/).

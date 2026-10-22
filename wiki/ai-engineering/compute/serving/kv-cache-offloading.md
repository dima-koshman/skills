---
type: Concept
title: "KV Cache Offloading"
aliases:
- "KV Cache Tiering"
- "Hierarchical KV Cache"
description: "Moving KV state to CPU memory or storage trades GPU residency for transfer work and potentially avoids later recomputation."
tags:
- ai-engineering
- compute
- inference
- serving
parent: /ai-engineering/compute/serving.md
related:
- /ai-engineering/compute/serving/kv-cache.md
- /ai-engineering/compute/serving/prefix-caching.md
- /ai-engineering/compute/serving/paged-attention.md
- /ai-engineering/compute/serving/prefill-decode-disaggregation.md
sources:
- id: modular-offloading
  resource: https://handbook.modular.com/inference-optimization/kv-cache-offloading/
  title: "KV cache offloading"
  author: "Modular"
- id: hf-cache-strategies
  resource: https://huggingface.co/docs/transformers/main/kv_cache
  title: "Cache strategies"
  author: "Hugging Face"
generated:
  by: codex/gpt-6
  at: '2026-10-22T13:46:52+04:00'
---

## Two related mechanisms

**Retention tiering:** move inactive or evicted prefix blocks from GPU memory to CPU RAM or slower storage. Reload them when a later request reuses that prefix. This can retain more reusable state than GPU memory alone allows.[^modular-offloading]

**Active-cache offloading:** keep much of an ongoing request's KV state on CPU and transfer the currently needed layer to the GPU. Hugging Face documents layerwise offloading with asynchronous prefetch and eviction.[^hf-cache-strategies]

The first mainly preserves reusable history between uses; the second can let an active generation fit in limited GPU memory.

## When the trade pays

Offloading exchanges scarce GPU capacity for copy bandwidth, latency and storage management. Restoring a large, expensive prefix can beat recomputing it. Repeatedly transferring active state can slow decode when the interconnect cannot keep up.

**Decision rule:** compare transfer plus lookup time with the computation avoided, and include whether the freed GPU memory enables useful extra concurrency. Offloading is not inherently a speedup.[^modular-offloading][^hf-cache-strategies]

## Boundaries

KV offloading moves attention state; weight offloading moves model parameters. [Quantization](/ai-engineering/compute/serving/quantization.md) reduces representation size. [Paging](/ai-engineering/compute/serving/paged-attention.md) changes allocation layout without inherently moving state off-device.

[^modular-offloading]: Modular, [KV cache offloading](https://handbook.modular.com/inference-optimization/kv-cache-offloading/).
[^hf-cache-strategies]: Hugging Face, [Cache strategies](https://huggingface.co/docs/transformers/main/kv_cache).

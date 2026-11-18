---
type: Concept
title: Prefill, Decode and the KV Cache
aliases:
- Prefill and Decode
- Prompt Processing
- Autoregressive Decoding
- KV Cache
- Key-Value Cache
- Attention Cache
- PagedAttention
- Paged Attention
- Paged KV Cache
- Prefix Caching
- Automatic Prefix Caching
- KV Prefix Reuse
- KV Cache Offloading
- KV Cache Tiering
- Hierarchical KV Cache
description: 'What happens during one request and where its attention state lives: the two inference phases, the
  KV cache they build, and how that cache is paged, reused across requests and offloaded.'
tags:
- ai-engineering
- compute
- inference
- serving
parent: /ai-engineering/compute/serving.md
related:
- /ai-engineering/compute/serving/batching-and-scheduling.md
- /ai-engineering/compute/serving/serving-metrics.md
- /ai-engineering/models/llm-architecture.md
- /ai-engineering/compute/serving/kernels-and-decoding.md
- /ai-engineering/context/prompt-caching.md
status: draft
sources:
- id: modular-inference
  resource: https://handbook.modular.com/llm-inference-basics/how-does-llm-inference-work/
  title: How does an LLM work?
  author: Modular
- id: hf-cache
  resource: https://huggingface.co/docs/transformers/main/cache_explanation
  title: How caching works
  author: Hugging Face
- id: modular-offloading
  resource: https://handbook.modular.com/inference-optimization/kv-cache-offloading/
  title: KV cache offloading
  author: Modular
- id: pagedattention
  resource: https://arxiv.org/abs/2309.06180
  title: Efficient Memory Management for Large Language Model Serving with PagedAttention
  author: Woosuk Kwon et al.
- id: vllm-prefix
  resource: https://docs.vllm.ai/en/latest/features/automatic_prefix_caching/
  title: Automatic Prefix Caching
  author: vLLM
- id: hf-cache-strategies
  resource: https://huggingface.co/docs/transformers/main/kv_cache
  title: Cache strategies
  author: Hugging Face
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-18T12:00:00+04:00'
---

What happens during one request, and where its attention state lives. Prefill and decode build and read the KV cache; paging, prefix caching and offloading manage it.

## Prefill and Decode

The two inference phases process a known prompt in parallel, then generate a dependent output sequence token by token.

### Mechanism

**Prefill** processes the known prompt, builds its [KV cache](/ai-engineering/compute/serving/prefill-decode-and-kv-cache.md#kv-cache), and produces the distribution used to sample the first output token. Prompt positions can be computed in parallel within each layer while a causal mask prevents attention to future positions.

**Decode** repeatedly processes the newly sampled token using the cached keys and values, then samples the next token. An ordinary autoregressive sequence therefore has a dependency between successive generation steps.[^modular-inference]

### Performance implications

Long prefills often have enough parallel work to be compute-bound. Small-batch decode often spends more time reading weights and cached state than doing arithmetic. These are workload-dependent tendencies: large batches, long contexts, architecture and hardware can change the bottleneck.

Prefill largely influences time to first token; decode influences time between output tokens. Client-observed timings also include queues, transport and serialization. See [Serving Metrics](/ai-engineering/compute/serving/serving-metrics.md).

A long prefill can interrupt streaming decode on shared hardware. [Chunked prefill](/ai-engineering/compute/serving/batching-and-scheduling.md#chunked-prefill) limits its scheduling quantum; [disaggregation](/ai-engineering/compute/serving/batching-and-scheduling.md#prefilldecode-disaggregation) assigns the phases to separate worker pools.[^modular-inference]

## KV Cache

Cached attention keys and values avoid recomputing earlier tokens while making sequence length and concurrency consume serving memory.

### Mechanism

In causal Transformer attention, a past token's keys and values do not change when future tokens arrive. Store them once per attention layer, then reuse them at each decode step. New tokens append new K/V entries. The current query still attends over the retained history; caching does not make that attention work disappear.[^hf-cache]

### Memory model

For uniform, full-attention layers with equal key/value head dimensions, the unsharded payload is approximately:

```text
KV bytes = 2 × layers × KV heads × head dimension
             × bytes per element × total retained tokens across requests
```

Use **KV heads**, not query heads, for [GQA/MQA](/ai-engineering/models/llm-architecture.md#serving-view-grouped-query-and-multi-query-attention). This estimate excludes allocator padding, metadata and distributed replication. Sliding-window, latent-attention and hybrid architectures need different accounting.[^hf-cache][^modular-offloading]

**Calculated example:** 32 layers × 8 KV heads × 128 dimensions × 2 bytes × 2 gives 128 KiB per retained token. An 8,192-token request needs about 1 GiB; 32 such requests need about 32 GiB, before overhead.

### Related optimizations

[Paging](/ai-engineering/compute/serving/prefill-decode-and-kv-cache.md#pagedattention) reduces allocation waste; [prefix caching](/ai-engineering/compute/serving/prefill-decode-and-kv-cache.md#prefix-caching) reuses state across requests; [offloading](/ai-engineering/compute/serving/prefill-decode-and-kv-cache.md#kv-cache-offloading) changes its storage tier; [quantization](/ai-engineering/compute/serving/kernels-and-decoding.md#llm-quantization) changes its representation. Ordinary within-request KV caching and cross-request prefix reuse are distinct.

## PagedAttention

A block table maps logical token positions to noncontiguous KV blocks, reducing allocation waste and enabling flexible sharing.

### Mechanism

A request's [KV cache](/ai-engineering/compute/serving/prefill-decode-and-kv-cache.md#kv-cache) grows as it generates tokens. Reserving a contiguous region for its maximum possible length wastes memory and creates fragmentation.

PagedAttention divides KV storage into fixed-size blocks. A block table maps the sequence's logical positions to physical blocks that need not be adjacent. Attention kernels follow that mapping, and the allocator adds blocks as needed. Read-only blocks can be shared; branching generation can use copy-on-write.[^pagedattention]

### Benefit and cost

Less reserved and fragmented memory leaves room for more live sequences, which can improve serving throughput. The system pays for block tables, indirection and block-aware kernels; partially filled final blocks still waste some space.

Paging manages **where** exact KV entries live. It does not inherently reduce their numeric precision, select fewer tokens to attend to, or move them to CPU memory. CPU/disk transfer is [offloading](/ai-engineering/compute/serving/prefill-decode-and-kv-cache.md#kv-cache-offloading).

### Relation to FlashAttention

[FlashAttention](/ai-engineering/compute/serving/kernels-and-decoding.md#flashattention) reduces attention's memory traffic through tiling and on-chip computation. PagedAttention addresses KV layout and allocation. These ideas can coexist; implementation names do not imply mutually exclusive attention algorithms.[^pagedattention]

## Prefix Caching

Reuse stored KV state for a matching prompt prefix to skip repeated prefill computation across requests.

### Mechanism

After a prompt prefix has been processed, retain its KV blocks. A later request with the same compatible token prefix can reuse those blocks and prefill only the uncached suffix. Long shared system prompts, documents and growing conversation histories are natural workloads.[^vllm-prefix]

This is the server-side mechanism behind much [Prompt Caching](/ai-engineering/context/prompt-caching.md). That existing concept focuses on prompt layout and harness economics; this one describes inference execution.

### Boundaries

Reuse requires a matching prefix and compatible model state. Similar meaning or a repeated substring later in the prompt is insufficient. Moving changing content earlier can invalidate reuse for everything following it.

Prefix caching skips repeated **prefill**. It does not remove the work of generating the answer or attending to retained context during decode. A workload dominated by long outputs or unique prompts can therefore benefit little.[^vllm-prefix]

### Serving implications

Cache entries occupy memory that could hold active requests, and replicas have their own cache state. [Inference routing](/ai-engineering/compute/serving/batching-and-scheduling.md#cache-aware-inference-routing) must balance sending a request to a warm worker against waiting in that worker's queue. [Offloading](/ai-engineering/compute/serving/prefill-decode-and-kv-cache.md#kv-cache-offloading) can extend retention into cheaper memory tiers.

## KV Cache Offloading

Moving KV state to CPU memory or storage trades GPU residency for transfer work and potentially avoids later recomputation.

### Two related mechanisms

**Retention tiering:** move inactive or evicted prefix blocks from GPU memory to CPU RAM or slower storage. Reload them when a later request reuses that prefix. This can retain more reusable state than GPU memory alone allows.[^modular-offloading]

**Active-cache offloading:** keep much of an ongoing request's KV state on CPU and transfer the currently needed layer to the GPU. Hugging Face documents layerwise offloading with asynchronous prefetch and eviction.[^hf-cache-strategies]

The first mainly preserves reusable history between uses; the second can let an active generation fit in limited GPU memory.

### When the trade pays

Offloading exchanges scarce GPU capacity for copy bandwidth, latency and storage management. Restoring a large, expensive prefix can beat recomputing it. Repeatedly transferring active state can slow decode when the interconnect cannot keep up.

**Decision rule:** compare transfer plus lookup time with the computation avoided, and include whether the freed GPU memory enables useful extra concurrency. Offloading is not inherently a speedup.[^modular-offloading][^hf-cache-strategies]

### Boundaries

KV offloading moves attention state; weight offloading moves model parameters. [Quantization](/ai-engineering/compute/serving/kernels-and-decoding.md#llm-quantization) reduces representation size. [Paging](/ai-engineering/compute/serving/prefill-decode-and-kv-cache.md#pagedattention) changes allocation layout without inherently moving state off-device.

[^modular-inference]: Modular, [How does an LLM work?](https://handbook.modular.com/llm-inference-basics/how-does-llm-inference-work/).
[^hf-cache]: Hugging Face, [How caching works](https://huggingface.co/docs/transformers/main/cache_explanation).
[^modular-offloading]: Modular, [KV cache offloading](https://handbook.modular.com/inference-optimization/kv-cache-offloading/).
[^pagedattention]: Woosuk Kwon et al., [Efficient Memory Management for Large Language Model Serving with PagedAttention](https://arxiv.org/abs/2309.06180).
[^vllm-prefix]: vLLM, [Automatic Prefix Caching](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching/).
[^hf-cache-strategies]: Hugging Face, [Cache strategies](https://huggingface.co/docs/transformers/main/kv_cache).

---
type: Concept
title: "Prefix Caching"
aliases:
- "Automatic Prefix Caching"
- "KV Prefix Reuse"
description: "Reuse stored KV state for a matching prompt prefix to skip repeated prefill computation across requests."
tags:
- ai-engineering
- compute
- inference
- serving
parent: /ai-engineering/compute/serving.md
related:
- /ai-engineering/compute/serving/kv-cache.md
- /ai-engineering/compute/serving/paged-attention.md
- /ai-engineering/compute/serving/kv-cache-offloading.md
- /ai-engineering/compute/serving/inference-routing.md
- /ai-engineering/context/prompt-caching.md
sources:
- id: vllm-prefix
  resource: https://docs.vllm.ai/en/latest/features/automatic_prefix_caching/
  title: "Automatic Prefix Caching"
  author: "vLLM"
generated:
  by: codex/gpt-6
  at: '2026-10-22T13:46:52+04:00'
---

## Mechanism

After a prompt prefix has been processed, retain its KV blocks. A later request with the same compatible token prefix can reuse those blocks and prefill only the uncached suffix. Long shared system prompts, documents and growing conversation histories are natural workloads.[^vllm-prefix]

This is the server-side mechanism behind much [Prompt Caching](/ai-engineering/context/prompt-caching.md). That existing concept focuses on prompt layout and harness economics; this one describes inference execution.

## Boundaries

Reuse requires a matching prefix and compatible model state. Similar meaning or a repeated substring later in the prompt is insufficient. Moving changing content earlier can invalidate reuse for everything following it.

Prefix caching skips repeated **prefill**. It does not remove the work of generating the answer or attending to retained context during decode. A workload dominated by long outputs or unique prompts can therefore benefit little.[^vllm-prefix]

## Serving implications

Cache entries occupy memory that could hold active requests, and replicas have their own cache state. [Inference routing](/ai-engineering/compute/serving/inference-routing.md) must balance sending a request to a warm worker against waiting in that worker's queue. [Offloading](/ai-engineering/compute/serving/kv-cache-offloading.md) can extend retention into cheaper memory tiers.

[^vllm-prefix]: vLLM, [Automatic Prefix Caching](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching/).

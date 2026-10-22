---
type: Concept
title: "Prefill and Decode"
aliases:
- "Prompt Processing"
- "Autoregressive Decoding"
description: "The two inference phases process a known prompt in parallel, then generate a dependent output sequence token by token."
tags:
- ai-engineering
- compute
- inference
- serving
parent: /ai-engineering/compute/serving.md
related:
- /ai-engineering/compute/serving/kv-cache.md
- /ai-engineering/compute/serving/chunked-prefill.md
- /ai-engineering/compute/serving/prefill-decode-disaggregation.md
- /ai-engineering/compute/serving/serving-metrics.md
sources:
- id: modular-inference
  resource: https://handbook.modular.com/llm-inference-basics/how-does-llm-inference-work/
  title: "How does an LLM work?"
  author: "Modular"
generated:
  by: codex/gpt-6
  at: '2026-10-22T13:46:52+04:00'
---

## Mechanism

**Prefill** processes the known prompt, builds its [KV cache](/ai-engineering/compute/serving/kv-cache.md), and produces the distribution used to sample the first output token. Prompt positions can be computed in parallel within each layer while a causal mask prevents attention to future positions.

**Decode** repeatedly processes the newly sampled token using the cached keys and values, then samples the next token. An ordinary autoregressive sequence therefore has a dependency between successive generation steps.[^modular-inference]

## Performance implications

Long prefills often have enough parallel work to be compute-bound. Small-batch decode often spends more time reading weights and cached state than doing arithmetic. These are workload-dependent tendencies: large batches, long contexts, architecture and hardware can change the bottleneck.

Prefill largely influences time to first token; decode influences time between output tokens. Client-observed timings also include queues, transport and serialization. See [Serving Metrics](/ai-engineering/compute/serving/serving-metrics.md).

A long prefill can interrupt streaming decode on shared hardware. [Chunked prefill](/ai-engineering/compute/serving/chunked-prefill.md) limits its scheduling quantum; [disaggregation](/ai-engineering/compute/serving/prefill-decode-disaggregation.md) assigns the phases to separate worker pools.[^modular-inference]

[^modular-inference]: Modular, [How does an LLM work?](https://handbook.modular.com/llm-inference-basics/how-does-llm-inference-work/).

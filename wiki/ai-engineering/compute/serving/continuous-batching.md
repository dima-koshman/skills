---
type: Concept
title: "Continuous Batching"
aliases:
- "In-flight Batching"
- "Iteration-level Scheduling"
description: "The server updates the active request batch between generation iterations so completed requests leave and new work can enter."
tags:
- ai-engineering
- compute
- inference
- serving
parent: /ai-engineering/compute/serving.md
related:
- /ai-engineering/compute/serving/chunked-prefill.md
- /ai-engineering/compute/serving/kv-cache.md
- /ai-engineering/compute/serving/paged-attention.md
- /ai-engineering/compute/serving/serving-metrics.md
sources:
- id: orca
  resource: https://www.usenix.org/conference/osdi22/presentation/yu
  title: "Orca: A Distributed Serving System for Transformer-Based Generative Models"
  author: "Gyeong-In Yu et al."
generated:
  by: codex/gpt-6
  at: '2026-10-22T13:46:52+04:00'
---

## Mechanism

Conventional request-level batching groups requests and executes that group to completion. Different output lengths leave capacity unused as shorter requests finish. Continuous batching reschedules at generation-iteration boundaries: completed requests leave and eligible requests join.

Orca's iteration-level scheduling is a foundational implementation. Its scheduler invokes one model iteration at a time rather than committing to the lifetime of an entire request batch.[^orca]

## Static, dynamic and continuous

- **Static batching:** collect a fixed group and process it together.
- **Dynamic batching:** form request batches at runtime, often with a short waiting window.
- **Continuous batching:** change membership between iterations of ongoing generation.

Product terminology varies; the defining property is the scheduling boundary.

## When it helps and what it costs

Mixed output lengths and sustained concurrent traffic provide opportunities to keep the device busy. The server must still manage KV memory and decide how much new work to admit. Adding every available request can worsen individual latency.

Continuous batching does not itself specify how to interleave long prefills with decode. [Chunked Prefill](/ai-engineering/compute/serving/chunked-prefill.md) addresses that separate scheduling decision. Evaluate aggregate throughput together with TTFT and streaming latency.[^orca]

[^orca]: Gyeong-In Yu et al., [Orca: A Distributed Serving System for Transformer-Based Generative Models](https://www.usenix.org/conference/osdi22/presentation/yu).

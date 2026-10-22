---
type: Concept
title: "Cache-aware Inference Routing"
aliases:
- "KV-aware Routing"
- "Prefix-aware Routing"
- "Serving Load Balancing"
description: "Choose serving workers using prefix locality, queueing and KV pressure rather than only request counts."
tags:
- ai-engineering
- compute
- inference
- serving
parent: /ai-engineering/compute/serving.md
related:
- /ai-engineering/compute/serving/data-parallelism.md
- /ai-engineering/compute/serving/prefix-caching.md
- /ai-engineering/compute/serving/kv-cache-offloading.md
- /ai-engineering/compute/serving/prefill-decode-disaggregation.md
- /ai-engineering/compute/serving/serving-metrics.md
- /ai-engineering/harness/model-routing.md
sources:
- id: modular-routing
  resource: https://handbook.modular.com/inference-optimization/inference-routing/
  title: "Inference routing"
  author: "Modular"
generated:
  by: codex/gpt-6
  at: '2026-10-22T13:46:52+04:00'
---

## Mechanism

Replicas do not necessarily have the same cost for a request: one may already hold most of its prompt's KV state while another must recompute it. A cache-aware router considers reusable prefix state alongside queues, active decode work and KV memory pressure.

This selects a **worker for a model**. [Model Routing](/ai-engineering/harness/model-routing.md) selects which model should solve the task.[^modular-routing]

## The central trade-off

Always choosing the warmest worker can overload it; always choosing the shortest queue can destroy cache locality. A useful policy estimates time to service, including both waiting and uncached prompt processing.

Raw request counts are weak load estimates because prompt length, output length and KV occupancy vary. Static affinity can help repeated conversations, but must tolerate worker failure and changing load.[^modular-routing]

## Example and evaluation

A follow-up with a long shared history might finish sooner on a moderately busy warm worker than an idle cold one. If the warm queue grows enough, that preference should reverse.

Measure cache hits, TTFT tails and useful throughput together. A higher hit rate alone does not prove better service. Separate worker selection from admission control: a router cannot remove overload simply by moving requests among saturated workers.

[^modular-routing]: Modular, [Inference routing](https://handbook.modular.com/inference-optimization/inference-routing/).

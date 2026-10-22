---
type: Concept
title: "LLM Serving Metrics"
aliases:
- "TTFT"
- "ITL"
- "TPOT"
- "Serving Goodput"
description: "Latency, throughput and goodput measure different serving goals and must be compared under a specified workload and load."
tags:
- ai-engineering
- compute
- inference
- serving
parent: /ai-engineering/compute/serving.md
related:
- /ai-engineering/compute/serving/prefill-decode.md
- /ai-engineering/compute/serving/continuous-batching.md
- /ai-engineering/compute/serving/prefill-decode-disaggregation.md
- /ai-engineering/compute/serving/inference-routing.md
sources:
- id: modular-metrics
  resource: https://handbook.modular.com/llm-inference-basics/llm-inference-metrics/
  title: "Key metrics for LLM inference"
  author: "Modular"
- id: distserve
  resource: https://arxiv.org/abs/2401.09670
  title: "DistServe: Disaggregating Prefill and Decoding for Goodput-optimized Large Language Model Serving"
  author: "Yinmin Zhong et al."
generated:
  by: codex/gpt-6
  at: '2026-10-22T13:46:52+04:00'
---

## What to measure

| Metric | Meaning |
| --- | --- |
| Time to first token (TTFT) | Request submission to first visible output token; includes queueing and other overhead at the chosen measurement boundary. |
| Inter-token latency (ITL) | Gap between consecutive output tokens; percentiles expose streaming stalls. |
| Time per output token (TPOT) | Common per-request average: (last-token time − first-token time) / (output tokens − 1), for outputs longer than one token. |
| End-to-end latency | Submission to completion of the response. |
| Throughput | Completed requests/s or input/output tokens/s across the server; specify which. |
| Goodput | Work completed while satisfying stated latency or other service objectives. |

Definitions vary between benchmark tools, especially token timing under buffered streaming. Document the boundary and aggregation method.[^modular-metrics][^distserve]

## How to compare

Report prompt/output length distributions, offered request rate, concurrency, cache-hit conditions, model precision and hardware. Compare tail latency as well as means. Aggregate tokens/s and one user's tokens/s answer different questions.

A larger batch can increase total throughput while delaying individuals. Disaggregation can improve goodput under TTFT and TPOT constraints without establishing a universal raw-throughput advantage. Treat “faster” as incomplete until the workload and objective are specified.[^modular-metrics][^distserve]

[^modular-metrics]: Modular, [Key metrics for LLM inference](https://handbook.modular.com/llm-inference-basics/llm-inference-metrics/).
[^distserve]: Yinmin Zhong et al., [DistServe: Disaggregating Prefill and Decoding for Goodput-optimized Large Language Model Serving](https://arxiv.org/abs/2401.09670).

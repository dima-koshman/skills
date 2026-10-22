---
type: Concept
title: "Chunked Prefill"
description: "Splitting prompt processing into bounded chunks lets a scheduler interleave new prompts with ongoing decode work."
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
- /ai-engineering/compute/serving/serving-metrics.md
sources:
- id: sarathi
  resource: https://arxiv.org/abs/2403.02310
  title: "Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve"
  author: "Amey Agrawal et al."
- id: vllm-tuning
  resource: https://docs.vllm.ai/en/latest/configuration/optimization/
  title: "Optimization and Tuning"
  author: "vLLM"
generated:
  by: codex/gpt-6
  at: '2026-10-22T13:46:52+04:00'
---

## Mechanism

A long prefill can monopolize a shared worker and delay tokens for requests already decoding. Chunked prefill divides prompt processing into smaller pieces, preserving the intermediate KV state between chunks. The scheduler can fit chunks alongside decode work rather than running the whole prompt uninterrupted.

Sarathi-Serve combines chunked prefills with scheduling designed to avoid stalling ongoing decodes.[^sarathi]

## Tuning trade-off

Small chunks bound how long new prompt work occupies an iteration, helping streaming latency. Larger chunks can make prompt processing more efficient and finish prefills sooner. Too-small chunks add scheduling overhead and may reduce compute efficiency; aggressive decode priority can increase prompt waiting.

vLLM's current tuning guide describes decode-prioritized scheduling under a token budget: pending decode work is scheduled first, with remaining capacity used for prefill chunks. Its implementation defaults and flags can change.[^vllm-tuning]

## Relationship to other techniques

[Continuous batching](/ai-engineering/compute/serving/continuous-batching.md) controls batch membership; chunking controls the granularity of prompt work. [Disaggregation](/ai-engineering/compute/serving/prefill-decode-disaggregation.md) separates phases onto workers instead. Both approaches target prefill/decode interference, with different resource and operational costs.

[^sarathi]: Amey Agrawal et al., [Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve](https://arxiv.org/abs/2403.02310).
[^vllm-tuning]: vLLM, [Optimization and Tuning](https://docs.vllm.ai/en/latest/configuration/optimization/).

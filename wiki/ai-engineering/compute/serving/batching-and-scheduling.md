---
type: Concept
title: Batching and Scheduling
aliases:
- Continuous Batching
- In-flight Batching
- Iteration-level Scheduling
- Chunked Prefill
- Prefill–Decode Disaggregation
- PD Disaggregation
- Disaggregated Prefilling
- Split-phase Serving
- Cache-aware Inference Routing
- KV-aware Routing
- Prefix-aware Routing
- Serving Load Balancing
description: 'How a server decides what runs next: batch membership between iterations, chunked prompts, separate
  prefill and decode workers, and choosing a worker for each request.'
tags:
- ai-engineering
- compute
- inference
- serving
parent: /ai-engineering/compute/serving.md
related:
- /ai-engineering/compute/serving/prefill-decode-and-kv-cache.md
- /ai-engineering/compute/serving/serving-metrics.md
- /ai-engineering/compute/serving/parallelism.md
- /ai-engineering/harness/model-routing.md
status: draft
sources:
- id: orca
  resource: https://www.usenix.org/conference/osdi22/presentation/yu
  title: 'Orca: A Distributed Serving System for Transformer-Based Generative Models'
  author: Gyeong-In Yu et al.
- id: sarathi
  resource: https://arxiv.org/abs/2403.02310
  title: Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve
  author: Amey Agrawal et al.
- id: vllm-tuning
  resource: https://docs.vllm.ai/en/latest/configuration/optimization/
  title: Optimization and Tuning
  author: vLLM
- id: distserve
  resource: https://arxiv.org/abs/2401.09670
  title: 'DistServe: Disaggregating Prefill and Decoding for Goodput-optimized Large Language Model Serving'
  author: Yinmin Zhong et al.
- id: vllm-disagg
  resource: https://docs.vllm.ai/en/latest/features/disagg_prefill/
  title: Disaggregated Prefilling
  author: vLLM
- id: modular-routing
  resource: https://handbook.modular.com/inference-optimization/inference-routing/
  title: Inference routing
  author: Modular
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-18T12:00:00+04:00'
---

How a server decides what runs next. Continuous batching changes who is in the batch, chunked prefill bounds how much prompt work enters an iteration, disaggregation moves the phases to separate workers, and cache-aware routing picks the worker.

## Continuous Batching

The server updates the active request batch between generation iterations so completed requests leave and new work can enter.

### Mechanism

Conventional request-level batching groups requests and executes that group to completion. Different output lengths leave capacity unused as shorter requests finish. Continuous batching reschedules at generation-iteration boundaries: completed requests leave and eligible requests join.

Orca's iteration-level scheduling is a foundational implementation. Its scheduler invokes one model iteration at a time rather than committing to the lifetime of an entire request batch.[^orca]

### Static, dynamic and continuous

- **Static batching:** collect a fixed group and process it together.
- **Dynamic batching:** form request batches at runtime, often with a short waiting window.
- **Continuous batching:** change membership between iterations of ongoing generation.

Product terminology varies; the defining property is the scheduling boundary.

### When it helps and what it costs

Mixed output lengths and sustained concurrent traffic provide opportunities to keep the device busy. The server must still manage KV memory and decide how much new work to admit. Adding every available request can worsen individual latency.

Continuous batching does not itself specify how to interleave long prefills with decode. [Chunked Prefill](/ai-engineering/compute/serving/batching-and-scheduling.md#chunked-prefill) addresses that separate scheduling decision. Evaluate aggregate throughput together with TTFT and streaming latency.[^orca]

## Chunked Prefill

Splitting prompt processing into bounded chunks lets a scheduler interleave new prompts with ongoing decode work.

### Mechanism

A long prefill can monopolize a shared worker and delay tokens for requests already decoding. Chunked prefill divides prompt processing into smaller pieces, preserving the intermediate KV state between chunks. The scheduler can fit chunks alongside decode work rather than running the whole prompt uninterrupted.

Sarathi-Serve combines chunked prefills with scheduling designed to avoid stalling ongoing decodes.[^sarathi]

### Tuning trade-off

Small chunks bound how long new prompt work occupies an iteration, helping streaming latency. Larger chunks can make prompt processing more efficient and finish prefills sooner. Too-small chunks add scheduling overhead and may reduce compute efficiency; aggressive decode priority can increase prompt waiting.

vLLM's current tuning guide describes decode-prioritized scheduling under a token budget: pending decode work is scheduled first, with remaining capacity used for prefill chunks. Its implementation defaults and flags can change.[^vllm-tuning]

### Relationship to other techniques

[Continuous batching](/ai-engineering/compute/serving/batching-and-scheduling.md#continuous-batching) controls batch membership; chunking controls the granularity of prompt work. [Disaggregation](/ai-engineering/compute/serving/batching-and-scheduling.md#prefilldecode-disaggregation) separates phases onto workers instead. Both approaches target prefill/decode interference, with different resource and operational costs.

## Prefill–Decode Disaggregation

Separate worker pools perform prompt processing and token generation, transferring KV state between independently tuned phases.

### Mechanism

Prefill workers process prompts and hand their KV state to decode workers, which stream subsequent tokens. Separate pools can use different hardware allocations, parallelism degrees and scheduling policies.

The goal is to prevent long prompt processing from interrupting ongoing decode and to tune time to first token separately from streaming latency. DistServe studies this through **goodput**: how much traffic meets both phase-specific latency objectives.[^distserve]

### Trade-offs

KV handoff consumes bandwidth and adds a synchronization point. The deployment also needs routing, capacity balance between pools, transfer backpressure and failure handling. If transfer time dominates or one pool is underused, separation can lose to colocated serving.

vLLM's documentation explicitly warns that its disaggregated-prefill feature does not improve throughput. That is compatible with DistServe's goodput results: meeting latency objectives and maximizing unconstrained tokens/s are different goals.[^vllm-disagg][^distserve]

### Alternative and boundary

[Chunked Prefill](/ai-engineering/compute/serving/batching-and-scheduling.md#chunked-prefill) mitigates interference on shared workers without a separate decode pool. Compare it before accepting disaggregation's operational cost.

This is a split between **inference phases**, not [pipeline parallelism](/ai-engineering/compute/serving/parallelism.md#pipeline-parallelism), which splits a model's layers across devices.

## Cache-aware Inference Routing

Choose serving workers using prefix locality, queueing and KV pressure rather than only request counts.

### Mechanism

Replicas do not necessarily have the same cost for a request: one may already hold most of its prompt's KV state while another must recompute it. A cache-aware router considers reusable prefix state alongside queues, active decode work and KV memory pressure.

This selects a **worker for a model**. [Model Routing](/ai-engineering/harness/model-routing.md) selects which model should solve the task.[^modular-routing]

### The central trade-off

Always choosing the warmest worker can overload it; always choosing the shortest queue can destroy cache locality. A useful policy estimates time to service, including both waiting and uncached prompt processing.

Raw request counts are weak load estimates because prompt length, output length and KV occupancy vary. Static affinity can help repeated conversations, but must tolerate worker failure and changing load.[^modular-routing]

### Example and evaluation

A follow-up with a long shared history might finish sooner on a moderately busy warm worker than an idle cold one. If the warm queue grows enough, that preference should reverse.

Measure cache hits, TTFT tails and useful throughput together. A higher hit rate alone does not prove better service. Separate worker selection from admission control: a router cannot remove overload simply by moving requests among saturated workers.

[^orca]: Gyeong-In Yu et al., [Orca: A Distributed Serving System for Transformer-Based Generative Models](https://www.usenix.org/conference/osdi22/presentation/yu).
[^sarathi]: Amey Agrawal et al., [Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve](https://arxiv.org/abs/2403.02310).
[^vllm-tuning]: vLLM, [Optimization and Tuning](https://docs.vllm.ai/en/latest/configuration/optimization/).
[^distserve]: Yinmin Zhong et al., [DistServe: Disaggregating Prefill and Decoding for Goodput-optimized Large Language Model Serving](https://arxiv.org/abs/2401.09670).
[^vllm-disagg]: vLLM, [Disaggregated Prefilling](https://docs.vllm.ai/en/latest/features/disagg_prefill/).
[^modular-routing]: Modular, [Inference routing](https://handbook.modular.com/inference-optimization/inference-routing/).

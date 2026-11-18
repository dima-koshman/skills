---
type: Tool
title: vLLM
description: An open-source LLM inference and serving library built around KV cache management, which runs on its
  own or as a backend under a general model server such as Triton.
resource: https://docs.vllm.ai/
tags:
- ai-engineering
- compute
- inference
- serving
parent: /ai-engineering/compute/serving.md
related:
- /ai-engineering/compute/serving/triton-inference-server.md
- /ai-engineering/compute/serving/prefill-decode-and-kv-cache.md
- /ai-engineering/compute/serving/batching-and-scheduling.md
- /ai-engineering/compute/gpu-sharing/mps.md
- /ai-engineering/compute/software-stack/max.md
sources:
- id: vllm-docs
  resource: https://docs.vllm.ai/en/latest/
  title: vLLM documentation
  author: vLLM
- id: vllm-paper
  resource: https://arxiv.org/abs/2309.06180
  title: Efficient Memory Management for Large Language Model Serving with PagedAttention
  author: Woosuk Kwon, Zhuohan Li, Siyuan Zhuang, Ying Sheng, Lianmin Zheng, Cody Hao Yu, Joseph E. Gonzalez, Hao Zhang, Ion Stoica
  last_modified: '2023-09-12T12:50:04Z'
- id: vllm-engine-args
  resource: https://docs.vllm.ai/en/v0.7.3/serving/engine_args.html
  title: Engine Arguments (v0.7.3)
  author: vLLM
- id: vllm-server
  resource: https://docs.vllm.ai/en/v0.7.3/serving/openai_compatible_server.html
  title: OpenAI-Compatible Server
  author: vLLM
- id: triton-vllm-backend
  resource: https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/vllm_backend/README.html
  title: vLLM Backend
  author: NVIDIA
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-05T14:58:40+04:00'
---

vLLM is a library for LLM inference and serving, started in the Sky Computing Lab at UC Berkeley.[^vllm-docs] Its
starting point was KV cache memory: the 2023 SOSP paper showed that managing it like virtual memory pages cuts
waste and allows larger batches, with 2-4x throughput at similar latency against the systems it
tested.[^vllm-paper]

## What it owns

vLLM is where the LLM-specific scheduling lives. This is what separates an inference engine from a general model
server:

- KV memory, through [PagedAttention](/ai-engineering/compute/serving/prefill-decode-and-kv-cache.md#pagedattention).[^vllm-docs]
- [Continuous batching](/ai-engineering/compute/serving/batching-and-scheduling.md#continuous-batching),
  [chunked prefill](/ai-engineering/compute/serving/batching-and-scheduling.md#chunked-prefill) and
  [prefix caching](/ai-engineering/compute/serving/prefill-decode-and-kv-cache.md#prefix-caching).[^vllm-docs]
- Kernel choice, including [FlashAttention](/ai-engineering/compute/serving/kernels-and-decoding.md#flashattention), plus
  [CUDA graphs](/ai-engineering/compute/serving/kernels-and-decoding.md#cuda-graphs) and
  [quantization](/ai-engineering/compute/serving/kernels-and-decoding.md#llm-quantization) formats.[^vllm-docs]

## Is it lower level than Triton?

Yes in the stack, but it is not a low-level tool. When the two are combined, Triton is the server and vLLM is the
engine underneath: requests are placed on vLLM's async engine, which does the batching and
paging.[^triton-vllm-backend] Still, vLLM can stand alone, since it ships its own OpenAI-compatible
server.[^vllm-server]

The more useful split is general versus LLM-specific:

| Layer | Example | Unit it schedules |
| --- | --- | --- |
| Cluster | [Run:ai](/ai-engineering/compute/gpu-sharing/run-ai.md), Kubernetes | Pods onto GPUs |
| Model server | [Triton](/ai-engineering/compute/serving/triton-inference-server.md) | Requests onto model instances |
| Inference engine | vLLM, [MAX](/ai-engineering/compute/software-stack/max.md) | Tokens and KV memory within a batch |
| Kernels | FlashAttention, CUDA | Threads on the GPU |

This table is our framing, not a standard taxonomy. MAX's position is approximate, since it also ships a server.

## Sharing a GPU

The memory setting `--gpu-memory-utilization` is per instance. To put two instances on one GPU, the docs suggest
0.5 each; the default is 0.9.[^vllm-engine-args] That value comes from older v0.7.3 docs, so check it for your
version.

The setting only divides memory. Two instances are two processes, so without
[MPS](/ai-engineering/compute/gpu-sharing/mps.md) they still time-slice the GPU's compute.

[^vllm-docs]: vLLM documentation, home page.
[^vllm-paper]: Kwon et al., SOSP 2023.
[^vllm-engine-args]: vLLM documentation, Engine Arguments.
[^vllm-server]: vLLM documentation, OpenAI-Compatible Server.
[^triton-vllm-backend]: NVIDIA Triton Inference Server documentation, vLLM Backend.

---
type: Concept
title: "LLM Quantization"
aliases:
- "Low-precision Inference"
- "Post-training Quantization"
- "PTQ"
description: "Represent weights, activations or KV state with fewer bits to reduce memory and potentially accelerate supported inference kernels."
tags:
- ai-engineering
- compute
- inference
- serving
parent: /ai-engineering/compute/serving.md
related:
- /ai-engineering/compute/serving/kv-cache.md
- /ai-engineering/compute/serving/grouped-query-attention.md
- /ai-engineering/compute/serving/tensor-parallelism.md
- /ai-engineering/compute/serving/serving-metrics.md
sources:
- id: modular-quantization
  resource: https://handbook.modular.com/model-preparation/llm-quantization/
  title: "LLM quantization"
  author: "Modular"
- id: awq
  resource: https://arxiv.org/abs/2306.00978
  title: "AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration"
  author: "Ji Lin et al."
- id: smoothquant
  resource: https://arxiv.org/abs/2211.10438
  title: "SmoothQuant: Accurate and Efficient Post-Training Quantization for Large Language Models"
  author: "Guangxuan Xiao et al."
- id: vllm-kv-quant
  resource: https://docs.vllm.ai/en/latest/features/quantization/quantized_kvcache/
  title: "Quantized KV Cache"
  author: "vLLM"
generated:
  by: codex/gpt-6
  at: '2026-10-22T13:46:52+04:00'
---

## What is quantized?

| Target | Main benefit | Example |
| --- | --- | --- |
| Weights | Smaller checkpoint and fewer weight bytes read | AWQ weight-only quantization; W4A16 means 4-bit weights and 16-bit activations. |
| Weights and activations | Smaller operands and access to faster supported arithmetic | SmoothQuant W8A8; suitable FP8 execution paths. |
| KV cache | More retained tokens or concurrent sequences | FP8 KV storage with calibrated scales. |

These are separate choices: low-bit weights do not automatically shrink the KV cache.[^modular-quantization][^awq][^smoothquant][^vllm-kv-quant]

## Mechanism and preparation

Values are mapped into a lower-precision representation, often using scales per tensor, channel or group. Calibration can estimate useful scales and protect difficult value distributions. Post-training quantization transforms an existing checkpoint; quantization-aware training adapts the model during training.

## Trade-offs

Less storage does not guarantee lower latency. Packing, conversion overhead, kernel quality, hardware format support and batch shape determine whether the compressed representation runs faster. Actual memory includes scales, metadata, activations and KV state as well as weights.

Measure quality on the intended workload, including long-context and structured-output behavior where relevant. “4-bit” specifies neither a complete quantization method nor a universal quality level. Keep the unquantized baseline and distinguish memory savings from throughput gains.[^modular-quantization]

[^modular-quantization]: Modular, [LLM quantization](https://handbook.modular.com/model-preparation/llm-quantization/).
[^awq]: Ji Lin et al., [AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration](https://arxiv.org/abs/2306.00978).
[^smoothquant]: Guangxuan Xiao et al., [SmoothQuant: Accurate and Efficient Post-Training Quantization for Large Language Models](https://arxiv.org/abs/2211.10438).
[^vllm-kv-quant]: vLLM, [Quantized KV Cache](https://docs.vllm.ai/en/latest/features/quantization/quantized_kvcache/).

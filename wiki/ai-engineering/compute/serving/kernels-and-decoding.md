---
type: Concept
title: Faster Kernels and Decoding
aliases:
- FlashAttention
- IO-aware Attention
- Kernel Fusion
- Operator Fusion
- Fused Kernels
- CUDA Graphs
- CUDA Graph Replay
- Speculative Decoding
- Speculative Sampling
- Assisted Decoding
- LLM Quantization
- Low-precision Inference
- Post-training Quantization
- PTQ
description: 'Ways to make each generated token cheaper: attention and fused kernels that move less memory, CUDA
  graphs that cut launch overhead, speculative decoding and quantization.'
tags:
- ai-engineering
- compute
- inference
- serving
parent: /ai-engineering/compute/serving.md
related:
- /ai-engineering/compute/serving/prefill-decode-and-kv-cache.md
- /ai-engineering/models/llm-architecture.md
- /ai-engineering/compute/performance-regimes.md
- /ai-engineering/compute/software-stack/compilers.md
- /ai-engineering/compute/serving/batching-and-scheduling.md
- /ai-engineering/compute/software-stack/cuda.md
- /ai-engineering/compute/serving/serving-metrics.md
- /ai-engineering/compute/serving/parallelism.md
status: draft
sources:
- id: flashattention
  resource: https://arxiv.org/abs/2205.14135
  title: 'FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness'
  author: Tri Dao et al.
- id: triton-softmax
  resource: https://triton-lang.org/main/getting-started/tutorials/02-fused-softmax.html
  title: Fused Softmax
  author: Triton
- id: pytorch-cuda-graphs
  resource: https://pytorch.org/blog/accelerating-pytorch-with-cuda-graphs/
  title: Accelerating PyTorch with CUDA Graphs
  author: PyTorch and NVIDIA
- id: vllm-cuda-graphs
  resource: https://docs.vllm.ai/en/latest/design/cuda_graphs/
  title: CUDA Graphs
  author: vLLM
- id: speculative-decoding
  resource: https://arxiv.org/abs/2211.17192
  title: Fast Inference from Transformers via Speculative Decoding
  author: Yaniv Leviathan, Matan Kalman and Yossi Matias
- id: modular-quantization
  resource: https://handbook.modular.com/model-preparation/llm-quantization/
  title: LLM quantization
  author: Modular
- id: awq
  resource: https://arxiv.org/abs/2306.00978
  title: 'AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration'
  author: Ji Lin et al.
- id: smoothquant
  resource: https://arxiv.org/abs/2211.10438
  title: 'SmoothQuant: Accurate and Efficient Post-Training Quantization for Large Language Models'
  author: Guangxuan Xiao et al.
- id: vllm-kv-quant
  resource: https://docs.vllm.ai/en/latest/features/quantization/quantized_kvcache/
  title: Quantized KV Cache
  author: vLLM
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-18T12:00:00+04:00'
---

Ways to make each generated token cheaper. FlashAttention and kernel fusion move less memory, CUDA graphs cut launch overhead, speculative decoding cuts serial target-model passes, and quantization shrinks the bytes.

## FlashAttention

Tiled attention keeps intermediates on chip and avoids materializing the full attention-score matrix in GPU memory.

### Mechanism

A straightforward attention implementation writes a large matrix of pairwise scores to high-bandwidth memory, then reads it again for softmax and value aggregation. FlashAttention tiles the computation, keeping working data in on-chip memory and updating softmax statistics incrementally.

It computes dense attention without materializing the full score matrix in GPU memory. The core idea is reducing data movement across the memory hierarchy, rather than approximating attention.[^flashattention]

### What improves

Lower memory traffic and fewer large intermediate allocations can make attention faster and enable longer sequences. This particularly matters when many query positions are processed, as in prefill and training.

“Exact attention” refers to the mathematical operation rather than bitwise equality across floating-point implementations. Dense attention's pairwise arithmetic still grows quadratically with sequence length; saving intermediate memory does not remove that work.

### Distinctions

[PagedAttention](/ai-engineering/compute/serving/prefill-decode-and-kv-cache.md#pagedattention) manages KV blocks. [GQA](/ai-engineering/models/llm-architecture.md#serving-view-grouped-query-and-multi-query-attention) changes the model's KV-head sharing. FlashAttention changes how attention computation is executed. A serving backend can combine these ideas; the best kernel depends on hardware, shapes and whether the workload is prefill or decode.[^flashattention]

## Kernel Fusion

Execute multiple operations inside one GPU kernel to reduce launch overhead and avoid writing intermediate tensors to global memory.

### Mechanism

Separate GPU operations often write an intermediate result to global memory, then launch another kernel that reads it back. Fusion performs the operations together so intermediate values can remain in registers or on-chip memory.

Softmax illustrates the idea: finding a maximum, subtracting it, exponentiating, reducing and normalizing can avoid repeatedly reading and writing the same row. Triton's tutorial demonstrates a fused implementation for rows that fit the kernel's on-chip working set.[^triton-softmax]

### When it helps

Fusion is valuable for bandwidth-bound sequences of small operations and can reduce launch overhead too. In inference, normalization, activation and related elementwise steps are natural opportunities. Compilers can generate fused kernels; carefully tuned libraries provide others.

### Trade-offs

A larger fused kernel can require more registers or shared memory, lowering occupancy or spilling values back to global memory. Layout constraints and oversized working sets can make fusion slower. “Fewer kernels” is therefore a hypothesis to profile, not sufficient evidence of a speedup.

[FlashAttention](/ai-engineering/compute/serving/kernels-and-decoding.md#flashattention) applies IO-aware computation to attention; [CUDA Graphs](/ai-engineering/compute/serving/kernels-and-decoding.md#cuda-graphs) reduce repeated submission overhead without inherently combining operations.[^triton-softmax]

## CUDA Graphs

Capture and replay a compatible sequence of GPU operations to reduce repeated host dispatch and kernel-launch overhead.

### Mechanism

Instead of having the CPU submit the same sequence of small operations repeatedly, capture a compatible execution into a CUDA graph and replay it. Inputs can change while the captured operation structure and required memory addresses remain suitable for replay.

The primary gain is less Python/framework/driver submission overhead. This is useful when GPU operations are short enough that host dispatch leaves gaps between them.[^pytorch-cuda-graphs]

### Constraints and cost

Graph-safe regions require controlled shapes, memory lifetimes and control flow. Capture has startup cost, and retained buffers consume memory. An inference engine must reconcile variable batch sizes and attention workloads with reusable execution shapes; vLLM documents its serving-specific graph modes.[^pytorch-cuda-graphs][^vllm-cuda-graphs]

A graph does not by itself reduce the mathematical work or fuse its kernels. If runtime is dominated by large matrix multiplication or KV reads, removing host overhead may have limited impact.

### Relation to fusion

[Kernel Fusion](/ai-engineering/compute/serving/kernels-and-decoding.md#kernel-fusion) combines operations to avoid launches and intermediate memory traffic. CUDA graphs replay a sequence more cheaply. They address overlapping but different costs and can be used together.

## Speculative Decoding

A cheap proposer drafts multiple tokens and a target model verifies them together to reduce serial target-model passes.

### Mechanism

A cheaper draft model proposes several tokens. The target model evaluates those candidate positions together, accepts a valid prefix, and corrects the first rejected position. Successful rounds commit multiple tokens per target-model pass, reducing the serial dependency cost of ordinary decode.

The original speculative-sampling algorithm includes acceptance and correction rules that preserve the target distribution. Merely checking whether a draft “looks good” does not provide that guarantee.[^speculative-decoding]

### When it helps

The proposal must be cheap, agreement must be high, and verification must cost less than generating the accepted tokens through separate target passes. This often suits decode workloads with spare parallel compute.

Draft inference, verification and rejected work add overhead. Poor agreement or a target already operating at high utilization can erase the benefit. The right speculation length depends on the proposer, target and workload.

### How to evaluate

Measure accepted tokens per verification round, end-to-end latency and total device cost. Compare with ordinary decoding at the same load and quality settings. “Lossless” means preserving the target sampling distribution under the algorithm's assumptions, not producing the same random sample or guaranteeing bitwise-identical execution.[^speculative-decoding]

## LLM Quantization

Represent weights, activations or KV state with fewer bits to reduce memory and potentially accelerate supported inference kernels.

### What is quantized?

| Target | Main benefit | Example |
| --- | --- | --- |
| Weights | Smaller checkpoint and fewer weight bytes read | AWQ weight-only quantization; W4A16 means 4-bit weights and 16-bit activations. |
| Weights and activations | Smaller operands and access to faster supported arithmetic | SmoothQuant W8A8; suitable FP8 execution paths. |
| KV cache | More retained tokens or concurrent sequences | FP8 KV storage with calibrated scales. |

These are separate choices: low-bit weights do not automatically shrink the KV cache.[^modular-quantization][^awq][^smoothquant][^vllm-kv-quant]

### Mechanism and preparation

Values are mapped into a lower-precision representation, often using scales per tensor, channel or group. Calibration can estimate useful scales and protect difficult value distributions. Post-training quantization transforms an existing checkpoint; quantization-aware training adapts the model during training.

### Trade-offs

Less storage does not guarantee lower latency. Packing, conversion overhead, kernel quality, hardware format support and batch shape determine whether the compressed representation runs faster. Actual memory includes scales, metadata, activations and KV state as well as weights.

Measure quality on the intended workload, including long-context and structured-output behavior where relevant. “4-bit” specifies neither a complete quantization method nor a universal quality level. Keep the unquantized baseline and distinguish memory savings from throughput gains.[^modular-quantization]

[^flashattention]: Tri Dao et al., [FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness](https://arxiv.org/abs/2205.14135).
[^triton-softmax]: Triton, [Fused Softmax](https://triton-lang.org/main/getting-started/tutorials/02-fused-softmax.html).
[^pytorch-cuda-graphs]: PyTorch and NVIDIA, [Accelerating PyTorch with CUDA Graphs](https://pytorch.org/blog/accelerating-pytorch-with-cuda-graphs/).
[^vllm-cuda-graphs]: vLLM, [CUDA Graphs](https://docs.vllm.ai/en/latest/design/cuda_graphs/).
[^speculative-decoding]: Yaniv Leviathan, Matan Kalman and Yossi Matias, [Fast Inference from Transformers via Speculative Decoding](https://arxiv.org/abs/2211.17192).
[^modular-quantization]: Modular, [LLM quantization](https://handbook.modular.com/model-preparation/llm-quantization/).
[^awq]: Ji Lin et al., [AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration](https://arxiv.org/abs/2306.00978).
[^smoothquant]: Guangxuan Xiao et al., [SmoothQuant: Accurate and Efficient Post-Training Quantization for Large Language Models](https://arxiv.org/abs/2211.10438).
[^vllm-kv-quant]: vLLM, [Quantized KV Cache](https://docs.vllm.ai/en/latest/features/quantization/quantized_kvcache/).

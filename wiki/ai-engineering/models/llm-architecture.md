---
type: Concept
title: LLM Architecture
aliases:
- Grouped-Query Attention
- GQA
- Multi-Query Attention
- MQA
description: Design choices inside modern open-weight LLMs — sparsity, attention efficiency, and the empirical tweaks
  — and the two main ways to make them multimodal.
tags:
- ai-engineering
- models
- compute
- inference
- serving
parent: /ai-engineering/models.md
related:
- /ai-engineering/models/providers/claude.md
- /ai-engineering/models/leaderboards.md
- /ai-engineering/compute/serving/prefill-decode-and-kv-cache.md
- /ai-engineering/compute/serving/kernels-and-decoding.md
- /ai-engineering/compute/serving/parallelism.md
status: draft
sources:
- id: ref-1
  resource: https://magazine.sebastianraschka.com/p/the-big-llm-architecture-comparison
  title: magazine.sebastianraschka.com
- id: ref-2
  resource: https://magazine.sebastianraschka.com/p/understanding-multimodal-llms
  title: magazine.sebastianraschka.com
- id: gqa
  resource: https://arxiv.org/abs/2305.13245
  title: 'GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints'
  author: Joshua Ainslie et al.
- id: vllm-cp
  resource: https://docs.vllm.ai/en/latest/serving/context_parallel_deployment/
  title: Context Parallel Deployment
  author: vLLM
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-18T12:00:00+04:00'
note_date: '2026-10-03'
---

References:

- <https://magazine.sebastianraschka.com/p/the-big-llm-architecture-comparison>
- <https://magazine.sebastianraschka.com/p/understanding-multimodal-llms>

Note dated: 2026-10-03.

Under the surface, contemporary LLMs are still the same decoder-only
transformer as GPT-2: token embeddings, stacked attention and feed-forward
blocks, residual connections, normalization. Most of the differences between
model families are efficiency optimizations and empirical choices layered on
that core. Few of them change what the model fundamentally is.

## Mixture of Experts makes models sparse

A Mixture-of-Experts (MoE) block replaces the single feed-forward layer with
many expert feed-forward layers and a router that sends each token to a few of
them. Only the selected experts run, so the **active** parameter count per
token is a fraction of the **total** parameter count. DeepSeek V3 has 671B
total but 37B active parameters; Qwen3 235B-A22B has 22B active.

This makes model-size comparisons tricky. Total parameters drive memory
footprint and knowledge capacity, while active parameters drive per-token
compute and latency. A "235B" MoE model and a 235B dense model are not the same
kind of thing.

Many MoE designs add a **shared expert**: one feed-forward layer that is always
active for every token. It learns the common patterns, which frees the routed
experts to specialize instead of each re-learning the same basics. Usage is
not settled. DeepSeek V3, GLM-4.5, and Qwen3-Next keep a shared expert, while
Qwen3 235B-A22B, gpt-oss, and MiniMax-M2 drop it. Designs also differ on
many small experts (DeepSeek, Qwen3) versus a few large ones (gpt-oss: 32
experts, 4 active).

## Attention variants are KV-cache optimizations

**The KV cache.** During autoregressive generation, every new token attends to
all previous tokens. Caching each layer's key and value tensors avoids
recomputing them for the whole prefix at every step. This greatly speeds up
inference at the cost of memory that grows with context length, layers, and
attention heads. Within a single model call the cache is per sequence. Serving
stacks can additionally reuse cached prefixes across requests that share them;
this is what provider [prompt caching](/ai-engineering/models/providers/claude.md) and vLLM prefix
caching do.

Because KV-cache memory is often the binding constraint, most attention
variants are ways to shrink it:

- **Multi-Head Attention (MHA)** — every query head has its own key and value
  head. This is the baseline, still used by OLMo 2.
- **Grouped-Query Attention (GQA)** — several query heads share one key/value
  head, so fewer K/V tensors are cached. Used by Llama 4, Gemma 3, Qwen3, and
  gpt-oss.
- **Multi-Head Latent Attention (MLA)** — keys and values are compressed into a
  lower-dimensional latent before caching and projected back when used. It
  trades extra compute for a much smaller cache. Used by DeepSeek V3 and
  Kimi K2. DeepSeek's ablations report it modeling slightly better than MHA,
  whereas GQA is roughly on par.

These savings compound with the rest of the architecture: fewer layers, fewer
KV heads, a smaller head dimension, and local attention windows all multiply
into the cache size.

### Serving view: grouped-query and multi-query attention

Multiple query heads share fewer key/value heads, reducing KV state and decode bandwidth through a model architecture choice.

#### Mechanism

Ordinary multi-head attention gives each query head a corresponding key/value head. **Multi-query attention (MQA)** shares one KV head across all query heads. **Grouped-query attention (GQA)** uses an intermediate number: each group of query heads shares a KV head.

Fewer KV heads mean less state to store per token and fewer KV bytes to read during decode.[^gqa]

#### Why the distinction matters

The [KV cache](/ai-engineering/compute/serving/prefill-decode-and-kv-cache.md#kv-cache) memory estimate must use the number of KV heads. For the same layer count, head dimension and precision, eight KV heads require one quarter of the KV payload of 32 KV heads.

This is an architecture/checkpoint property, not a lossless runtime switch. The GQA paper describes uptraining existing multi-head checkpoints and studies the speed/quality compromise. A server cannot safely reinterpret an arbitrary checkpoint as MQA just by changing a flag.[^gqa]

#### Trade-offs

Sharing KV heads reduces representational freedom; quality depends on how the model was trained or adapted. Fewer KV heads can also constrain straightforward head-based tensor sharding, making [context parallelism](/ai-engineering/compute/serving/parallelism.md#context-parallelism) relevant when serving very long contexts across many devices.[^vllm-cp]

## Sliding-window attention is an optimization, not a new category

Sliding-window (local) attention lets each token attend only to a fixed window
of recent tokens. This bounds per-layer KV-cache size and compute, so in
principle the context length is unbounded. On its own, though, the model
cannot directly see anything outside the window. It works well only when
interleaved with regular global-attention layers that preserve long-range
access. Gemma 3 uses five local layers (1,024-token window) per global layer,
and gpt-oss alternates local and global layers. With global layers still
present, sliding windows are a memory and compute optimization rather than a
categorically different architecture.

Linear and hybrid attention (Gated DeltaNet in Qwen3-Next and Kimi Linear,
Lightning Attention in MiniMax-M1) follow the same pattern: cheaper attention
in most layers, full attention in some. MiniMax-M2 reverted to full attention,
with its authors noting that linear attention is tricky in production.

## Empirical tweaks that sometimes help

Many choices are heuristics. Each helped in some ablation and did not clearly
transfer elsewhere, so families diverge:

- **Normalization type and placement.** Pre-Norm (RMSNorm before attention and
  feed-forward) is standard. OLMo 2 moved to a Post-Norm variant for training
  stability, Gemma 3 uses both, and QK-Norm (normalizing queries and keys
  before RoPE) appears in OLMo 2, Gemma 3, and gpt-oss.
- **Width vs. depth.** For a similar budget, gpt-oss-20b is wider (2,880-dim
  embeddings, 24 blocks) while Qwen3 30B-A3B is deeper (2,048-dim, 48 blocks).
  A Gemma 2 ablation slightly favored wider.
- **Positional encoding.** RoPE is the default, with variants such as partial
  RoPE (MiniMax-M2) and YaRN for context extension. Some layers drop positional
  embeddings entirely (NoPE in every fourth SmolLM3 layer), relying on the
  causal mask for order. The length-generalization benefit is unproven at
  scale.
- **Optimizer.** Kimi K2 trained with Muon instead of AdamW at a scale where
  this had not been done before.
- **Multi-token prediction.** Training the model to predict several future
  tokens (DeepSeek V3, GLM-4.5, Qwen3-Next) improves training signal and
  enables speculative decoding.
- **Kernels.** FlashAttention changes how attention is computed (IO-aware,
  fused, tiled), not what is computed. It is an implementation optimization
  orthogonal to the architectural variants above.

## Multimodal architectures

Both main approaches start from a pretrained modality encoder, typically a
Vision Transformer such as CLIP for images. They differ in *where* the
non-text signal is fused into the language model.

**Unified embedding-decoder (Method A).** Image patches are encoded and then
projected by a small adapter into the same embedding space as text tokens. The
resulting embeddings are concatenated with the text tokens and fed to an
otherwise unmodified decoder. This is architecturally simpler and reuses
mature decoder-only tooling. The cost is that the decoder must learn to
interpret the new modality itself, and image tokens consume its context window.
Examples include Pixtral 12B, Molmo, MM1.5, and Emu3.

**Cross-modality attention (Method B).** Text flows through the decoder as
usual, and cross-attention layers inside the transformer blocks attend to the
encoder's outputs. Some of the cross-modal complexity moves out of the decoder
and into the encoder and the cross-attention layers, which are trained
separately. The context window is not filled with image tokens, and if the LLM
weights stay frozen its text-only performance is preserved. Examples include
Llama 3.2 Vision, NVLM-X, and Aria.

Hybrids exist as well, such as NVLM-H, which mixes both.

## Why it matters for AI engineering

- Compare models on **active parameters, KV-cache footprint, and context
  strategy**, not only on headline parameter count. These determine serving
  cost, latency, and how far long-context claims can be trusted.
- Long-context quality depends on how much **global attention** remains;
  sliding-window and linear-attention layers make long contexts cheaper, not
  automatically better.
- Benchmarks and [leaderboards](/ai-engineering/models/leaderboards.md) measure
  outcomes. Architecture explains cost and failure modes, but no single tweak
  reliably predicts quality.

[^gqa]: Joshua Ainslie et al., [GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints](https://arxiv.org/abs/2305.13245).
[^vllm-cp]: vLLM, [Context Parallel Deployment](https://docs.vllm.ai/en/latest/serving/context_parallel_deployment/).

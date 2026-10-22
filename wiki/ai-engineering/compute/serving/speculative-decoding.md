---
type: Concept
title: "Speculative Decoding"
aliases:
- "Speculative Sampling"
- "Assisted Decoding"
description: "A cheap proposer drafts multiple tokens and a target model verifies them together to reduce serial target-model passes."
tags:
- ai-engineering
- compute
- inference
- serving
parent: /ai-engineering/compute/serving.md
related:
- /ai-engineering/compute/serving/prefill-decode.md
- /ai-engineering/compute/serving/serving-metrics.md
- /ai-engineering/compute/serving/continuous-batching.md
sources:
- id: speculative-decoding
  resource: https://arxiv.org/abs/2211.17192
  title: "Fast Inference from Transformers via Speculative Decoding"
  author: "Yaniv Leviathan, Matan Kalman and Yossi Matias"
generated:
  by: codex/gpt-6
  at: '2026-10-22T13:46:52+04:00'
---

## Mechanism

A cheaper draft model proposes several tokens. The target model evaluates those candidate positions together, accepts a valid prefix, and corrects the first rejected position. Successful rounds commit multiple tokens per target-model pass, reducing the serial dependency cost of ordinary decode.

The original speculative-sampling algorithm includes acceptance and correction rules that preserve the target distribution. Merely checking whether a draft “looks good” does not provide that guarantee.[^speculative-decoding]

## When it helps

The proposal must be cheap, agreement must be high, and verification must cost less than generating the accepted tokens through separate target passes. This often suits decode workloads with spare parallel compute.

Draft inference, verification and rejected work add overhead. Poor agreement or a target already operating at high utilization can erase the benefit. The right speculation length depends on the proposer, target and workload.

## How to evaluate

Measure accepted tokens per verification round, end-to-end latency and total device cost. Compare with ordinary decoding at the same load and quality settings. “Lossless” means preserving the target sampling distribution under the algorithm's assumptions, not producing the same random sample or guaranteeing bitwise-identical execution.[^speculative-decoding]

[^speculative-decoding]: Yaniv Leviathan, Matan Kalman and Yossi Matias, [Fast Inference from Transformers via Speculative Decoding](https://arxiv.org/abs/2211.17192).

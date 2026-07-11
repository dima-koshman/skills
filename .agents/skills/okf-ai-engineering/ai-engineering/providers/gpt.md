---
type: Product
title: GPT
description: OpenAI GPT API token pricing and prompt caching — the 272K long-context cliff, cache-write fees, and keep-alive economics.
resource: https://developers.openai.com/api/docs/pricing
---

Token pricing and prompt-caching behavior for OpenAI's GPT API — short- and
long-context rates, the 272K-token pricing cliff, and cache-write economics. Read
it alongside the [Claude](/providers/claude.md) and [Gemini](/providers/gemini.md)
pricing notes for a cross-provider comparison. Caching is the concrete cost lever
behind [context engineering](/context/context-engineering.md);
[provider-side tools](/harness/provider-tools.md) are billed on top of these token
rates; and an [LLM gateway](/enterprise/llm-gateway.md) is where per-provider
costs get compared, routed, and capped.

*Verified against OpenAI documentation on 2026-07-11. Prices below are for GPT-5.6 Sol, Standard processing.*

# Token pricing

## Short context: up to 272,000 input tokens

| Token type | Price / 1M tokens |
|---|---:|
| Ordinary uncached input | $5.00 |
| Cached input read | $0.50 |
| Cache write | $6.25 |
| Output, including reasoning tokens | $30.00 |

A token belongs to only one input category: ordinary input, cache read, or cache write. Cache-write tokens are **not** charged both $5 and $6.25.

The advertised `$5/M input` is the ordinary uncached rate. With automatic caching enabled, an eligible cold prefix **may be written to cache** and those written tokens cost `$6.25/M`. Therefore, a one-off cacheable request can cost more than the headline input rate, but not every input token or request automatically costs $6.25.

Approximate billing:

```text
ordinary_input × $5/M
+ cached_input × $0.50/M
+ cache_write_tokens × $6.25/M
+ output_tokens × $30/M
```

Inspect `cached_tokens` and `cache_write_tokens` in API usage data rather than assuming which rate applied.

## Long-context pricing

A request with **more than 272,000 input tokens** uses long-context prices for the **entire request**, not only the excess:

| Token type | Long-context price / 1M |
|---|---:|
| Ordinary input | $10.00 |
| Cached input | $1.00 |
| Cache write | $12.50 |
| Output | $45.00 |

This creates a real pricing cliff at 272,001 input tokens — a threshold [Claude's 1M-context models do not have](/providers/claude.md), and one that [Gemini](/providers/gemini.md) sets at a different point (200K).

The threshold is based on the request's **input tokens**. Output generated during that request does not retroactively trigger long-context pricing. However, if that output is included as conversation history in the next request, it becomes input and can push the next request over 272K.

# How prompt caching works

- Automatic caching still exists. GPT-5.6 defaults to one **implicit** cache breakpoint.
- Explicit breakpoints can mark stable reusable prefixes.
- Setting cache mode to `explicit` disables the implicit breakpoint; only provided breakpoints are considered.
- Use a stable `prompt_cache_key` for requests sharing the same long prefix to improve matching.
- Cached prefixes remain eligible for reuse for **at least 30 minutes** and may remain longer.
- Cache reads still count toward token-per-minute limits.
- Cache writes cost 1.25× ordinary input on GPT-5.6-family models; older model families do not have this separate write fee.

# Keep-alive requests

Sending a tiny request that reuses a large cached prefix can theoretically be cheaper than allowing the prefix to expire and paying for another cache write:

- Read/write price ratio: `$0.50 / $6.25 = 1/12.5`
- For a 100K-token prefix: cache read ≈ `$0.05`; cache write ≈ `$0.625`

But OpenAI guarantees only a **minimum 30-minute eligibility period**. Its documentation does not clearly promise that every cache hit resets the guaranteed lifetime. Treat keep-alive as an experiment, not a contractual optimization:

1. Use it only when another real request is likely.
2. Verify each ping has `cached_tokens > 0` and `cache_write_tokens = 0`.
3. Stop after a bounded idle period.
4. Account for rate-limit consumption and small output costs.
5. Prefer prewarming before a predictable workload over indefinite pings.

# Practical recommendations

- Put stable system instructions, tools, files, or code before dynamic content.
- Use explicit breakpoints for large prefixes with predictable reuse.
- Log ordinary, cached, and cache-write tokens separately.
- Compact or summarize conversations before approaching 272K input tokens.
- Optimize for **cost per successful task**, not only listed price per token.

# Citations

- Pricing: <https://developers.openai.com/api/docs/pricing>
- GPT-5.6 Sol model page: <https://developers.openai.com/api/docs/models/gpt-5.6-sol>
- Prompt caching guide: <https://developers.openai.com/api/docs/guides/prompt-caching>

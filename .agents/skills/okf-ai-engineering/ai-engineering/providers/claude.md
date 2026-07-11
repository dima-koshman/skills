---
type: Product
title: Claude
description: Anthropic Claude API token pricing and prompt-caching mechanics — cache multipliers, TTLs, and cost-optimization guidance.
resource: https://docs.anthropic.com/en/docs/about-claude/pricing
---

Token pricing and prompt-caching behavior for Anthropic's Claude API — the
per-model rates, cache multipliers, and TTL rules that drive cost. Read it
alongside the [OpenAI](/providers/gpt.md) and [Gemini](/providers/gemini.md)
pricing notes for a cross-provider comparison. Caching is the concrete cost lever
behind [context engineering](/context/context-engineering.md);
[provider-side tools](/harness/provider-tools.md) are billed on top of these token
rates; and an [LLM gateway](/enterprise/llm-gateway.md) is where per-provider
costs get compared, routed, and capped.

*Verified against Anthropic documentation on 2026-07-11. Prices are per 1 million tokens.*

# Representative pricing

| Model | Base input | 5-minute cache write | 1-hour cache write | Cache hit/refresh | Output |
|---|---:|---:|---:|---:|---:|
| Claude Fable 5 | $10.00 | $12.50 | $20.00 | $1.00 | $50.00 |
| Claude Opus 4.8 | $5.00 | $6.25 | $10.00 | $0.50 | $25.00 |

Cache multipliers are:

- 5-minute write: **1.25×** base input
- 1-hour write: **2×** base input
- Cache hit/refresh: **0.1×** base input

A token is charged as ordinary input, cache creation, or cache read — not all three.

# How caching works

- Prompt caching must be enabled with `cache_control`; it is not globally automatic for every request.
- Top-level automatic caching lets Anthropic choose cache boundaries.
- Explicit `cache_control` markers let you define reusable prefixes.
- The default TTL is 5 minutes.
- A successful hit refreshes the 5-minute TTL without another cache-write charge.
- A 1-hour TTL is available at the higher write rate.
- Cache matching is prefix-based, so stable system prompts, tools, documents, and conversation history should come before changing content.
- Usage reports separate ordinary input, cache creation, and cache reads.

With a 5-minute cache, one later hit is already cheaper than sending the same prefix uncached twice. A 1-hour write generally needs at least two later hits to beat repeated uncached input.

# Context and long-context pricing

Current Claude models with a 1M-token context window use the same listed per-token rates throughout that window. Anthropic does not apply a [GPT-style](/providers/gpt.md) pricing cliff at a lower threshold for those models.

Input, generated output, and thinking tokens share the context window. Generated output does not retroactively change the current request's input price, but it becomes input if preserved in a later turn. Cached tokens still occupy context.

# Other modifiers

- US-only inference on supported newer models adds **1.1×**.
- Batch API processing gives a **50% input/output discount**.
- For most Claude models, cache-read tokens do not count toward input-token-per-minute limits; cache creation and uncached input do.

# Practical recommendations

- Use a 5-minute cache for interactive sessions.
- Use a 1-hour cache only when reuse over that period is likely.
- Keep stable content first and dynamic content last.
- Inspect `cache_creation_input_tokens` and `cache_read_input_tokens`.
- Bound any keep-alive loop; Claude's refresh-on-hit behavior makes it predictable, but unnecessary pings still cost money.

# Citations

- Pricing: <https://docs.anthropic.com/en/docs/about-claude/pricing>
- Prompt caching: <https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching>
- Context windows: <https://docs.anthropic.com/en/docs/build-with-claude/context-windows>
- Rate limits: <https://docs.anthropic.com/en/api/rate-limits>

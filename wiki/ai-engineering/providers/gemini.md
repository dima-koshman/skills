---
type: Model Provider
title: Gemini
description: Google Gemini API token pricing plus implicit and explicit context caching, with break-even
  guidance.
resource: https://ai.google.dev/gemini-api/docs/pricing
tags:
- ai-engineering
- providers
parent: /ai-engineering/providers.md
related:
- /ai-engineering/providers/claude.md
- /ai-engineering/providers/gpt.md
- /ai-engineering/context/context-engineering.md
- /ai-engineering/harness/provider-tools.md
- /ai-engineering/enterprise/llm-gateway.md
pricing_unit: USD per 1 million tokens
sources:
- id: ref-1
  resource: https://ai.google.dev/gemini-api/docs/pricing
  title: ai.google.dev
- id: ref-2
  resource: https://ai.google.dev/gemini-api/docs/caching
  title: ai.google.dev
- id: ref-3
  resource: https://ai.google.dev/gemini-api/docs/interactions
  title: ai.google.dev
- id: ref-4
  resource: https://ai.google.dev/gemini-api/docs/tokens
  title: ai.google.dev
generated:
  by: codex/gpt-6
  at: '2026-10-15T15:23:06+04:00'
---

Reference: <https://ai.google.dev/gemini-api/docs/pricing>

Token pricing and context-caching behavior for Google's Gemini API — per-model
rates, the 200K prompt-size tier, and the difference between implicit and explicit
caching. Read it alongside the [Claude](/ai-engineering/providers/claude.md) and
[OpenAI](/ai-engineering/providers/gpt.md) pricing notes for a cross-provider comparison. Caching
is the concrete cost lever behind
[context engineering](/ai-engineering/context/context-engineering.md);
[provider-side tools](/ai-engineering/harness/provider-tools.md) are billed on top of these token
rates; and an [LLM gateway](/ai-engineering/enterprise/llm-gateway.md) is where per-provider
costs get compared, routed, and capped.

*Verified against Google documentation on 2026-07-11. Prices are per 1 million tokens unless noted.*

## Representative pricing

### Gemini 3.5 Flash — Standard

| Token type | Price |
|---|---:|
| Input | $1.50 |
| Cached input | $0.15 |
| Output, including thinking | $9.00 |
| Cache storage | $1.00 per 1M tokens per hour |

Batch pricing is $0.75 input and $4.50 output; cached input is $0.075.

### Gemini 3.1 Pro Preview — Standard

| Prompt size | Input | Cached input | Output, including thinking |
|---|---:|---:|---:|
| Up to 200K tokens | $2.00 | $0.20 | $12.00 |
| Over 200K tokens | $4.00 | $0.40 | $18.00 |

Cache storage is $4.50 per 1M tokens per hour.

Google lists separate request-wide rates for prompts up to and over 200K tokens; it does not describe the higher tier as marginal pricing applied only to excess tokens. Budget conservatively as a full-request tier — the same cliff shape [OpenAI has at 272K](/ai-engineering/providers/gpt.md), just at a lower threshold, and one [Claude's 1M-context models avoid](/ai-engineering/providers/claude.md).

## Implicit caching

For Gemini 2.5 and newer models, implicit caching is enabled by default when eligible:

- No cache object or explicit breakpoint is required.
- A hit is opportunistic, not guaranteed.
- Minimum eligible prompt size is currently 4,096 tokens for Gemini 3.5 Flash and Gemini 3.1 Pro Preview, and 2,048 for Gemini 2.5 Flash/Pro.
- The Interactions API currently supports implicit caching only.

Place stable, repeated material at the beginning of the prompt to improve hit probability.

## Explicit caching

The `generateContent` API also supports explicit cache objects:

- You create and reference a named cache.
- Default TTL is 1 hour.
- TTL can be chosen and updated.
- Billing includes discounted cached-token reads plus token-hours of storage.
- There is no [Claude](/ai-engineering/providers/claude.md)/[OpenAI](/ai-engineering/providers/gpt.md)-style cache-write multiplier in the published pricing table; storage duration is the main extra cost.

Explicit caching is preferable when reuse is predictable and you need guaranteed cache identity. Implicit caching is simpler but offers no guaranteed savings.

## Context and billing

The long-context pricing tier is determined by prompt/input size. Output and thinking generated during the request do not retroactively change that tier. If retained in a later conversation turn, they become input and may push that later request over 200K.

Use `countTokens` before expensive requests and inspect cached-token fields in `usageMetadata`.

## Practical recommendations

- Use implicit caching for repeated interactive prompts with stable prefixes.
- Use explicit caches for large documents reused enough to justify storage.
- Calculate break-even from cached-read savings versus token-hours of storage.
- Compact conversations before approaching a model's pricing threshold.
- Remember that thinking tokens are billed at the output rate.

## Resources

- Pricing: <https://ai.google.dev/gemini-api/docs/pricing>
- Context caching: <https://ai.google.dev/gemini-api/docs/caching>
- Interactions API caching: <https://ai.google.dev/gemini-api/docs/interactions>
- Token counting: <https://ai.google.dev/gemini-api/docs/tokens>

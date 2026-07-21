---
name: ranking-llms-by-benchmark
description: Use when asked which model is best/strongest/fastest/cheapest, the current best model per provider, what to use for coding/reasoning, or to compare or pick between specific models — anything where the answer depends on rankings that change as new models ship.
---

# Ranking LLMs by Benchmark

## Overview

Model rankings change constantly — new models ship weekly and leaderboards reshuffle. Your training data is stale by the time anyone asks. **Never answer "which model is best" from memory; always fetch current data first.**

Core principle: a model-ranking answer is only as good as the date of the data behind it. Cite the source and the date.

## When to Use

Use when the question is about *which* model, not *how to use* one:

- "What's the best model right now / for coding / for reasoning?"
- "Current best model from OpenAI / Anthropic / Google?"
- "Is X better than Y?" / "Should I use X or Y for Z?"
- "What's the fastest / cheapest frontier model?"
- Any recommendation where a newer model could have changed the answer.

Do NOT use for: how to call a model, pricing math you already have, or provider-specific API mechanics (use the `claude-api` skill for Anthropic specifics).

## The One Rule

```
DO NOT answer from training data. Fetch live, then answer.
```

If you catch yourself typing a model name and a verdict without having fetched anything this turn — stop. That confident memory is exactly the stale-data failure. (It happens: a prior session asserted "the codex model is better at coding" with no source; the live benchmarks said the opposite.)

## Workflow

1. **Fetch current rankings.** WebSearch + WebFetch the authoritative sources below. Pull the *current* top models and their scores.
2. **Cross-check ≥2 sources.** Leaderboards disagree and can lag. One source is a data point, not a conclusion.
3. **Answer overall + coding** (the requested scope):
   - Lead with the **current frontier model per provider** (OpenAI / Anthropic / Google, plus any other relevant).
   - Add a **coding callout** — the strongest model(s) for coding/agentic-SWE, which is often *not* the same as the general frontier.
4. **Always state the date and cite sources** as markdown links. A ranking with no date is unusable.
5. **Flag freshness gaps** — if a model launched in the last few days, leaderboards may not cover it yet; say so rather than omit it.

## Authoritative Sources

**Public leaderboards** (vendor-neutral, continuously updated — lead with these):

- **LMArena** (`lmarena.ai`) — crowd-sourced Elo, overall + category leaderboards (coding, math, vision, etc.).
- **Artificial Analysis** (`artificialanalysis.ai`) — composite Intelligence Index plus speed (tokens/s) and price-per-token. Best single view of quality-vs-cost-vs-speed.
- **Aider leaderboard** (`aider.chat/docs/leaderboards/`) — practical code-editing benchmark.
- **SWE-bench** (`swebench.com`) — agentic software-engineering; look for Verified / Pro splits.

**Independent eval writeups** (aggregate/compare; use for context, recency varies):

- Third-party benchmark blogs that compare models head-to-head (e.g. Vellum, BenchLM, SmartScope). Treat as secondary — verify their numbers against a primary leaderboard before quoting.

Prefer primary leaderboards for the actual numbers; use writeups to interpret and to catch very recent releases.

## Caveats to Carry Into the Answer

- **"Best" is task-dependent.** The overall-frontier model and the best *coding* model are frequently different. Keep them separate.
- **Accuracy ≠ speed ≠ cost.** A model can win quality and lose on latency/price. Name the axis you're ranking on.
- **Benchmark splits matter.** SWE-bench Verified vs Pro, with/without tools — quote which split.
- **Vendor self-reported numbers are not neutral.** If you cite a release post's claim, label it as the vendor's own.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Answering from training-data memory | Fetch live every time. The question implies "as of now." |
| Citing one leaderboard | Cross-check ≥2; they disagree and lag. |
| Conflating "best overall" with "best at coding" | Report both; they're usually different models. |
| Omitting the date | Always state the data date — a ranking without it is worthless. |
| Quoting a vendor's own benchmark as neutral truth | Label self-reported claims; prefer third-party leaderboards. |

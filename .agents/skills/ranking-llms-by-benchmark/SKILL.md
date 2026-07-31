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

## Ranking Models Inside a Subscription Pool

A different question from "which model is best": *given a fixed monthly allowance, which
models should fill which agent roles?* Raw benchmark rank is the wrong answer here —
capacity per unit of quality is what matters.

`scripts/rank_opencode_go.py` does this end-to-end for opencode Zen Go. It fetches the
model list, prices and usage multipliers from `opencode.ai/docs/go`, cross-checks prices
and release dates against `models.dev/api.json`, pulls Coding/Agentic/Intelligence indices
from the Artificial Analysis API, scrapes measured steps-per-task from the coding-agents
board, and prints a comparison table plus both Pareto frontiers.

```bash
AA_API_KEY=... python3 scripts/rank_opencode_go.py --json out.json
```

Adapt the same shape for any capped plan. The method:

1. **Find the real budget unit.** Not "requests" unless the provider actually meters
   requests. Zen Go meters **dollars of usage**: $12/5h, $30/week, $60/month.
2. **Establish whether the pool is shared or per-model.** This changes everything —
   see the caveat below.
3. **Convert price-per-token into cost-per-task.** The bridge is *steps per task* (median
   ≈84 API calls for agentic coding, but ranging 61-174 by model). Get it from the AA
   coding-agents `mean.steps` field; there is no other public source.
4. **Weight by any multiplier**, then rank on quality-vs-capacity, not quality alone.
5. **Check the shortest window, not just the monthly one.** A burst limit can make a
   model unusable even when the monthly budget looks fine.

## Authoritative Sources

**Public leaderboards** (vendor-neutral, continuously updated — lead with these):

- **LMArena** (`lmarena.ai`) — crowd-sourced Elo, overall + category leaderboards (coding, math, vision, etc.).
- **Artificial Analysis** (`artificialanalysis.ai`) — **the best single view of quality-vs-cost-vs-speed**, and the only one with a machine-readable API. Composite Intelligence / Coding / Agentic indices, price-per-token, tokens/s. Its `/agents/coding-agents` board additionally measures whole *harness + model* combinations — Coding Agent Index, Cost per Task, Time per Task, and steps per task. See `references/artificial-analysis-api.md` for the API, the free-tier limits, and how to extract the agent leaderboard (which has no API).
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
- **Reasoning effort is part of the model's identity.** AA scores `gpt-5-6-luna` (max) at CI 71.4 and `gpt-5-6-luna-low` at 44.2 — same model, 27 points apart. Quote the effort level you actually configure, and pull cost/steps from that same variant.
- **Match builds on release date, not name.** Providers serve older builds under unversioned ids. opencode's `deepseek-v4-flash` (2026-04-24) is AA's `deepseek-v4-flash-0420` at CI 56.2, not AA's unsuffixed 0731 build at CI 69.1.
- **A derived table is not a quota.** Zen Go's "requests per month" column looks like a second ceiling but is arithmetic: `usage_allowance ÷ cost_per_request`, using per-model token profiles the docs list right underneath. It reproduces to the request. Read the prose before treating any table as an enforced limit.
- **Shared pools do not compose.** If one pool covers every model, you cannot plan "model A, then fall back to model B" — exhausting the pool on A blocks B too. Budget roles as *fractions of one pool* and check the burst window: a single full-size Kimi K3 task costs $15.26 of pool, more than the entire $12 five-hour allowance.
- **Cost per task is a band, not a number.** Cache-hit rate dominates it and is a property of the harness, not the price sheet. AA measured GLM-5.2 at a 34% hit rate versus a 93% median, making it 2.3x more expensive than its price sheet implies.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Answering from training-data memory | Fetch live every time. The question implies "as of now." |
| Citing one leaderboard | Cross-check ≥2; they disagree and lag. |
| Conflating "best overall" with "best at coding" | Report both; they're usually different models. |
| Omitting the date | Always state the data date — a ranking without it is worthless. |
| Quoting a vendor's own benchmark as neutral truth | Label self-reported claims; prefer third-party leaderboards. |
| Reading a derived estimate as an enforced quota | Read the surrounding prose. If the numbers reproduce from price × allowance, it's arithmetic, not a limit. |
| Assuming per-model budgets on a shared pool | Confirm the metering model first; it decides whether fallback chains are even possible. |
| Matching models by name across sources | Match on release date. Same name ≠ same build. |
| Quoting cost per task as a point estimate | Give a band, and say where measured data lands in it. |

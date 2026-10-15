---
type: Reference
title: LLM Leaderboards
description: A curated bookmark set and benchmark map for choosing reliable, independent LLM evaluation
  sources across capabilities.
tags:
- ai-engineering
- providers
parent: /ai-engineering/providers.md
related:
- /ai-engineering/observability/langsmith-evals.md
- /ai-engineering/providers/claude.md
- /ai-engineering/providers/gpt.md
- /ai-engineering/providers/gemini.md
note_date: '2026-07-13'
sources:
- id: ref-1
  resource: https://artificialanalysis.ai/
  title: Artificial Analysis
- id: ref-2
  resource: https://benchlm.ai/
  title: BenchLM
- id: ref-3
  resource: https://labs.scale.com/leaderboard/swe_bench_pro_public
  title: Scale Labs SWE-Bench Pro
- id: ref-4
  resource: https://gorilla.cs.berkeley.edu/leaderboard.html
  title: Berkeley Function Calling Leaderboard
- id: ref-5
  resource: https://livebench.ai/
  title: LiveBench
- id: ref-6
  resource: https://arena.ai/leaderboard/text
  title: Arena
generated:
  by: codex/gpt-6
  at: '2026-10-15T15:23:06+04:00'
---

Note dated: 2026-07-13.

Topics: leaderboards, evaluation, benchmarks, model-selection.

A curated set of external LLM leaderboards and benchmarks for picking models, and
a capability-to-benchmark map for verifying results. These are the *public,
cross-model* evaluation sources — complementary to the *internal, task-specific*
evaluation covered by [LangSmith Evals](/ai-engineering/observability/langsmith-evals.md). Pair
model-quality signals here with the per-provider cost signals in the
[Claude](/ai-engineering/providers/claude.md), [GPT](/ai-engineering/providers/gpt.md), and
[Gemini](/ai-engineering/providers/gemini.md) pricing notes when selecting a model.

There is currently no single LLM leaderboard that is simultaneously:

- comprehensive across capabilities;
- current across the newest models;
- independently evaluated;
- methodologically consistent;
- broad enough to cover coding agents, tool use, reasoning, knowledge, long context, and real workflows.

The best approach is to use one broad dashboard for discovery, then verify important results against the benchmark owner's own leaderboard.

## Recommended bookmark set

A compact set that covers most practical needs:

1. [Artificial Analysis](https://artificialanalysis.ai/)
   Best daily dashboard for quality, price, speed, and independently run evaluations.

2. [BenchLM](https://benchlm.ai/)
   Best benchmark and model discovery index.

3. [Scale Labs SWE-Bench Pro](https://labs.scale.com/leaderboard/swe_bench_pro_public)
   Best source for serious repository-level software-engineering evaluation.

4. [Berkeley Function Calling Leaderboard](https://gorilla.cs.berkeley.edu/leaderboard.html)
   Best source for structured function and tool calling.

5. [LiveBench](https://livebench.ai/)
   Useful broad and relatively fresh objective evaluation.

6. [Arena](https://arena.ai/leaderboard/text)
   Useful for human preference and conversational quality.

## Practical benchmark map

| Capability | Primary benchmark or source | Secondary check |
|---|---|---|
| Repository software engineering | SWE-Bench Pro | Terminal-Bench |
| Algorithmic coding | LiveCodeBench | SciCode |
| Basic function calling | BFCL | Tests against your own API schemas |
| Multi-step tool workflows | τ²-bench | EnterpriseOps-Gym / AutomationBench |
| General knowledge | AA-Omniscience | MMLU-Pro |
| Difficult reasoning | Humanity's Last Exam | GPQA Diamond |
| Long-context work | AA Long Context Reasoning | Application-specific retrieval tests |
| Conversational quality | Arena category scores | Blind manual review |
| Enterprise task completion | GDPval-AA / AA-Briefcase | Internal workflow evaluation |
| Cost efficiency | Cost per successful task | Price per token |

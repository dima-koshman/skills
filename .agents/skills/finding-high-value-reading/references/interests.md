# Reader profile

What Dima is focused on and how deep he wants to go. Update this file when he states
a new interest or a depth preference, and give the change a date. The wiki
(`~/Projects/dima/wiki`) records what he has learned; this file records what he is
looking for now.

## Current focus (as of 2026-10-22)

- **Mojo, the MAX framework, and GPU programming / AI compute.** He is learning these
  now. Hardware-aware material, kernels explained conceptually, and Modular's own
  news and design rationale are all in scope.
  - 2026-10-22: Building a conceptual map of LLM inference and serving techniques:
    KV memory, scheduling, attention kernels, quantization, disaggregation and
    parallelism; wants separate notes with mechanisms and trade-offs.
  - 2026-10-22: Comparing interactive cloud GPU development environments for
    PyTorch, vLLM and Mojo, especially local VS Code over SSH, browser IDEs,
    Runpod, Modal and access to GPU clusters.
- **AI engineering:** agents, harnesses, context engineering, evals, LLM gateways and
  observability (see `ai-engineering/` in the wiki).
  - 2026-10-22: Interested in PTC adoption and whether improving models and harnesses
    complement orchestration techniques or make them less useful.
  - 2026-10-22: Main orchestration interest is dynamic subagents: generated code
    coordinating workers, rather than generic API-tool orchestration.
- **Software engineering decisions at scale:** why strong organizations choose what
  they choose (monorepos, SRE practice, distributed systems).
- **State of LLMs:** which models lead on quality, price and speed. For an actual
  model pick, use the `ranking-llms-by-benchmark` skill.

## Depth preference

- Prefer decision rationale, trade-offs, lessons learned, and conceptual
  explanations over implementation detail.
- Framework-internals blogs (e.g. the PyTorch blog's operator and compiler posts) are
  out of scope for now unless he asks to dig in. Mention one only when it changes
  how he would build something.
- Actionable posts (e.g. many LangChain posts on agent design and evals) rank high.

## Not interested

Add topics he dismisses so they are filtered next time, including trending-repo
categories.

- **Indexed code-search servers for agents** (e.g. xerj), dismissed 2026-10-16. The
  index has to be kept fresh and the server kept running. Gains over the grep and
  file reads agents already handle well are modest, and only on unfamiliar code.
  Mention one only if it is a big step beyond grep on large private codebases,
  backed by an independent benchmark.

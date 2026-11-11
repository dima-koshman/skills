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
  - 2026-11-05: Asking how GPUs are shared (MPS, MIG, Run:ai) and how the serving
    stack layers (Triton, vLLM); wants isolation guarantees and failure behavior,
    not just features.
- **AI engineering:** agents, harnesses, context engineering, evals, LLM gateways and
  observability (see `ai-engineering/` in the wiki).
  - 2026-10-22: Interested in PTC adoption and whether improving models and harnesses
    complement orchestration techniques or make them less useful.
  - 2026-10-22: Main orchestration interest is dynamic subagents: generated code
    coordinating workers, rather than generic API-tool orchestration.
- **Software engineering decisions at scale:** why strong organizations choose what
  they choose (monorepos, SRE practice, distributed systems).
- **Which skills hold value as AI improves (2026-11-04):** he wants to hand execution to
  AI and move up to directing it. Looking for general skills that gain value as models
  improve, plus evidence on supervision and skill loss.
- **State of LLMs:** which models lead on quality, price and speed. For an actual
  model pick, use the `ranking-llms-by-benchmark` skill.
  - 2026-11-11: Also wants to know how far to trust benchmarks. That means
    leaderboard method changes and benchmaxxing evidence, such as fresh or mutated
    tasks that show public scores falling apart. The wiki's LLM Leaderboards note
    has the current picture.

## Depth preference

- Prefer decision rationale, trade-offs, lessons learned, and conceptual
  explanations over implementation detail.
- Framework-internals blogs (e.g. the PyTorch blog's operator and compiler posts) are
  out of scope for now unless he asks to dig in. Mention one only when it changes
  how he would build something.
- Actionable posts (e.g. many LangChain posts on agent design and evals) rank high.
- **New only if it isn't replicable (2026-11-11).** He judges a post by whether its
  idea is new or already doable with what he has: skills, hooks, scheduled jobs,
  his wiki. Example: Anthropic's agent-memory "dreaming" post he saw as replicable
  with a memory skill plus hooks. Put a post forward for its new empirical results
  or a new mechanism, and say which in the "why" line.
- **Name the source's incentive (2026-11-11).** Vendor blogs are fine, but flag when
  a post is selling the vendor's product. LangChain posts often push LangSmith,
  LangSmith Engine and Managed Deep Agents. Pull out the general pattern and mention
  the pitch.
- **Weigh adoption cost (2026-11-11).** He accepts eval-driven development as a good
  pattern, but thinks it only pays for critical agentic use cases. Golden datasets
  need human upkeep, and LLM judges, periodic runs and human review all cost money.
  Prefer material that is honest about upkeep cost or shows cheap versions.

## "What's new" digests (2026-11-11)

His feedback on the first digest (2026-11-06 to 2026-11-11):

- **Two tiers.** Most news is "nice to know": he gets the idea from the title or a
  quick glance. Give those items a title plus one line, and keep the tier short. Save
  fuller summaries for the few items that hold reasoning, evidence or a mechanism.
- **Model launches:** cover frontier models and the models he can actually use.
  Mention other launches in one line or drop them. Inkling 2 Small, a Tinker-only
  open model from Thinking Machines, wasn't relevant.
- **Low-signal formats:** Latent Space's event write-ups, such as the Nov 11 piece
  on working with Codex, were unfocused. Latent Space's AI News headlines are still
  fine as titles.

## Not interested

Add topics he dismisses so they are filtered next time, including trending-repo
categories.

- **Indexed code-search servers for agents** (e.g. xerj), dismissed 2026-10-16. The
  index has to be kept fresh and the server kept running. Gains over the grep and
  file reads agents already handle well are modest, and only on unfamiliar code.
  Mention one only if it is a big step beyond grep on large private codebases,
  backed by an independent benchmark.
- **Trending GitHub agent tools** (worktree managers, computer-use and browser CLIs,
  skill packs, memory plugins), dismissed 2026-11-11. They look interesting at first,
  but they're too specific and are usually superseded within months. Report a
  trending repo only if it marks a durable shift, such as a new capability or a
  major org's foundational project. Otherwise skip trending unless he asks for it.
- **Async-agent and multi-session UX research** (async subagents, worktree tooling
  for parallel sessions), set aside 2026-11-11. He sees it as mostly a UX problem
  that harnesses will soon solve natively: reply fast in chat, run work in the
  background. One-line news is enough, with no deep reading. Exception: material on
  what native async won't fix, such as conflicting edits and the human review
  bottleneck.
- **Decision-model hype**, 2026-11-11. They are efficient for decisions, but the
  niche is narrower than the hype. He found no natural fit in his work or hobby
  projects. Mention one only with a concrete use case close to his work.

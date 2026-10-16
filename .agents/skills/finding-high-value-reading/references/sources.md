# High-signal sources

Starting points, grouped by what they are good for. Pick the groups that match the
topic. Never recommend a source from this list without fetching the specific post. The
list says where to look, not what is true. URLs checked 2026-10-16. Netflix, Uber and
ACM Queue block scripted fetches but are live.

## Decision rationale from the people who built it

Company engineering blogs are where a team explains *why*: a migration, a rewrite, a
technology choice, and what it cost.

| Source | Strong on |
| --- | --- |
| [Anthropic Engineering](https://www.anthropic.com/engineering) | Agent harnesses, evals, context engineering, internal infra at agent scale (e.g. the Scion monorepo post) |
| [Google Research blog](https://research.google/blog/) | Research behind Google systems and models |
| [Google SRE books](https://sre.google/books/) | Reliability practice. The original book, the Workbook and *Building Secure & Reliable Systems* are free online. The rewritten **2nd edition** (2026) is paid (O'Reilly, Google Books). The free [book update pages](https://sre.google/resources/book-update/) link later papers and talks per chapter. |
| [Software Engineering at Google](https://abseil.io/resources/swe-book) (free book) | Why Google does code review, testing, monorepo/One Version, deprecation the way it does |
| [AWS Builders' Library](https://aws.amazon.com/builders-library/) | How Amazon builds and operates services: timeouts, retries, load shedding, deployments |
| [All Things Distributed](https://www.allthingsdistributed.com/) (Werner Vogels), [Marc Brooker](https://brooker.co.za/blog/) | Distributed-systems reasoning from AWS leaders |
| [Meta Engineering](https://engineering.fb.com/) | Source control (Sapling), infra at extreme scale |
| [Netflix Tech Blog](https://netflixtechblog.com/), [Uber Engineering](https://www.uber.com/blog/engineering/) | Microservices, data platforms, migrations |
| [Stripe](https://stripe.com/blog/engineering), [Cloudflare](https://blog.cloudflare.com/), [Discord](https://discord.com/category/engineering), [Slack](https://slack.engineering/), [Dropbox](https://dropbox.tech/), [Figma](https://www.figma.com/blog/engineering/), [GitHub](https://github.blog/engineering/), [Shopify](https://shopify.engineering/) | Concrete "why we moved from X to Y" posts with numbers |

## AI engineering

| Source | Strong on |
| --- | --- |
| [Anthropic Engineering](https://www.anthropic.com/engineering), [Anthropic Research](https://www.anthropic.com/research) | Building agents, tool design, evals, interpretability |
| [OpenAI engineering](https://openai.com/news/engineering/), [Google DeepMind blog](https://deepmind.google/discover/blog/) | Frontier-lab practice and research |
| [LangChain blog](https://blog.langchain.com/) | Often directly actionable: agent architectures, context engineering, evals in practice |
| [Artificial Analysis](https://artificialanalysis.ai/) | Current state of LLMs: quality, price and speed leaderboards, coding-agent benchmarks. For a model pick, use the `ranking-llms-by-benchmark` skill. |
| [Hugging Face blog](https://huggingface.co/blog) | Open models, training and serving |
| [PyTorch blog](https://pytorch.org/blog/) | Active, but mostly framework internals (compiler, kernels, distributed training). Use only for deep dives; see the depth preference in `interests.md`. |
| [Simon Willison](https://simonwillison.net/) | Daily, skeptical, hands-on notes on LLM tools and security (prompt injection) |
| [Lilian Weng](https://lilianweng.github.io/) | Long, citation-dense surveys (agents, hallucination, RL) |
| [Chip Huyen](https://huyenchip.com/blog/), [Eugene Yan](https://eugeneyan.com/writing/), [Hamel Husain](https://hamel.dev/) | Production ML/LLM systems, evals, lessons from real deployments |
| [Latent Space](https://www.latent.space/), [Interconnects](https://www.interconnects.ai/) (Nathan Lambert), [Sebastian Raschka](https://magazine.sebastianraschka.com/) | Industry context, post-training, model architecture |

## GPU programming and AI compute

| Source | Strong on |
| --- | --- |
| [Modular blog](https://www.modular.com/blog) | Mojo and MAX releases and design rationale; the *Democratizing AI Compute* series by Chris Lattner on why the AI software stack looks the way it does. Recent: Qualcomm acquired Modular (July 2026), Mojo 1.0 (August 2026) and open-sourced. |
| [Mojo GPU Puzzles](https://puzzles.modular.com/), [Mojo GPU intro tutorial](https://docs.modular.com/mojo/manual/gpu/intro-tutorial) | Hands-on path from thread indexing to tensor cores in Mojo and MAX |
| [Making Deep Learning Go Brrrr](https://horace.io/brrr_intro.html) (Horace He) | Conceptual: compute-bound vs memory-bound vs overhead-bound. The mental model behind most GPU optimization. |
| [How to optimize a CUDA matmul](https://siboehm.com/articles/22/CUDA-MMM) (Simon Boehm) | One kernel taken step by step toward cuBLAS performance, explaining why each step helps |
| [GPU MODE resource stream](https://github.com/gpu-mode/resource-stream) | Community-curated GPU programming links, from the GPU MODE lecture series |
| [Hazy Research blog](https://hazyresearch.stanford.edu/blog) | Stanford's kernel and hardware-aware ML research (FlashAttention lineage, ThunderKittens) |
| [GPU-Puzzles](https://github.com/srush/GPU-Puzzles) (Sasha Rush) | The original puzzle set that Mojo GPU Puzzles adapts |
| [NVIDIA Technical Blog](https://developer.nvidia.com/blog/) | Vendor view of new hardware features. Primary for what the chip does, biased on comparisons. |

## What's new and trending

| Source | Use |
| --- | --- |
| [GitHub Trending](https://github.com/trending?since=daily) | Repos gaining stars today. Filter by language: [Python](https://github.com/trending/python?since=daily), [Mojo](https://github.com/trending/mojo?since=daily). Use `since=weekly` for a less noisy view. |
| [GitHub blog](https://github.blog/), [GitHub engineering](https://github.blog/engineering/) | GitHub product changes and how GitHub runs its own infrastructure |

## Curators: someone else already filtered

| Source | Strong on |
| --- | --- |
| [The Pragmatic Engineer](https://newsletter.pragmaticengineer.com/) (Gergely Orosz) | How big tech and scale-ups actually work, from interviews with insiders. The closest thing to a feed of unknown unknowns. |
| [ByteByteGo](https://blog.bytebytego.com/) | Visual system-design summaries of company architectures. Good for an entry point, but follow through to the primary post. |
| [InfoQ](https://www.infoq.com/) | QCon talks: practitioners presenting decisions and their consequences |
| [Martin Fowler](https://martinfowler.com/) | Architecture patterns and refactoring, carefully argued |
| [ACM Queue](https://queue.acm.org/), [USENIX conferences](https://www.usenix.org/conferences) (SREcon, OSDI, NSDI) | Practitioner papers and talks with real data |
| [Dan Luu](https://danluu.com/), [Julia Evans](https://jvns.ca/) | Evidence-heavy essays; clear explanations of systems internals |
| [The Morning Paper](https://blog.acolyer.org/) (archived), [Papers We Love](https://paperswelove.org/) | Paper summaries and discussion of classic CS papers |
| [Increment](https://increment.com/) (archived), [High Scalability](https://www.highscalability.com/) | Archives of themed engineering issues and architecture write-ups |

## Lessons from failure

| Source | Strong on |
| --- | --- |
| [danluu/post-mortems](https://github.com/danluu/post-mortems) | Curated public postmortems by category: config, hardware, time, database |
| [AWS post-event summaries](https://aws.amazon.com/premiumsupport/technology/pes/) | Detailed root-cause write-ups of major AWS outages |
| [Cloudflare blog](https://blog.cloudflare.com/) | Unusually candid incident write-ups |

## Community-vetted classics

Use these to find the posts practitioners kept rereading, which is often older material.

- [Hacker News search](https://hn.algolia.com/), sorted by popularity. The API gives
  points and dates, and a post resubmitted over many years is a classic:

  ```bash
  curl -s "https://hn.algolia.com/api/v1/search?query=<topic>&tags=story" \
    | python3 -c "import json,sys; [print(h['points'], h['created_at'][:10], h['title'], h.get('url')) for h in json.load(sys.stdin)['hits']]"
  ```

  It also confirms a post's real URL and date when the host blocks fetches (Medium does).
- [Hacker News](https://news.ycombinator.com/), [Lobsters](https://lobste.rs/). Comment
  threads often contain the strongest counter-argument.
- Curated lists: [engineering-blogs](https://github.com/kilimchoi/engineering-blogs)
  (an index of company blogs), [awesome-scalability](https://github.com/binhnguyennus/awesome-scalability)
  (articles grouped by scalability, availability and stability topics),
  [system-design-primer](https://github.com/donnemartin/system-design-primer).

---
type: Practice
title: Model Routing
description: Choosing a cheaper or stronger model per task belongs in the harness, which knows the task, and
  should happen once per thread, because switching models mid-conversation throws away the prompt cache.
tags:
- ai-engineering
- harness
- cost
parent: /ai-engineering/harness.md
related:
- /ai-engineering/enterprise/llm-gateway.md
- /ai-engineering/context/prompt-caching.md
- /ai-engineering/models/jev.md
sources:
- id: langchain-harness-router
  resource: https://www.langchain.com/blog/how-to-build-a-model-router-in-the-harness
  title: How to build a model router in the harness
  author: Sydney Runkle, Eugene Yurtsev (LangChain)
  last_modified: '2026-10-01T00:00:00Z'
- id: dima-teams-2026-09-02
  resource: Dima's reply in the AI Platform team channel, 2026-09-02
  title: Advice against LiteLLM's Auto Router in the gateway
  author: human:dmitry-koshman
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-10-16T16:00:00+04:00'
---

Model routing sends easy requests to a cheap model and hard ones to a strong model, to save money. The
question is where the decision is made.

## Why not in the gateway

Gateways such as LiteLLM offer automatic routing by request complexity. Dima advised his team against it
(2026-09-02), and the AI Platform does not make routing the gateway's job:[^dima-teams-2026-09-02]

- **Unpredictable classification.** Judging a request's complexity from the request alone is
  unreliable.
- **Lost caches.** Switching models discards the cached prompt prefix, so each switch pays full input
  price. See [prompt caching](/ai-engineering/context/prompt-caching.md).
- **The savings backfire.** Cache misses plus simple requests misrouted to heavy models can cost more than
  no routing.

The [LLM gateway](/ai-engineering/enterprise/llm-gateway.md) forwards the model the client named.

## When it works: in the harness, once per thread

LangChain's Open SWE router shows the version that pays off:[^langchain-harness-router]

- **In the harness**, because routing needs the task context the harness already assembles; the
  criteria are specific to Open SWE's tasks.
- **Once per thread.** One model is chosen at the start; mid-thread switching is avoided because it
  discards the prompt cache.
- **A fast classifier.** The first version used an LLM with structured output; moving to
  [Jev](/ai-engineering/models/jev.md) made classification about 50× faster.
- **Measured with a live A/B test** over 973 threads: median cost per thread fell 64% ($2.61 → $0.94)
  with no measurable quality change (merged PRs 29.2% vs 27.3%, p = 0.49). A fast-only control was stopped
  within a day because output quality was poor.

Limits: a thread whose difficulty changes midway stays on its first model, and the criteria have to be
rewritten for each agent.[^langchain-harness-router]

[^langchain-harness-router]: LangChain blog, 2026-10-01.
[^dima-teams-2026-09-02]: Dima, Teams, 2026-09-02; recorded as a decision in the AI Platform knowledge base.

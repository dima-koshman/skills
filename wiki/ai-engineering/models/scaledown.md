---
type: Decision Model
title: ScaleDown
description: Hosted constrained decoding models (CDMs) for summarizing, compressing, extracting and classifying
  agent context — small task-specific models that return only answers the task allows.
resource: https://docs.scaledown.ai
tags:
- ai-engineering
- models
- context-engineering
parent: /ai-engineering/models.md
related:
- /ai-engineering/models/jev.md
- /ai-engineering/models/clm.md
- /ai-engineering/agents/deep-agents.md
- /ai-engineering/context/context-engineering.md
- /ai-engineering/observability/langsmith.md
decision_interface:
- Summarize
- Compress
- Extract
- Classify
serving_model: hosted
sources:
- id: langchain-scaledown
  resource: https://www.langchain.com/blog/building-long-running-agents-with-scaledown-and-deep-agents
  title: Building long-running agents with ScaleDown and Deep Agents
  author: Sydney Runkle, Srimanth Tangedipalli and Neal Patel (LangChain)
  last_modified: '2026-10-13T00:00:00Z'
- id: scaledown-docs
  resource: https://docs.scaledown.ai
  title: ScaleDown documentation
- id: pypi
  resource: https://pypi.org/project/langchain-scaledown/
  title: langchain-scaledown on PyPI (0.2.0 as of 2026-10-16)
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-10-16T14:00:00+04:00'
---

ScaleDown sells **constrained decoding models (CDMs)**: "a CDM is trained for
one task and only returns answers that task allows, like a label from your list
or spans of the input."[^langchain-scaledown] Being narrow is what lets each
model be much smaller, faster and cheaper than a general LLM. It belongs to the
same family as [Jev](/ai-engineering/models/jev.md) and
[CLM](/ai-engineering/models/clm.md): models that return a bounded, typed answer
instead of free text that you parse afterwards.

## Models

| Model | Returns | Typical agent use |
| --- | --- | --- |
| Summarize | Abstractive summary of long text | Compact conversation history before the context fills |
| Compress | Only the parts of a context relevant to a query | Shrink tool output before the main model reads it |
| Extract | Described fields with confidence scores and source positions | Copy IDs, error codes and emails exactly instead of paraphrasing them |
| Classify | A probability per user-defined label, plus an optional one-sentence reason | Routing, triage, detecting a looping or drifting run |

All four accept up to 1M tokens. Extract, Summarize and Classify also take
images and scanned PDFs.[^langchain-scaledown] All four are behind one hosted
API.[^scaledown-docs]

## How it fits a harness: Deep Agents middleware

`langchain-scaledown` wires the models into
[Deep Agents](/ai-engineering/agents/deep-agents.md) as middleware, so the
frontier model never sees the raw bulk.[^pypi][^langchain-scaledown]

- **Summarization:** replaces Deep Agents' built-in history summarization,
  using the same `trigger`/`keep` options. If a call fails, the history is left
  unchanged and the agent keeps running.
- **Tool-output compression:** adds a `compression_query` argument to every
  tool call, MCP tools included, and compresses the result against it. In the
  post's trace a docs page went from 18,402 to 3,110 characters, about 83%
  (the post rounds this to "almost 90%"). The compressed result tells the model
  it can call again without the query to get the full output.
- **Extraction into state:** before the first model call, it pulls fields such
  as order ID, error message and email from *user messages only*. Values come
  from what the customer actually wrote. The issue type goes through Classify.
- **Circuit breaker (custom):** an `after_model` hook classifies the history
  as progressing, looping or drifting. It stops the run when a
  non-"progressing" label scores above 0.8 and includes the reason. A gentler
  variant feeds the reason back as a nudge first.

The principle is **"cheap by default, frontier on exception"**: keep the
general LLM for open-ended work (code, drafts, planning) and send the frequent,
high-volume context decisions to CDMs.[^langchain-scaledown] This is a
[context engineering](/ai-engineering/context/context-engineering.md) technique:
the main model's context window stays small without the harness dropping
information blindly.

## Compared with Jev

Classify is the closest to Jev: "both return a typed answer with a
probability." Jev takes text only, up to 32K tokens of state per question.
Classify takes up to 1M tokens, images included, and adds a one-sentence
reason to each decision.[^langchain-scaledown] Jev's primitives (Choice, Score,
Noul) are decision-only. ScaleDown also covers summarizing, compressing and
extracting context.

## Caveats

- **Vendor-reported numbers.** These are ScaleDown's own benchmarks against
  the average of three GPT-5.x models on public datasets: Summarize 41× cheaper
  and 2.7× faster, Compress 138× cheaper and 1.8× faster, both with higher
  accuracy, and "200x faster and 467x cheaper" on narrow tasks overall. The post
  does not verify them independently.[^langchain-scaledown]
- **Typed is not correct.** As with Jev, constrained output rules out malformed
  answers, not wrong ones. Calibrate thresholds such as the circuit breaker's
  0.8 on real traces, using the returned reason to debug.
- **Compression can drop what the agent needs.** Keep the full-output escape
  hatch, and evaluate on tasks where the detail matters.
- **Access.** The post routes calls through the LangSmith LLM Gateway
  (`/scaledown` path, workspace secret, traced and counted toward spend and
  rate limits) and offers 50M free tokens to new accounts. ScaleDown's docs say
  API keys come through sales.[^langchain-scaledown][^scaledown-docs]

## Resources

- [Building long-running agents with ScaleDown and Deep Agents](https://www.langchain.com/blog/building-long-running-agents-with-scaledown-and-deep-agents)
  (LangChain, 2026-10-13) — the four models, the middlewares, the circuit-breaker example.
- [ScaleDown documentation](https://docs.scaledown.ai)
- [langchain-scaledown](https://github.com/scaledown-team/langchain-scaledown) — middleware source.

[^langchain-scaledown]: LangChain blog, 2026-10-13
[^scaledown-docs]: ScaleDown documentation
[^pypi]: langchain-scaledown package

---
type: Decision Model
title: Jev
description: TypeSafe's System One model for fast typed decisions with probabilities, composed into software
  workflows.
resource: https://docs.typesafe.ai/
tags:
- ai-engineering
- models
parent: /ai-engineering/models.md
related:
- /ai-engineering/harness/programmatic-tool-calling.md
- /ai-engineering/harness.md
- /ai-engineering/observability/langsmith-evals.md
- /ai-engineering/models/clm.md
- /ai-engineering/models/scaledown.md
decision_interface:
- Choice
- Score
- Noul
serving_model: hosted
note_date: '2026-09-30'
sources:
- id: ref-1
  resource: https://docs.typesafe.ai/
  title: docs.typesafe.ai
- id: ref-2
  resource: https://typesafe.ai/
  title: 'TypeSafe: System One and RLCD'
- id: ref-3
  resource: https://github.com/Contrastive-LM/CLM
  title: CLM repository and Jev comparison
- id: langchain-scaledown
  resource: https://www.langchain.com/blog/building-long-running-agents-with-scaledown-and-deep-agents
  title: Building long-running agents with ScaleDown and Deep Agents
  author: Sydney Runkle, Srimanth Tangedipalli and Neal Patel (LangChain)
  last_modified: '2026-10-13T00:00:00Z'
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-10-16T14:00:00+04:00'
---

Reference: <https://docs.typesafe.ai/>

Note dated: 2026-09-30 18:00:00+00:00.

Jev is TypeSafe AI's first public **System One model**: supply a state and
well-scoped questions, and receive typed judgments directly. It is a decision
primitive for software, rather than a model that generates a textual answer
and then parses it into a schema. TypeSafe describes its training approach as
Reinforcement Learning for Calibrated Decisions (RLCD).

## Interface and uses

| Primitive | Question | Result |
| --- | --- | --- |
| Choice | Which supplied option fits? | Selected option, probability distribution, confidence |
| Score | Where does the state fall on an ordered rubric? | Score, probability distribution, confidence |
| Noul | Is this statement true? | A value between 0 and 1 |

Questions in a request are evaluated independently against the same state.
Decompose a compound judgment into atomic questions and combine the results in
code. Useful applications include intent and tool routing, candidate selection,
and confidence-gated automation in a workflow.
An [agent harness](/ai-engineering/harness.md) can use a decision model for frequent,
bounded choices while using a generative model for proposing candidates or
extended reasoning.

Typed output prevents malformed free-text answers; it does **not** establish
that a decision is correct. Validate accuracy and probability calibration on
representative data with [evals](/ai-engineering/observability/langsmith-evals.md), then choose
action and escalation thresholds based on the cost of mistakes. A closed set
of choices also needs an explicit fallback when none is appropriate.

## Open-source alternatives

[Contrastive Language Models (CLM)](/ai-engineering/models/clm.md) provide a separately trained,
open-source alternative with a TypeSafe-compatible decision API. CLM is not an
official open-source edition of Jev, nor evidence that Jev uses the same
architecture. The sources reviewed on 2026-09-30 establish hosted Jev access;
they do not establish a public Jev weight release. CLM is the concrete open
implementation verified in this review.

## Related constrained decoding models

[ScaleDown](/ai-engineering/models/scaledown.md) sells the same idea as
constrained decoding models (CDMs). Its Classify model is the closest
counterpart: a typed answer with a probability. Jev takes text only, up to 32K
tokens of state per question. Classify takes up to 1M tokens, images included,
and adds a one-sentence reason.[^langchain-scaledown] ScaleDown also has
Summarize, Compress and Extract models. LangChain wires them into
[Deep Agents](/ai-engineering/agents/deep-agents.md) as middleware, under the
same "cheap by default, frontier on exception" principle LangChain applies to
Jev.

## Resources

- [TypeSafe documentation: Jev and its primitives](https://docs.typesafe.ai/)
- [TypeSafe: System One and RLCD](https://typesafe.ai/)
- [CLM repository and Jev comparison](https://github.com/Contrastive-LM/CLM)
- [Building long-running agents with ScaleDown and Deep Agents](https://www.langchain.com/blog/building-long-running-agents-with-scaledown-and-deep-agents) — Jev vs ScaleDown Classify

[^langchain-scaledown]: LangChain blog, 2026-10-13

---
type: Concept
title: Context Engineering
description: Deliberately assembling what goes into the model's context window — instructions, tools,
  retrieved data, memory, and history.
tags:
- ai-engineering
- context
parent: /ai-engineering/context.md
related:
- /ai-engineering/harness/tools.md
- /ai-engineering/context/prompt-caching.md
- /ai-engineering/context/rag.md
- /ai-engineering/context/memory.md
sources:
- id: ref-1
  resource: https://docs.langchain.com/oss/python/deepagents/context-engineering
  title: docs.langchain.com
generated:
  by: antigravity/gemini-3-8-flash
  at: '2026-10-15T17:36:45+04:00'
---

Reference: <https://docs.langchain.com/oss/python/deepagents/context-engineering>

Context engineering is the practice of deliberately assembling everything the
model sees for a given step — system instructions, [tool](/ai-engineering/harness/tools.md)
definitions, [retrieved](/ai-engineering/context/rag.md) data, [memory](/ai-engineering/context/memory.md), and
conversation history — and managing the limited context window. It is the broader
successor discipline to prompt engineering.

A core principle of modern context engineering is designing for [prompt caching](/ai-engineering/context/prompt-caching.md). Because provider caches rely on prefix matching, context must be assembled with static components (base prompts, invariant tool schemas, project configs) positioned strictly before dynamic components (session context, recent tool results, user messages). Inadvertently modifying or reordering early context breaks caching across the entire conversation.

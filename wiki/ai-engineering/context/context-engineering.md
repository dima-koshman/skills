---
type: Concept
title: Context Engineering
aliases:
- Memory
- RAG
description: Deliberately assembling what goes into the model's context window — instructions, tools, retrieved
  data, memory, and history.
tags:
- ai-engineering
- context
parent: /ai-engineering/context.md
related:
- /ai-engineering/harness/tools.md
- /ai-engineering/context/prompt-caching.md
- /ai-engineering/context/skills.md
- /ai-engineering/context/tool-result-offloading.md
- /ai-engineering/multi-agent/subagents.md
- /ai-engineering/security.md
status: draft
sources:
- id: ref-1
  resource: https://docs.langchain.com/oss/python/deepagents/context-engineering
  title: docs.langchain.com
- id: chase-late-2026
  resource: https://www.langchain.com/blog/context-engineering-challenges-late-2026
  title: New context engineering challenges in late 2026
  author: Harrison Chase
  last_modified: '2026-11-02'
- id: memory-ref-1
  resource: https://docs.langchain.com/oss/python/deepagents/memory
  title: docs.langchain.com
- id: rag-ref-1
  resource: https://www.reddit.com/r/Rag/s/KDBqvK7pMb
  title: retrieval is not a vector store
- id: ref-2
  resource: https://www.reddit.com/r/Rag/comments/1m890yk/i_made_60k_building_rag_projects_in_3_months/
  title: metadata is everything
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-18T12:00:00+04:00'
---

Reference: <https://docs.langchain.com/oss/python/deepagents/context-engineering>

Context engineering is the practice of deliberately assembling everything the
model sees for a given step — system instructions, [tool](/ai-engineering/harness/tools.md)
definitions, [retrieved](/ai-engineering/context/context-engineering.md#retrieval-augmented-generation-rag) data, [memory](/ai-engineering/context/context-engineering.md#memory), and
conversation history — and managing the limited context window. It is the broader
successor discipline to prompt engineering.

A core principle of modern context engineering is designing for [prompt caching](/ai-engineering/context/prompt-caching.md). Because provider caches rely on prefix matching, context must be assembled with static components (base prompts, invariant tool schemas, project configs) positioned strictly before dynamic components (session context, recent tool results, user messages). Inadvertently modifying or reordering early context breaks caching across the entire conversation.

# Cornerstones

Harrison Chase lists the "standard-ish" solutions that agent harnesses have converged on as of late 2026:[^chase-late-2026]

| Technique | Problem it handles |
| --- | --- |
| Summarizing long threads | History outgrows the context window |
| [Offloading large tool results](/ai-engineering/context/tool-result-offloading.md) | One result is too big to keep in context |
| [Skills](/ai-engineering/context/skills.md) | Instructions load only when relevant (progressive disclosure) |
| [Tool search](/ai-engineering/harness/tool-search.md) | Too many tools to list up front |
| [Subagents](/ai-engineering/multi-agent/subagents.md) | Isolate a subtask's context from the main thread |
| Bash as a primary tool | Replaces many specialized tools |

His argument is that these solve the known problems, and that proactive, always-on, goal-oriented agents raise new ones: when to interrupt, what to remember, async work, goal tracking, alignment and browser use. He says the industry doesn't necessarily have general solutions for those yet.[^chase-late-2026]

# Memory

Reference: <https://docs.langchain.com/oss/python/deepagents/memory>

Memory is how an agent retains information beyond a single model call: short-term
working memory in the context window, and long-term memory persisted externally
(often a vector store) and retrieved when relevant. It lets an agent accumulate
state across steps and sessions — and is a target for
[poisoning](/ai-engineering/security.md#risks-owasp-agentic-top-10).

# Retrieval-Augmented Generation (RAG)

Retrieval-augmented generation — fetching relevant documents at query time and adding them to the model's context.

While strictly speaking retrieval-augmented generation doesn't have to be based on vector embeddings and semantic similarity search, in practice that's what is usually implied when people mention RAG. Powerful technique, but doesn't suit all use cases - doesn't work well for structured or semi-structured data or data that changes frequently - embeddings are not directly linked to original text and require re-indexing. Additionally, it requires a lot of maintenance and complex setup - need to normalize text, deal with structured data, chunking, etc.

RAG is one of the techniques used in
[context engineering](/ai-engineering/context/context-engineering.md).

Some discussions about RAG highlighting the need for custom approaches and complex data engineering pipelines, as well as retrieval techniques:

- > [retrieval is not a vector store](https://www.reddit.com/r/Rag/s/KDBqvK7pMb)

- > [metadata is everything](https://www.reddit.com/r/Rag/comments/1m890yk/i_made_60k_building_rag_projects_in_3_months/)

[^chase-late-2026]: Harrison Chase, LangChain blog, 2026-11-02.

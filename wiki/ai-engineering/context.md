---
type: Knowledge Area
title: Context and Knowledge
description: Context assembly, memory, retrieval, skills, and portable knowledge formats for agents.
tags:
- ai-engineering
- context
parent: /ai-engineering.md
topics:
- /ai-engineering/context/context-engineering.md
- /ai-engineering/context/mcp.md
- /ai-engineering/context/memory.md
- /ai-engineering/context/okf-visualizers.md
- /ai-engineering/context/okf.md
- /ai-engineering/context/openwiki.md
- /ai-engineering/context/prompt-caching.md
- /ai-engineering/context/rag.md
- /ai-engineering/context/skills.md
generated:
  by: antigravity/gemini-3-8-flash
  at: '2026-10-15T17:36:30+04:00'
---

## Topics

- [Context Engineering](/ai-engineering/context/context-engineering.md) — Deliberately assembling what goes into the model's context window — instructions, tools, retrieved data, memory, and history.
- [Model Context Protocol (MCP)](/ai-engineering/context/mcp.md) — Open protocol standardizing how LLM apps expose and consume tools, resources, and prompts.
- [Memory](/ai-engineering/context/memory.md) — How an agent carries state across steps and sessions — short-term context plus durable long-term stores.
- [OKF Visualizers](/ai-engineering/context/okf-visualizers.md) — Comparison of the upstream static HTML viewer with our custom graph-and-reader renderer, including adoption instructions and compatibility limits.
- [Open Knowledge Format (OKF)](/ai-engineering/context/okf.md) — Google's vendor-neutral markdown-plus-frontmatter standard for agent-readable knowledge.
- [OpenWiki](/ai-engineering/context/openwiki.md) — LangChain's early-stage CLI for generating and maintaining agent-facing Markdown wikis from local knowledge sources.
- [Prompt Caching](/ai-engineering/context/prompt-caching.md) — Reusing cached prefix tokens across LLM requests to minimize latency and token costs, and how to design agent harnesses around cache preservation.
- [RAG](/ai-engineering/context/rag.md) — Retrieval-augmented generation — fetching relevant documents at query time and adding them to the model's context.
- [Agent Skills](/ai-engineering/context/skills.md) — Packaged instruction files an agent loads on demand — most useful as behavior control, and a context tax when installed indiscriminately.

---
type: Knowledge Area
title: Context
description: "What goes into the model's context window and how to manage it: context engineering, memory, retrieval, prompt caching, tool result offloading and skills."
tags:
- ai-engineering
- context
parent: /ai-engineering.md
topics:
- /ai-engineering/context/context-engineering.md
- /ai-engineering/context/prompt-caching.md
- /ai-engineering/context/skills.md
- /ai-engineering/context/tool-result-offloading.md
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-18T12:00:00+04:00'
---

## Topics

- [Context Engineering](/ai-engineering/context/context-engineering.md) — Deliberately assembling what goes into the model's context window — instructions, tools, retrieved data, memory, and history.
- [Prompt Caching](/ai-engineering/context/prompt-caching.md) — Reusing cached prefix tokens across LLM requests to minimize latency and token costs, and how to design agent harnesses around cache preservation.
- [Agent Skills](/ai-engineering/context/skills.md) — Packaged instruction files an agent loads on demand — most useful as behavior control, and a context tax when installed indiscriminately.
- [Tool Result Offloading](/ai-engineering/context/tool-result-offloading.md) — Store a large tool result outside the context window and keep only a path and preview, so the model can fetch the rest when it needs it.

---
type: Technique
title: Context Engineering
description: Deliberately assembling what goes into the model's context window — instructions, tools, retrieved data, memory, and history.
resource: https://docs.langchain.com/oss/python/deepagents/context-engineering
---

Context engineering is the practice of deliberately assembling everything the
model sees for a given step — system instructions, [tool](/harness/tools.md)
definitions, [retrieved](/context/rag.md) data, [memory](/context/memory.md), and
conversation history — and managing the limited context window. It is the broader
successor discipline to prompt engineering.

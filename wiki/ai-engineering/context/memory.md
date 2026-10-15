---
type: Concept
title: Memory
description: How an agent carries state across steps and sessions — short-term context plus durable long-term
  stores.
tags:
- ai-engineering
- context
parent: /ai-engineering/context.md
related:
- /ai-engineering/security/risks/memory-context-poisoning.md
sources:
- id: ref-1
  resource: https://docs.langchain.com/oss/python/deepagents/memory
  title: docs.langchain.com
generated:
  by: codex/gpt-6
  at: '2026-10-15T15:23:06+04:00'
---

Reference: <https://docs.langchain.com/oss/python/deepagents/memory>

Memory is how an agent retains information beyond a single model call: short-term
working memory in the context window, and long-term memory persisted externally
(often a vector store) and retrieved when relevant. It lets an agent accumulate
state across steps and sessions — and is a target for
[poisoning](/ai-engineering/security/risks/memory-context-poisoning.md).

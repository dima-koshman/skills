---
type: Technique
title: Memory
description: How an agent carries state across steps and sessions — short-term context plus durable long-term stores.
resource: https://docs.langchain.com/oss/python/deepagents/memory
---

Memory is how an agent retains information beyond a single model call: short-term
working memory in the context window, and long-term memory persisted externally
(often a vector store) and retrieved when relevant. It lets an agent accumulate
state across steps and sessions — and is a target for
[poisoning](/security/risks/memory-context-poisoning.md).

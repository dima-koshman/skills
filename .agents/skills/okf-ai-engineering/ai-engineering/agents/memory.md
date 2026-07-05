---
type: Concept
title: Memory
description: How an agent carries state across steps and sessions — short-term context plus durable long-term stores.
tags: [agents, memory, state]
timestamp: 2026-07-05T00:00:00Z
---

Memory is how an agent retains information beyond a single model call: short-term
working memory in the context window, and long-term memory persisted externally
(often a vector store) and retrieved when relevant. It lets an agent accumulate
state across steps and sessions — and is a target for
[poisoning](/security/threats/memory-context-poisoning.md).

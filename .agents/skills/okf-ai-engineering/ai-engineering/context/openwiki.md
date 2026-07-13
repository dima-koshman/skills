---
type: Product
title: OpenWiki
description: LangChain's early-stage CLI for generating and maintaining agent-facing Markdown wikis from local knowledge sources.
resource: https://github.com/langchain-ai/openwiki
---

OpenWiki generates and maintains local Markdown knowledge for agents. Code mode
writes repository documentation, while personal mode synthesizes configured
sources into `~/.openwiki/wiki` for cross-project continuity.

# How it works

Connectors first write deterministic raw snapshots and manifests locally.
Source-specific agent runs then synthesize those artifacts into wiki pages,
while the raw artifacts remain available for provenance checks. Generated pages
may link back to that evidence, but citations are not enforced. Scheduled
ingestion can keep the wiki fresh without placing the full source corpus into
every agent context.

# Where it fits

OpenWiki is a product implementation of durable [Memory](/context/memory.md) and
selective [Context Engineering](/context/context-engineering.md). Like
[RAG](/context/rag.md), it retrieves external context for a task, but it
pre-synthesizes that context into an agent-oriented wiki rather than retrieving
raw chunks only at query time.

Its current value is strongest for broad context, trends, commitments, and
cross-project continuity. For concrete engineering work, generated summaries
should remain leads: current source files, Git history, tests, and other primary
evidence are more authoritative.

# Resources

- [OpenWiki repository](https://github.com/langchain-ai/openwiki)

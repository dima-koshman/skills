---
type: Tool
title: OpenWiki
description: LangChain's early-stage CLI for generating and maintaining agent-facing Markdown wikis from
  local knowledge sources.
resource: https://github.com/langchain-ai/openwiki
tags:
- ai-engineering
- context
parent: /ai-engineering/context.md
related:
- /ai-engineering/context/memory.md
- /ai-engineering/context/context-engineering.md
- /ai-engineering/context/rag.md
input_bundle: wiki/
output_bundle: openwiki/
role: OKF-to-OKF synthesis experiment
sources:
- id: ref-1
  resource: https://github.com/langchain-ai/openwiki
  title: github.com
generated:
  by: codex/gpt-6
  at: '2026-10-15T15:23:06+04:00'
---

Reference: <https://github.com/langchain-ai/openwiki>

OpenWiki generates and maintains local Markdown knowledge for agents. Code mode
writes repository documentation, while personal mode synthesizes configured
sources into `~/.openwiki/wiki` for cross-project continuity.

## Local experiment (2026-10-15)

The maintained `wiki/` input is already a complete OKF v0.2 bundle. OpenWiki
transforms it into another bundle in `openwiki/` so we can test synthesis,
reorganization, Claims, and update behavior. Editorial control stays with the
source bundle, including its type schemas, typed relationships, and matching
directory-overview concepts. The generated bundle remains derived material.

Use **Wiki: regenerate, render and open** to compare either bundle with the same
custom renderer; `wiki/` is the default choice. The generation brief tells
OpenWiki how to interpret source-root links and preserve useful custom properties.

## How it works

Connectors first write deterministic raw snapshots and manifests locally.
Source-specific agent runs then synthesize those artifacts into wiki pages,
while the raw artifacts remain available for provenance checks. Generated pages
may link back to that evidence, but citations are not enforced. Scheduled
ingestion can keep the wiki fresh without placing the full source corpus into
every agent context.

## Where it fits

OpenWiki is a product implementation of durable [Memory](/ai-engineering/context/memory.md) and
selective [Context Engineering](/ai-engineering/context/context-engineering.md). Like
[RAG](/ai-engineering/context/rag.md), it retrieves external context for a task, but it
pre-synthesizes that context into an agent-oriented wiki rather than retrieving
raw chunks only at query time.

Its current value is strongest for broad context, trends, commitments, and
cross-project continuity. For concrete engineering work, generated summaries
should remain leads: current source files, Git history, tests, and other primary
evidence are more authoritative.

## Resources

- [OpenWiki repository](https://github.com/langchain-ai/openwiki)

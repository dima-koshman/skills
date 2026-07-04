---
type: Knowledge Format
title: Open Knowledge Format (OKF)
description: Google's vendor-neutral markdown-plus-frontmatter standard for agent-readable knowledge.
resource: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md
tags: [knowledge, standards, agents]
timestamp: 2026-07-04T00:00:00Z
---

OKF represents knowledge — the metadata and curated context around data and
systems — as a directory of markdown files with YAML frontmatter. One concept
per file; the file path is the concept's identity. No schema registry, no
central authority, no required tooling. This very bundle is an OKF bundle.

## In an enterprise platform

For an enterprise AI platform, the hard part of "give the agent context" is
governance, not storage: knowledge must be diffable, reviewable, portable across
tools, and free of vendor lock-in. OKF is deliberately the *lowest-common-
denominator* format — plain markdown in git — which is exactly what makes it
survive tool churn and cross-org exchange. It is the knowledge substrate an
agent reads; it is not itself a capability or a runtime.

## Design considerations

- **`type` is the only required field.** Everything else (title, description,
  resource, tags, timestamp) is recommended-but-optional; consumers must degrade
  gracefully. Permissive consumption is a feature, not a gap.
- **Links are untyped** — a link asserts a relationship; the *kind* lives in
  surrounding prose. Good for a knowledge graph, not a substitute for a schema.
- **`index.md` is a build artifact** — generate it from frontmatter, never hand-
  edit. This bundle is indexed by the `okf` skill's `okf_index.py`.
- **Snapshot vs. mirror** — a young draft (v0.1) will move; pin the version and
  reconcile deliberately rather than tracking a live upstream.

## Relationship

OKF is *knowledge* (declarative facts), distinct from an agent **skill**
(procedural capability) and from [MCP](/context/mcp.md) (a transport for tools
and resources). An agent could consume an OKF bundle as its knowledge base while
a skill provides the procedure to traverse it and MCP exposes the live tools.

# Citations

[1] [OKF specification](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
[2] [How the Open Knowledge Format can improve data sharing — Google Cloud](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing)

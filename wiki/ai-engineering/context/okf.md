---
type: Knowledge Format
title: Open Knowledge Format (OKF)
description: Google's vendor-neutral markdown-plus-frontmatter standard for agent-readable knowledge.
resource: https://github.com/GoogleCloudPlatform/open-knowledge-format
tags:
- ai-engineering
- context
parent: /ai-engineering/context.md
related:
- /ai-engineering/context/mcp.md
- /ai-engineering/context/okf-visualizers.md
format_version: '0.2'
concept_encoding: Markdown with YAML frontmatter
note_date: '2026-09-30'
sources:
- id: ref-1
  resource: https://github.com/GoogleCloudPlatform/open-knowledge-format
  title: github.com
- id: ref-2
  resource: https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md
  title: OKF v0.2 specification and v0.1 changelog (§13)
- id: ref-3
  resource: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md
  title: Earlier specification location, also serving v0.2 when checked
- id: ref-4
  resource: https://okf.md/tools/
  title: OKF tools directory
generated:
  by: codex/gpt-6
  at: '2026-10-15T15:23:06+04:00'
---

Reference: <https://github.com/GoogleCloudPlatform/open-knowledge-format>

Note dated: 2026-09-30 18:00:00+00:00.

OKF represents knowledge — the metadata and curated context around data and
systems — as a directory of markdown files with YAML frontmatter. One concept
per file; the file path is the concept's identity. No schema registry, no
central authority, no required tooling. This very bundle is an OKF bundle.

## Relationship with skills

OKF is *knowledge* (declarative facts), distinct from an agent **skill**
(procedural capability) and from [MCP](/ai-engineering/context/mcp.md) (a transport for tools
and resources). An agent could consume an OKF bundle as its knowledge base while
a skill provides the procedure to traverse it and MCP exposes the live tools.

## Local OKF v0.2 bundle

The local authoring skill, vendored specification, and index generator target
**OKF v0.2**. As of 2026-10-15, `wiki/` itself is the maintained source bundle;
`openwiki/` is separately generated for testing OpenWiki's OKF-to-OKF synthesis.
The older 2026-09-30 note described a local v0.1 pin; that local state has been
superseded. Existing dated external observations are retained as historical context.

The core remains a directory of Markdown concepts with `type` as the only
always-required field. Reserved `index.md` and `log.md`, cross-linking, and
permissive consumption remain. The new version makes provenance and trust
machine-readable:

| Area | v0.2 convention |
| --- | --- |
| Provenance | `sources` entries with a required `resource` and optional stable `id`; claim footnotes join to those IDs |
| Authorship and freshness | `generated: { by, at }`; optional absolute `stale_after` instant |
| Verification | `verified` events, separate from authorship; consumers derive unverified, machine-confirmed, or human-reviewed trust tiers |
| Lifecycle | `status` of `draft`, `stable`, or `deprecated`; absence means stable |
| Computation | `Attested Computation` concepts with executor, receipt, and deterministic attester conventions |

Despite the minor version number, upstream explicitly calls out two breaking
changes: `timestamp` is superseded by `generated.at`, and body `# Citations`
lists are superseded by frontmatter `sources`. A v0.2 consumer can still consume
v0.1 documents with the documented fallbacks. The conversion retains `# Resources` reading links and also records the existing
external references in structured `sources`; that extraction is not a new source check.

## Local consumer extensions

A sibling `topic.md` concept and `topic/` directory share a reader sidebar section
and graph node. Local `_types/` concepts use `type: Concept Type`; their attribute
tables provide hover descriptions, while `primary_fields` selects prominent YAML
properties and folds other custom fields under Technical details. These schema
pages stay out of the reader graph. Frontmatter concept paths become labeled
edges, and Mermaid fences render as diagrams. These are local consumer choices;
OKF permits custom keys without requiring other consumers to implement this UI.

Use **Wiki: regenerate, render and open** to choose `wiki/` (default) or
`openwiki/`. The [visualizer comparison](/ai-engineering/context/okf-visualizers.md)
retains the historical upstream evaluation and records the local rendering workflow.

## Resources

- [OKF v0.2 specification and v0.1 changelog (§13)](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md)
- [Earlier specification location, also serving v0.2 when checked](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
- [OKF tools directory](https://okf.md/tools/)

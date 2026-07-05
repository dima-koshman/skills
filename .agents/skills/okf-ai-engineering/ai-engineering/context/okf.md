---
type: Standard
title: Open Knowledge Format (OKF)
description: Google's vendor-neutral markdown-plus-frontmatter standard for agent-readable knowledge.
resource: https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf
---

OKF represents knowledge — the metadata and curated context around data and
systems — as a directory of markdown files with YAML frontmatter. One concept
per file; the file path is the concept's identity. No schema registry, no
central authority, no required tooling. This very bundle is an OKF bundle.

# Relationship with skills

OKF is *knowledge* (declarative facts), distinct from an agent **skill**
(procedural capability) and from [MCP](/context/mcp.md) (a transport for tools
and resources). An agent could consume an OKF bundle as its knowledge base while
a skill provides the procedure to traverse it and MCP exposes the live tools.

# Resources

- [OKF specification](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)

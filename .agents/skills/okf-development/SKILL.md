---
name: okf-development
description: >
  Curated, vendor-neutral knowledge base of general software-development and
  distributed-systems concepts — Protocol Buffers, gRPC, service mesh (Istio),
  and the data/control/management plane model. Use when asked about any of these
  concepts, or to explore, extend, or refresh the development knowledge graph.
  It is an OKF bundle — browse or render it with the `okf` skill's tooling.
---

# Development Knowledge Base

The `development/` directory is an OKF bundle of general software-development and
distributed-systems concepts — the non-AI-specific counterpart to the
`okf-ai-engineering` bundle. Notes are written for a senior practitioner: design
framing, trade-offs, and vetted primary sources, not beginner explainers or
vendor tutorials.

## What's here

- **communication/** — service contracts and transport: Protocol Buffers and gRPC.
- **infrastructure/** — the layer around services: the service mesh (Istio), and
  the data/control/management plane decomposition.

## How to use it

- **Read** `development/index.md` for the full catalog; each concept is one
  markdown file with frontmatter, cross-linked into a graph.
- **Browse** it visually: render `development/okf-site.html` with the `okf`
  skill's `okf_site.py development/` (interactive knowledge graph + reader).
- **Edit or extend** it via the `okf` skill: after changing concepts, regenerate
  `development/index.md` with `okf_index.py development/` and add a dated entry
  to `development/log.md`. Refresh cited sources periodically — see the `okf`
  skill's "Refreshing a knowledge base".

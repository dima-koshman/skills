---
name: okf-ai-engineering
description: >
  Curated, vendor-neutral knowledge base of enterprise AI-engineering concepts —
  MCP, the LLM and MCP gateways, agent architecture, deepagents, observability
  (LangSmith, Langfuse), evals, and the OWASP Agentic Top 10 security threats.
  Use when asked about any of these concepts, or to explore, extend, or refresh
  the AI-engineering knowledge graph. It is an OKF bundle — browse or render it
  with the `okf` skill's tooling.
---

# AI Engineering Knowledge Base

The `ai-engineering/` directory is an [OKF](ai-engineering/context/okf.md) bundle of the concepts behind
building enterprise-grade AI services — an AI platform, an MCP gateway, and a PII
masker. Notes are written for a senior practitioner: design framing and vetted
sources, not beginner explainers, vendor tutorials, or model training.

## What's here

- **context/** — the protocols this is built on: MCP and the Open Knowledge Format.
- **enterprise/** — the control plane: the LLM Gateway and the MCP Gateway.
- **agents/** — agent architecture, deepagents, the harness, programmatic tools.
- **observability/** — tracing, with LangSmith and Langfuse.
- **evaluation/** — evals & LLM-as-judge, operationalized via LangSmith Evals.
- **security/** — the OWASP Agentic Top 10 threats and the controls that contain
  them (guardrails, PII masking).

## How to use it

- **Read** `ai-engineering/index.md` for the full catalog; each concept is one markdown file
  with frontmatter, cross-linked into a graph. Anchoring project work:
  [Bir MCP](https://gitlab.com/koshmandk/bir_mcp),
  [agents](https://github.com/dima-koshman/agents).
- **Browse** it visually: render `ai-engineering/okf-site.html` with the `okf` skill's
  `okf_site.py ai-engineering/` (interactive knowledge graph + reader).
- **Edit or extend** it via the `okf` skill: after changing concepts, regenerate
  `ai-engineering/index.md` with `okf_index.py ai-engineering/` and add a dated entry to `ai-engineering/log.md`.
  Refresh cited sources periodically — see the `okf` skill's "Refreshing a
  knowledge base".

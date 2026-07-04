# Directory Update Log

## 2026-07-05

* **Reorganization**: Restructured the bundle into `context/`, `enterprise/`, `agents/`, `observability/`, `evaluation/`, and `security/` — renamed the session-specific `meta/` to `context/` and moved every concept to its new home.
* **Creation**: Adopted the [OWASP Agentic Top 10](/security/threats/asi01-agent-goal-hijack.md) as `security/threats/` (ASI01–ASI10; the former Prompt Injection concept became [ASI01: Agent Goal Hijack](/security/threats/asi01-agent-goal-hijack.md)); moved [Guardrails](/security/controls/guardrails.md) and [PII Masking](/security/controls/pii-masking.md) to `security/controls/`.
* **Creation**: Scaffolded new concepts — [MCP Gateway](/enterprise/mcp-gateway.md), [deepagents](/agents/deepagents.md), [Agent Harness](/agents/harness.md), [Programmatic Tools & Code Mode](/agents/programmatic-tools.md), [LangSmith](/observability/langsmith.md), [Langfuse](/observability/langfuse.md), and [LangSmith Evals](/evaluation/langsmith-evals.md) — frontmatter and cross-links complete, bodies to be filled in.

## 2026-07-04

* **Initialization**: Created the AI-engineering concept bundle — a cross-linked, vendor-neutral knowledge graph tuned to enterprise AI-platform work (platform + gateway + PII masker).
* **Creation**: Added meta concept [Open Knowledge Format](/context/okf.md).
* **Creation**: Added platform concepts [MCP](/context/mcp.md), [LLM Gateway](/enterprise/llm-gateway.md), and [Agent Architecture](/agents/agent-architecture.md).
* **Creation**: Added security concepts [Prompt Injection](/security/threats/asi01-agent-goal-hijack.md), [Guardrails](/security/controls/guardrails.md), and [PII Masking & Anonymization](/security/controls/pii-masking.md).
* **Creation**: Added lifecycle concepts [AI Observability & Tracing](/observability/observability.md) and [Evals & LLM-as-Judge](/evaluation/evals.md).
* **Update**: Switched PDF citations to canonical source URLs (Anthropic, LangChain, OWASP) so the bundle stays pure markdown and portable; local PDFs are no longer bundle dependencies.
* **Creation**: Added a root [Overview](/README.md) (`type: Overview`) as the knowledge-base landing page.
* **Update**: Restyled every concept body to clearer sections — `In an enterprise platform` and `Design considerations` — replacing the ambiguous "Why it matters" / "Key decisions" headings.

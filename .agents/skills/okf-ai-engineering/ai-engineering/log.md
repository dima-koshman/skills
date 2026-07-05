# Directory Update Log

## 2026-07-05

* **Reorganization**: Renamed the bundle directory `okf/` → `ai-engineering/` (updated the skill's SKILL.md and the VS Code build task). Site nav now lists concept pages above subdirectories, and the landing link reads "Index".
* **Creation**: Added area overview [Security](/security/security.md) (OWASP Agentic Top 10 threats + controls) and a general [AI Engineering](/ai-engineering.md) map concept.
* **Update**: Simplified `security/threats/` — each ASI concept is now just its definition (dropped the enterprise-framing, design-consideration, and citation sections).
* **Update**: Renamed `agents/agent-architecture.md` → [agents/agent.md](/agents/agent.md) and repaired all inbound links. Removed the general `observability/observability.md` and `evaluation/evals.md` concepts, stripping the now-dangling links (observability/evals live on as the vendor-tool concepts).
* **Update**: Trimmed citations across concepts to only genuinely-referenced sources, renamed `# Citations` to `# Resources`. Disabled markdownlint MD013 (line length) alongside MD025/MD041 for the OKF prose style.
* **Reorganization**: Split the skill from the bundle — the OKF bundle now lives in `okf/` with `SKILL.md` beside it, so the directory is both a proper agent skill and a fully spec-compliant OKF bundle (no reserved-filename special-casing for `SKILL.md`/`README.md`).
* **Update**: Site generator — added a clickable type-color **legend** above the graph (selecting a type highlights all its concepts in the graph and the nav tree), surfaced each concept's `description` on its page, and made the bundle `index.md` the HTML landing page.
* **Update**: Refactored `SKILL.md` into a lean agent-facing skill (routing + how-to) rather than a site landing description.
* **Update**: Formatting pass across concepts — citations rendered as markdown lists (line breaks), and level-2 body headings promoted to level-1 for consistency with `# Citations`. Added a repo-root `.markdownlint.json` disabling MD025/MD041, which OKF's multi-`#` convention intentionally trips.
* **Reorganization**: Restructured the bundle into `context/`, `enterprise/`, `agents/`, `observability/`, `evaluation/`, and `security/` — renamed the session-specific `meta/` to `context/` and moved every concept to its new home.
* **Creation**: Adopted the [OWASP Agentic Top 10](/security/threats/asi01-agent-goal-hijack.md) as `security/threats/` (ASI01–ASI10; the former Prompt Injection concept became [ASI01: Agent Goal Hijack](/security/threats/asi01-agent-goal-hijack.md)); moved [Guardrails](/security/controls/guardrails.md) and [PII Masking](/security/controls/pii-masking.md) to `security/controls/`.
* **Creation**: Scaffolded new concepts — [MCP Gateway](/enterprise/mcp-gateway.md), [deepagents](/agents/deepagents.md), [Agent Harness](/agents/harness.md), [Programmatic Tools & Code Mode](/agents/programmatic-tools.md), [LangSmith](/observability/langsmith.md), [Langfuse](/observability/langfuse.md), and [LangSmith Evals](/evaluation/langsmith-evals.md) — frontmatter and cross-links complete, bodies to be filled in.
* **Reorganization**: Moved the bundle into `.agents/skills/okf-ai-engineering/` and converted `README.md` to `SKILL.md` (added skill `name` and `description`), making the knowledge base a discoverable, distributable skill while keeping it a conformant OKF bundle.
* **Update**: Filled the ASI02–ASI10 threat bodies (enterprise framing + design considerations with cross-links). The vendor/tooling concepts (LangSmith, Langfuse, LangSmith Evals, deepagents, Agent Harness, Programmatic Tools, MCP Gateway) remain scaffolds pending domain input.

## 2026-07-04

* **Initialization**: Created the AI-engineering concept bundle — a cross-linked, vendor-neutral knowledge graph tuned to enterprise AI-platform work (platform + gateway + PII masker).
* **Creation**: Added meta concept [Open Knowledge Format](/context/okf.md).
* **Creation**: Added platform concepts [MCP](/context/mcp.md), [LLM Gateway](/enterprise/llm-gateway.md), and [Agent Architecture](/agents/agent.md).
* **Creation**: Added security concepts [Prompt Injection](/security/threats/asi01-agent-goal-hijack.md), [Guardrails](/security/controls/guardrails.md), and [PII Masking & Anonymization](/security/controls/pii-masking.md).
* **Creation**: Added lifecycle concepts AI Observability & Tracing and Evals & LLM-as-Judge (later removed; observability/evals now live as the vendor-tool concepts).
* **Update**: Switched PDF citations to canonical source URLs (Anthropic, LangChain, OWASP) so the bundle stays pure markdown and portable; local PDFs are no longer bundle dependencies.
* **Creation**: Added a root `SKILL.md` (`type: Overview`) as the knowledge-base landing page.
* **Update**: Restyled every concept body to clearer sections — `In an enterprise platform` and `Design considerations` — replacing the ambiguous "Why it matters" / "Key decisions" headings.

# Directory Update Log

## 2026-07-20

* **Creation**: Added [Agent Skills](/context/skills.md), capturing the finding that skills are diverging into two roles — a knowledge source whose value decays as frontier models improve, and behavior control whose value does not — and that skills structurally fail at the second, because an on-demand skill only fires when the agent recognizes the moment, which is precisely what discipline rules cannot rely on. Records the resulting practice: prefer `AGENTS.md` to generic plugins for behavior control, install skills selectively and project-scoped, audit against real invocation counts, extract rules from third-party skills rather than importing them wholesale, and treat installed skills as code-level supply-chain dependencies.

## 2026-07-13

* **Creation**: Added [OpenWiki](/context/openwiki.md), LangChain's early-stage CLI for synthesizing local sources into agent-facing code and personal-memory wikis, with explicit provenance and primary-evidence boundaries.
* **Creation**: Refactored [LLM Leaderboards](/providers/leaderboards.md) from plain markdown into an OKF concept — added `Reference` frontmatter (title, description, tags, timestamp), replaced the H1 and "Last updated" line with a linked intro that ties it to [LangSmith Evals](/observability/langsmith-evals.md) and the [Claude](/providers/claude.md)/[GPT](/providers/gpt.md)/[Gemini](/providers/gemini.md) pricing notes, promoted section headings to top-level, and dropped the horizontal-rule separators.

## 2026-07-11

* **Creation**: Added [Observability-Driven AI-Assisted Development](/development/observability-driven-development.md), defining the vendor-neutral loop that lets coding agents retrieve and correlate real runtime evidence for reactive debugging, proactive retrospectives, bounded remediation, and verification.
* **Creation**: Refactored the new provider pricing notes [Claude](/providers/claude.md), [OpenAI](/providers/gpt.md), and [Gemini](/providers/gemini.md) from plain markdown into OKF concepts — added `Product` frontmatter with `resource` pricing links, dropped the H1 in favor of a linked intro sentence, promoted sections to top-level headings, renamed "Official sources" to `# Citations`, and cross-linked the three providers to each other and to [Provider-Side Tools](/harness/provider-tools.md), [Context Engineering](/context/context-engineering.md), and [LLM Gateway](/enterprise/llm-gateway.md).

## 2026-07-06

* **Update**: Added current Claude, OpenAI, and Gemini examples with official documentation to [Provider-Side Tools](/harness/provider-tools.md), clarifying which tools execute on provider infrastructure.
* **Creation**: Added [Peer Agents](/agents/peer-agents.md), distinguishing independently governed peers from task-scoped subagents while documenting their shared implementation primitives and reduction boundary.
* **Reorganization**: Moved [Tools](/harness/tools.md), [Provider-Side Tools](/harness/provider-tools.md), and [Frontend Tools](/harness/frontend-tools.md) into `harness/` and repaired inbound links.
* **Update**: Made mobile search open the Contents panel as soon as the user types so filtered results are immediately visible.
* **Update**: Made the generated knowledge-graph site mobile-friendly with reading-first navigation and on-demand Contents and Graph panels.

## 2026-07-05

* **Reorganization**: Renamed `security/threats/` → `security/risks/` (type `Threat` → `Security risk`) and `security/controls/` → `security/mitigations/` — "risk" and "mitigation" are the accurate words (mitigations minimize risk, they don't eliminate it). Updated the Security overview wording and repaired all links.
* **Creation**: Seeded concrete agent concepts [Claude Code](/agents/claude-code.md), [opencode](/agents/opencode.md), [Codex](/agents/codex.md), [Devin](/agents/devin.md), and [Antigravity](/agents/antigravity.md).
* **Reorganization**: Split the agents area — `harness/` holds the machinery ([harness](/harness/harness.md), [subagents](/harness/subagents.md), [workflows](/harness/workflows.md)); `agents/` holds [agent architecture](/agents/agent.md) plus the concrete agents. Moved [Memory](/context/memory.md) into `context/`.
* **Update**: Removed `tags` and `timestamp` from every concept's frontmatter as clutter (the site still renders tags when present).
* **Update**: Full review pass. Dropped every `# Related` section — cross-references now read as prose in each concept's body (dropped ones that didn't fit). Balanced [MCP](/context/mcp.md) with why it was stateful (one-time negotiation, server-initiated push, local-stdio origin). Fixed the `workflows` description typos; normalized unnecessary title quotes.
* **Creation**: Added concise concepts [RAG](/context/rag.md), [Context Engineering](/context/context-engineering.md), [Memory](/context/memory.md), [Subagents & Multi-Agent](/harness/subagents.md), [Provider-Side Tools](/harness/provider-tools.md), and [Frontend Tools](/harness/frontend-tools.md) (bare definitions to expand later).
* **Reorganization**: Folded `evaluation/` into `observability/` (moved LangSmith Evals); kept `tools/` as its own area and split out provider-side and frontend tools.

* **Update**: Expanded [Agent Architecture](/agents/agent.md) (what distinguishes an agent — the model directs control flow — plus its ingredients) and added a `# Related` section wiring it to the harness, workflows, tools, and deepagents.
* **Update**: [MCP](/context/mcp.md) — recorded the stateless-by-default redesign with tracking links: requested in SEP-1442, accepted as SEP-2575 (merged May 2026, targeting the 2026-07-28 spec). Revisit when that revision ships.
* **Creation**: Added foundational concept [Tools](/harness/tools.md) (the primitive behind agents; client-side vs provider-side execution) and wired it into the catalog.
* **Reorganization**: Renamed `agents/programmatic-tools.md` → [agents/workflows.md](/harness/workflows.md) (retitled "Workflows") and repaired inbound links. Dropped the `ASI-NN` prefix from every `security/threats/` filename and title (e.g. `asi01-agent-goal-hijack.md` → `agent-goal-hijack.md`).
* **Update**: Tightened the [Agent Harness](/harness/harness.md) definition (runtime that drives the model→tool loop) and fixed a YAML-truncated description on [Agent Goal Hijack](/security/risks/agent-goal-hijack.md).
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
* **Creation**: Adopted the [OWASP Agentic Top 10](/security/risks/agent-goal-hijack.md) as `security/threats/` (ASI01–ASI10; the former Prompt Injection concept became [Agent Goal Hijack](/security/risks/agent-goal-hijack.md)); moved [Guardrails](/security/mitigations/guardrails.md) and [PII Masking](/security/mitigations/pii-masking.md) to `security/controls/`.
* **Creation**: Scaffolded new concepts — [MCP Gateway](/enterprise/mcp-gateway.md), [deepagents](/agents/deep-agents.md), [Agent Harness](/harness/harness.md), [Workflows](/harness/workflows.md), [LangSmith](/observability/langsmith.md), [Langfuse](/observability/langfuse.md), and [LangSmith Evals](/observability/langsmith-evals.md) — frontmatter and cross-links complete, bodies to be filled in.
* **Reorganization**: Moved the bundle into `.agents/skills/okf-ai-engineering/` and converted `README.md` to `SKILL.md` (added skill `name` and `description`), making the knowledge base a discoverable, distributable skill while keeping it a conformant OKF bundle.
* **Update**: Filled the ASI02–ASI10 threat bodies (enterprise framing + design considerations with cross-links). The vendor/tooling concepts (LangSmith, Langfuse, LangSmith Evals, deepagents, Agent Harness, Programmatic Tools, MCP Gateway) remain scaffolds pending domain input.

## 2026-07-04

* **Initialization**: Created the AI-engineering concept bundle — a cross-linked, vendor-neutral knowledge graph tuned to enterprise AI-platform work (platform + gateway + PII masker).
* **Creation**: Added meta concept [Open Knowledge Format](/context/okf.md).
* **Creation**: Added platform concepts [MCP](/context/mcp.md), [LLM Gateway](/enterprise/llm-gateway.md), and [Agent Architecture](/agents/agent.md).
* **Creation**: Added security concepts [Prompt Injection](/security/risks/agent-goal-hijack.md), [Guardrails](/security/mitigations/guardrails.md), and [PII Masking & Anonymization](/security/mitigations/pii-masking.md).
* **Creation**: Added lifecycle concepts AI Observability & Tracing and Evals & LLM-as-Judge (later removed; observability/evals now live as the vendor-tool concepts).
* **Update**: Switched PDF citations to canonical source URLs (Anthropic, LangChain, OWASP) so the bundle stays pure markdown and portable; local PDFs are no longer bundle dependencies.
* **Creation**: Added a root `SKILL.md` (`type: Overview`) as the knowledge-base landing page.
* **Update**: Restyled every concept body to clearer sections — `In an enterprise platform` and `Design considerations` — replacing the ambiguous "Why it matters" / "Key decisions" headings.

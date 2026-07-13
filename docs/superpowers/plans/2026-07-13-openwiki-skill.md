# OpenWiki Skill and OKF Concept Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a selective, personal-first OpenWiki operator skill and a concise OpenWiki product concept to the AI-engineering OKF bundle.

**Architecture:** The operational skill owns relevance routing, local provenance, CLI workflows, and safety boundaries. The OKF concept owns only durable product knowledge and links OpenWiki to memory, context engineering, and RAG; the generated index and curated log integrate it into the bundle.

**Tech Stack:** Agent Skills Markdown with YAML frontmatter, OpenWiki CLI v0.1.1, OKF v0.1 Markdown, Python 3.11+, PyYAML, markdownlint, pre-commit.

## Global Constraints

- Consult OpenWiki only when it can materially help with cross-project context, history, commitments, provenance, or OpenWiki operations.
- Treat synthesized wiki pages as leads and validate task-critical claims against current primary evidence.
- Never read, display, or copy credential values from `~/.openwiki/.env`.
- Require confirmation before connector deletion, schedule deletion, power-schedule changes, or credential replacement.
- Keep the operational skill in one file and the OKF concept machine-independent.
- Do not alter connectors, schedules, credentials, or existing OpenWiki data while creating these documents.
- Do not commit unless the user explicitly requests a commit.

---

### Task 1: OpenWiki Operator Skill

**Files:**
- Create: `.agents/skills/openwiki/SKILL.md`
- Reference: `docs/superpowers/specs/2026-07-13-openwiki-skill-design.md`

**Interfaces:**
- Consumes: Installed `openwiki` CLI, `~/.openwiki` personal workspace, and standard file/shell tools.
- Produces: A discoverable `openwiki` skill whose frontmatter routes OpenWiki context and administration requests.

- [ ] **Step 1: Load the skill-authoring workflow**

Invoke the `writing-skills` skill and follow its test-first authoring and verification requirements. Do not load or inspect `~/.openwiki/.env`.

- [ ] **Step 2: Record routing scenarios before writing the skill**

Use these scenarios as the behavioral acceptance set:

```text
Invoke: "What have I been working on across my repositories lately?"
Invoke: "Check whether my OpenWiki ingestion ran last night."
Invoke: "Refresh only the OpenWiki source for the agents repository."
Invoke: "Pause my OpenWiki schedule."
Do not invoke: "Fix the failing auth test in this repository."
Do not invoke: "Explain this function from the file currently open."
```

Expected behavior for invoked context requests: inspect only relevant wiki pages, check freshness, and validate important claims through source evidence. Expected behavior for concrete repository tasks: use current repository evidence without adding OpenWiki context.

- [ ] **Step 3: Create the skill**

Create `.agents/skills/openwiki/SKILL.md` with this structure and required content:

```markdown
---
name: openwiki
description: Work with LangChain OpenWiki and Dima's personal OpenWiki CLI workspace. Use when asked about OpenWiki, the personal wiki, cross-project activity, commitments, recurring themes, wiki provenance or freshness, connector ingestion, source configuration, or OpenWiki cron schedules. Also use when broad personal or project-history context may materially help. Do not use for concrete coding or debugging tasks already grounded in current files, Git history, tests, telemetry, or primary documentation.
---

# OpenWiki

OpenWiki is an early-stage CLI that builds agent-facing Markdown wikis. Personal
mode writes under `~/.openwiki/`; code mode writes repository-local docs. Treat
its synthesized pages as contextual leads, not as authority over current source
code or primary evidence.

## Decide whether to use it

Use the personal wiki when the task needs broad context that is not naturally
available from one current repository: cross-project activity, durable themes,
explicit commitments, historical continuity, or provenance. Also use this skill
for OpenWiki ingestion, configuration, authentication, diagnostics, and schedule
management.

Skip the wiki when a concrete coding or debugging task is already grounded in
current files, Git history, tests, telemetry, or primary documentation. Generic
wiki context should not displace stronger evidence or consume context merely
because it exists.

## Understand the data

Personal mode uses this local pipeline:

1. `~/.openwiki/onboarding.json` and
   `~/.openwiki/connectors/<connector>/config.json` define sources and goals.
2. Connectors write deterministic snapshots beneath
   `~/.openwiki/connectors/<connector>/raw/` and run history to `state.json`.
3. Source-specific agent runs synthesize Markdown beneath `~/.openwiki/wiki/`.
4. `~/.openwiki/wiki/.last-update.json` records the latest wiki update.
5. Scheduled macOS runs use user LaunchAgents and write to
   `~/.openwiki/logs/`.

This machine currently uses local Git sources and a 02:00 schedule, but those
details can change. Inspect live non-secret configuration before relying on
them.

## Retrieve context

Read narrowly:

1. Start at `~/.openwiki/wiki/quickstart.md` to identify relevant pages.
2. Read only the relevant project, theme, commitment, or source page.
3. Check `.last-update.json` and the matching connector's `state.json`.
4. For a task-critical claim, inspect the linked source page and latest raw
   manifest, then verify it against the primary repository or service.

Prefer direct Markdown reads because they are cheap and auditable. Use
`openwiki -p "<focused question>"` when the answer requires synthesis across
multiple wiki pages. Stop once the task has enough grounded context.

## Refresh and manage

Prefer the narrowest operation that satisfies the request:

```bash
openwiki ingest <source-instance>
openwiki ingest <connector>
openwiki ingest all
openwiki personal --update
openwiki cron list
openwiki cron pause <source|all>
openwiki cron resume <source|all>
openwiki cron delete <source|all>
openwiki auth <provider>
openwiki auth configure <provider>
openwiki auth tools <provider>
```

Use `openwiki --help` before relying on commands because OpenWiki is new and its
CLI may change.

## Safety

Never read, print, or parse `~/.openwiki/.env`. Configuration files may be read
only when they contain non-secret settings or environment-variable names rather
than credential values.

Obtain confirmation before deleting a connector or schedule, changing macOS
power schedules, or replacing credentials. Authentication may open a browser;
tell the user when interactive action is required.

## Diagnose failures

Establish the failure before changing configuration. Check, in order: command
output, the connector's `state.json`, its latest raw manifest, relevant files in
`~/.openwiki/logs/`, `openwiki cron list`, and macOS LaunchAgent status. Distinguish
connector collection failures from wiki synthesis failures and stale-but-successful
runs.
```

Verify command names against `openwiki --help`; do not add unsupported commands or speculative paths.

- [ ] **Step 4: Validate the skill document**

Run:

```bash
openwiki --help
uv run python -c 'from pathlib import Path; import yaml; text = Path(".agents/skills/openwiki/SKILL.md").read_text(); data = yaml.safe_load(text.split("---", 2)[1]); assert data["name"] == "openwiki" and data["description"]'
uv run pre-commit run trailing-whitespace --files .agents/skills/openwiki/SKILL.md
uv run pre-commit run end-of-file-fixer --files .agents/skills/openwiki/SKILL.md
```

Expected: the help output contains every documented command family; the Python command exits 0; each pre-commit hook reports `Passed`.

- [ ] **Step 5: Review routing quality**

Check the final frontmatter and body against all six scenarios from Step 2. Expected: all four invoke scenarios are directly named by the description, both non-invoke scenarios are excluded, and the body tells an agent when to stop retrieval and return to primary evidence.

### Task 2: OpenWiki OKF Concept

**Files:**
- Create: `.agents/skills/okf-ai-engineering/ai-engineering/context/openwiki.md`
- Modify: `.agents/skills/okf-ai-engineering/ai-engineering/log.md`
- Generate: `.agents/skills/okf-ai-engineering/ai-engineering/index.md`
- Generate: `.agents/skills/okf-ai-engineering/ai-engineering/okf-site.html`

**Interfaces:**
- Consumes: OKF v0.1 conventions and existing `/context/memory.md`, `/context/context-engineering.md`, and `/context/rag.md` concepts.
- Produces: `/context/openwiki.md`, an indexed `Product` concept with bundle-relative cross-links and a dated creation record.

- [ ] **Step 1: Create the concept**

Write `.agents/skills/okf-ai-engineering/ai-engineering/context/openwiki.md`:

```markdown
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

Connectors first write deterministic raw snapshots and manifests locally. OpenWiki
then uses source-specific agent runs to synthesize those artifacts into wiki pages,
preserving a path back to source evidence. Scheduled ingestion can keep the wiki
fresh without placing the full source corpus into every agent context.

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
```

- [ ] **Step 2: Add the OKF log entry**

Under the existing `## 2026-07-13` heading in `.agents/skills/okf-ai-engineering/ai-engineering/log.md`, add:

```markdown
* **Creation**: Added [OpenWiki](/context/openwiki.md), LangChain's early-stage CLI for synthesizing local sources into agent-facing code and personal-memory wikis, with explicit provenance and primary-evidence boundaries.
```

- [ ] **Step 3: Regenerate OKF artifacts**

Run:

```bash
uv run --project . python .agents/skills/okf/scripts/okf_index.py .agents/skills/okf-ai-engineering/ai-engineering
uv run --project . python .agents/skills/okf/scripts/okf_site.py .agents/skills/okf-ai-engineering/ai-engineering
```

Expected: both commands exit 0; `index.md` includes `OpenWiki` under `# context` with type `Product`; the HTML site is regenerated.

- [ ] **Step 4: Validate OKF content**

Run:

```bash
uv run python -c 'from pathlib import Path; import yaml; text = Path(".agents/skills/okf-ai-engineering/ai-engineering/context/openwiki.md").read_text(); data = yaml.safe_load(text.split("---", 2)[1]); assert data["type"] == "Product" and data["resource"] == "https://github.com/langchain-ai/openwiki"'
uv run pre-commit run trailing-whitespace --files .agents/skills/okf-ai-engineering/ai-engineering/context/openwiki.md .agents/skills/okf-ai-engineering/ai-engineering/log.md .agents/skills/okf-ai-engineering/ai-engineering/index.md
uv run pre-commit run end-of-file-fixer --files .agents/skills/okf-ai-engineering/ai-engineering/context/openwiki.md .agents/skills/okf-ai-engineering/ai-engineering/log.md .agents/skills/okf-ai-engineering/ai-engineering/index.md
```

Expected: the Python command exits 0 and every hook reports `Passed`.

### Task 3: Final Verification

**Files:**
- Verify: `.agents/skills/openwiki/SKILL.md`
- Verify: `.agents/skills/okf-ai-engineering/ai-engineering/context/openwiki.md`
- Verify: `.agents/skills/okf-ai-engineering/ai-engineering/index.md`
- Verify: `.agents/skills/okf-ai-engineering/ai-engineering/log.md`
- Verify: `.agents/skills/okf-ai-engineering/ai-engineering/okf-site.html`

**Interfaces:**
- Consumes: Deliverables from Tasks 1 and 2.
- Produces: Evidence that the skill and OKF bundle are internally consistent, secret-free, and repository-clean except for intended changes and pre-existing user work.

- [ ] **Step 1: Scan intended files for credential leakage and placeholders**

Run:

```bash
rg -n 'OPENAI_.*TOKEN|API_KEY=|REFRESH_TOKEN=|CLIENT_SECRET=' .agents/skills/openwiki/SKILL.md .agents/skills/okf-ai-engineering/ai-engineering/context/openwiki.md
```

Expected: no output and exit status 1.

- [ ] **Step 2: Verify generated and authored diffs**

Run:

```bash
git diff --check
```

Expected: `git diff --check` exits 0. Status includes the skill, concept, regenerated OKF artifacts, design, and plan, while preserving the pre-existing `.vscode/tasks.json` modification untouched.

- [ ] **Step 3: Run repository verification**

Run:

```bash
uv run pre-commit run --all-files
uv run pytest --ignore=tests/integration
```

Expected: all pre-commit hooks pass and pytest reports all tests passed. If pre-commit modifies generated artifacts, inspect those changes and rerun until clean.

- [ ] **Step 4: Perform final skill review**

Confirm all of the following manually:

```text
- The skill explains what OpenWiki is and distinguishes personal from code mode.
- The skill explains source config, raw connector data, synthesis, freshness, and schedules.
- The relevance gate avoids generic context pollution on concrete tasks.
- Full management commands are documented with narrow-refresh preference.
- Destructive and credential-changing actions require confirmation.
- No text tells an agent to inspect ~/.openwiki/.env.
- The OKF concept remains concise, portable, and cross-linked.
- No unrelated existing work was modified.
```

Expected: every item is true before reporting completion.

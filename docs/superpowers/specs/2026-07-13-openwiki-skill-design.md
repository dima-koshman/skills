# OpenWiki Skill and OKF Concept Design

## Goal

Add a personal-first but portable agent skill for LangChain OpenWiki, plus a small
OpenWiki concept in the AI-engineering OKF bundle. The skill should help agents
decide whether OpenWiki can materially improve a task, understand where its
claims came from, and operate the local CLI without treating generic synthesized
context as authoritative.

## Scope

Create:

- `.agents/skills/openwiki/SKILL.md`
- `.agents/skills/okf-ai-engineering/ai-engineering/context/openwiki.md`

Update generated or curated OKF artifacts:

- `.agents/skills/okf-ai-engineering/ai-engineering/index.md`
- `.agents/skills/okf-ai-engineering/ai-engineering/log.md`

The OpenWiki skill should remain a single file unless verification demonstrates
that a separate reference is necessary. The OKF concept stays conceptual and
machine-independent; host-specific operational guidance belongs in the skill.

## Skill Routing

The skill triggers for OpenWiki itself, personal-wiki context, cross-project
activity, commitments, recurring themes, connector ingestion, source provenance,
and OpenWiki schedule management.

Before reading the wiki, the agent applies a relevance gate:

- Use OpenWiki for cross-project context, historical themes, explicit
  commitments, provenance, broad "what changed" questions, and OpenWiki
  operations.
- Skip OpenWiki for concrete coding or debugging tasks when current files, Git
  history, tests, telemetry, or primary documentation answer the question.
- Treat synthesized wiki pages as leads, not authority. Validate task-critical
  claims against source pages, raw manifests, and ultimately the primary source.
- Check wiki and connector freshness before relying on time-sensitive claims.

This makes the skill selective by default while preserving full management
capability when OpenWiki is relevant.

## Data Model and Provenance

The skill explains OpenWiki's local pipeline:

1. `~/.openwiki/onboarding.json` and connector configuration define source
   instances, ingestion goals, and schedules.
2. Deterministic connector runs write local snapshots and manifests beneath
   `~/.openwiki/connectors/<connector>/raw/`.
3. Source-specific agent runs synthesize those snapshots into Markdown beneath
   `~/.openwiki/wiki/`.
4. `~/.openwiki/wiki/.last-update.json` and connector `state.json` files expose
   freshness and run status.
5. On macOS, scheduled ingestion uses user LaunchAgents and writes logs beneath
   `~/.openwiki/logs/`.

The current installation is an example, not a hard-coded invariant: it uses
personal mode, local Git repository sources, and a 02:00 ingestion schedule.
Agents must inspect live configuration because sources and schedules can change.

## Operating Workflow

The skill presents a compact decision-oriented workflow:

1. Inspect `wiki/quickstart.md`, then only the relevant synthesized page.
2. Check `.last-update.json` and the corresponding connector state.
3. Follow the wiki's source link and inspect the latest raw manifest when a
   claim matters to the task.
4. Use `openwiki -p "<focused question>"` only when synthesis across pages is
   useful; prefer direct Markdown reads for cheaper, auditable retrieval.
5. Refresh the narrowest relevant source instance with `openwiki ingest
   <source-instance>`; use personal update or `ingest all` only when broader
   maintenance is intended.
6. Use the installed CLI's cron and authentication/configuration commands for
   management and diagnostics.

Non-destructive management may be performed when useful. Connector deletion,
schedule deletion, power-schedule changes, and credential replacement require
user confirmation. Agents must never display or parse `~/.openwiki/.env`; they
should inspect non-secret config that references environment-variable names.

For failures, inspect CLI output, connector `state.json`, latest raw manifests,
`~/.openwiki/logs/`, and LaunchAgent status before changing configuration.

## OKF Concept

Add `context/openwiki.md` with `type: Product`, a one-sentence description, and
the GitHub repository as its canonical resource. Keep it concise and cover:

- OpenWiki as an early-stage LangChain CLI that generates and maintains
  agent-facing Markdown wikis.
- Repository-local code mode and the `~/.openwiki/wiki` personal mode.
- The provenance chain from configured connectors through raw snapshots to
  synthesized pages.
- Its practical role in broad context, trends, and continuity, together with
  the limitation that current primary evidence is preferable for concrete work.
- Its relationship to Memory, Context Engineering, and RAG.

Regenerate the bundle index with the OKF index script and add a newest-first
creation entry to the bundle log.

## Verification

Verify the implementation with:

- Frontmatter and trigger review against neighboring `.agents` skills.
- Command review against the installed `openwiki --help` output.
- A secret scan confirming no credential values or `.env` contents were copied.
- Checks that provenance, freshness, and authority boundaries are explicit.
- Scenario tests demonstrating intended invocation for cross-project context and
  OpenWiki operations, and non-invocation for a concrete repository task.
- OKF index regeneration, link validation where available, Markdown linting, and
  inspection of the generated diff and log entry.

## Non-Goals

- Automatically consulting OpenWiki at the start of every task.
- Treating synthesized wiki pages as a substitute for source code or primary
  evidence.
- Adding new connectors, changing the existing schedule, or altering current
  OpenWiki data as part of creating the skill.
- Duplicating personal machine administration details in the OKF concept.

## Validation Record

Baseline scenario runs without the skill handled evidence cautiously but guessed
unsupported `source`, `schedule`, `run`, and `status` commands for OpenWiki
operations. The concrete debugging counterexample correctly preferred tests and
current repository evidence over generic wiki context.

After adding the skill, fresh-agent scenarios passed cross-project retrieval,
OpenWiki operations, and concrete-task routing. Refactoring qualified the
OpenWiki-authentication trigger, bounded unscoped "lately" requests, documented
v0.1.1's global-only cron mutation behavior, and clarified that a source-instance
ingestion already performs its corresponding wiki update.

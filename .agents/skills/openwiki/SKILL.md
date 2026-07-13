---
name: openwiki
description: Use when a task mentions OpenWiki, the personal wiki, cross-project activity, commitments, recurring themes, wiki provenance or freshness, connector ingestion, source configuration, OpenWiki authentication, or OpenWiki cron schedules; also use when broad personal or project-history context may materially help. Do not use for concrete coding or debugging tasks already grounded in current files, Git history, tests, telemetry, or primary documentation.
---

# OpenWiki

OpenWiki is an early-stage LangChain CLI that builds agent-facing Markdown wikis.
Personal mode writes under `~/.openwiki/`; code mode writes repository-local docs.

**Core principle:** use the personal wiki as a selective map to context and
evidence, not as authority over current primary sources.

## Decide whether to use it

Use OpenWiki for cross-project activity, historical continuity, recurring themes,
explicit commitments, broad "what changed" questions, provenance, and OpenWiki
operations. Skip it when current repository files, Git history, tests, telemetry,
or primary documentation already ground a concrete task.

If the user explicitly requests wiki context during a concrete task, inspect it
narrowly after reproducing or locating the primary evidence. Stop when it does not
improve a concrete hypothesis.

## Understand the data

Personal mode uses this local pipeline:

1. `~/.openwiki/onboarding.json` defines source instances, ingestion goals, and
   saved schedules; `connectors/<connector>/config.json` holds current connector
   configuration.
2. Connectors write deterministic snapshots beneath
   `connectors/<connector>/raw/` and run history to `state.json`.
3. Source-specific agent runs synthesize Markdown beneath `wiki/`.
4. `wiki/.last-update.json` records the latest wiki update.
5. On macOS, scheduled runs use user LaunchAgents and write to `logs/`.

This machine currently uses local Git sources and a 02:00 schedule, but live
configuration can change or diverge. Inspect both onboarding source instances and
connector config; identify an instance by its ID and repository path, not its
display name alone.

## Retrieve grounded context

1. Read `wiki/quickstart.md`, then only the relevant project, theme, commitment,
   question, or source page.
2. Check `wiki/.last-update.json` and the matching connector's `state.json`.
3. For a consequential claim, follow its source page to the latest raw manifest.
4. Validate task-critical claims against the primary repository or service.

Prefer direct Markdown reads because they are cheap and auditable. Use
`openwiki -p "<focused question>"` only when synthesis across pages is useful.
Generated prose without retrievable evidence is low-confidence context.

For an unscoped "lately" request, default to the latest connector snapshot and
30 days of primary history. Read at most five relevant wiki pages, validate the
three most consequential claims, and report stale data rather than refreshing it
unless the user requested a refresh.

## Quick reference

| Intent | Command |
|---|---|
| Inspect the installed interface | `openwiki --help` |
| Query across the personal wiki | `openwiki -p "<focused question>"` |
| Refresh one source instance | `openwiki ingest <source-instance>` |
| Refresh every instance of a connector | `openwiki ingest <connector>` |
| Refresh all configured sources | `openwiki ingest all` |
| Update the personal wiki | `openwiki personal --update` |
| Inspect schedules | `openwiki cron list` |
| Pause or resume the installed schedule | `openwiki cron pause all` / `openwiki cron resume all` |
| Delete the installed schedule | `openwiki cron delete all` |
| Authenticate or inspect provider tools | `openwiki auth <provider>` / `openwiki auth configure <provider>` / `openwiki auth tools <provider>` |

Prefer the narrowest refresh. OpenWiki is new, so verify commands with
`openwiki --help` rather than inventing likely `source`, `schedule`, `run`, or
`status` subcommands.

Although v0.1.1 help accepts a source target for `cron`, its current scheduler is
global and skips targets other than `all`. Check command output and rerun
`openwiki cron list`; do not report a mutation from the exit code alone.

An `ingest` run includes the corresponding wiki update. After a source-instance
refresh, do not add `personal --update` unless a broader refresh is intended.

## Manage safely

Non-destructive inspection, a uniquely identified requested refresh, and
`cron list` need no extra confirmation. Confirm before deleting connector data or
schedules, changing macOS power schedules, directly editing OpenWiki state, or
replacing credentials. Authentication may require interactive browser action.

OpenWiki v0.1.1 has no general `cron create` or `cron update` command. Resume a
paused schedule with `openwiki cron resume all`; if repair requires changing timing or
recreating launchd state, diagnose and report the exact defect, then confirm
before rerunning interactive setup or editing system configuration.

Never read, print, or parse `~/.openwiki/.env`. Non-secret config may be read when
it contains settings or environment-variable names rather than credential values.

## Diagnose failures

Check command output, connector `state.json`, its latest raw manifest, relevant
files in `logs/`, `openwiki cron list`, the LaunchAgent path recorded in
`onboarding.json`, and `launchctl` status before changing configuration. Distinguish
connector collection failures from synthesis failures and stale-but-successful
runs.

## Common mistakes

| Mistake | Better action |
|---|---|
| Reading the whole wiki for a focused task | Start from `quickstart.md` and follow one relevant path. |
| Repeating a summary as fact | Check freshness, raw evidence, and the primary source. |
| Refreshing every source by default | Resolve and ingest one source-instance ID. |
| Guessing familiar CLI nouns | Read `openwiki --help` and use `ingest` or `cron`. |
| Dumping config to find credentials | Inspect non-secret metadata; never open `.env`. |

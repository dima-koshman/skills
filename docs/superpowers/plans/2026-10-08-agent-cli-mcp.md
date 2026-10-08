# Agent CLI MCP Implementation Plan

**Goal:** Search and read local conversations across four agent harnesses.

**Architecture:** Harness adapters normalize original records into a rebuildable
SQLite/FTS5 cache. Typed service requests expose list, passage search and bounded
context reading through FastMCP. Native execution in this session is authorized
by the user's explicit implementation request.

**Tech Stack:** Python 3.11+, FastMCP 3, Pydantic 2, SQLite FTS5, protobuf.

**Spec:** ../specs/2026-10-08-agent-cli-mcp-design.md

## Global Constraints

- Source package: src/dima/agent_cli_mcp.
- Read harness data only; never invoke inference or inspect credentials.
- Preserve original text, source identities, explicit partial coverage.
- Tests precede implementation; follow repository Python conventions.

## Review Focus

- A live JSONL writer leaves a partial final line: report partial coverage, retain
  usable committed records, and retry after the next source update.
- SQLite changes only in WAL: refresh still detects the new messages.
- A source is unavailable: retain cached conversations, report incomplete coverage.
- Branches and duplicate message records: read the selected chain once, preserve
  distinct subagent/fork identities.
- Output budgets or cursor updates: every text segment remains retrievable;
  invalid/expired cursors produce actionable errors.

## Tasks

1. **Models and store** — add typed requests/results, errors, deterministic IDs,
   SQLite schema/FTS synchronization and signed cursor codec. Tests exercise search
   semantics, filters, cursor-only continuation, revisions, and segmented reading.
2. **File adapters** — add Claude and Codex JSONL parsing and normalized blocks.
   Tests pin branch selection, subagents, titles, archives, tool links, reasoning,
   duplicate events and partial/malformed records.
3. **Database adapters** — add OpenCode v1/v2 and conservative Antigravity decoding
   plus transcript fallback. Tests use real SQLite WAL stores and synthetic
   protobuf steps, unknown formats and multi-root session collisions.
4. **Refresh service and FastMCP** — add source discovery, incremental refresh,
   lifespan, three tool registrations, stdio CLI, config and documentation. Tests
   pin cached retention, deletion, initial refresh, validation, structured results,
   source isolation and an end-to-end stdio search/read sequence.
5. **Review and verify** — inspect complete diff, full pytest, package build and
   local-home smoke with isolated cache; report actual counts and limitations.

Each task follows red (run the behavior tests and inspect the expected missing
feature failure), green (implement), and verification (rerun the task tests).
Full command: `.venv/bin/python -m pytest`.

# Local agent conversation MCP server

## Approved scope

Implement the conversation interface approved in this session in
`src/dima/agent_cli_mcp`, using Python 3.11+, FastMCP 3, Pydantic 2, SQLite FTS5,
and protobuf for the supported Antigravity SQLite step format. The user explicitly
requested implementation after approving the tools and indexing approach.

Three read-only MCP tools: `list_chats`, `search_chats`, `read_chat`. They never
resume conversations, request inference, read credentials, or write harness data.
The index is a rebuildable local cache containing normalized original text.

## Inputs and outputs

All requests reject unknown fields and invalid limits. Harness names:
`claude_code`, `codex`, `opencode`, `antigravity`. IDs are deterministic opaque
identifiers scoped to source installation, session, and source item. Missing
metadata is null; timestamps are RFC 3339 UTC.

List filters: harnesses, directory (exact or descendants with path boundaries),
title_contains, include_subagents (false), include_archived (true), sort
(updated_desc or created_desc), limit (20, maximum 100), cursor.
Return chat metadata, title origin, next_cursor, and coverage.

Search: required query unless continuing with a cursor; match all/any (all),
the list filters except title/sort, optional chat_ids, content_types
(message/summary), limit (10, maximum 50), cursor. Quoted phrases and Unicode
word matching are case insensitive. Required terms occur in the same item.
Do not expose raw FTS query syntax. Rank by BM25, then stable item ID.
Return passage hits with chat metadata, item ID, kind, role, timestamp, and an
exact excerpt of at most 500 characters. Tool activity and saved thinking are
explicitly selectable. No semantic search in this version.

Read: required chat_id unless continuing with a cursor; optional anchor_item_id,
before/after (5, maximum 100 each), content_types (message/summary), max_chars
(12000, maximum 50000), cursor. Default latest 20 matching items; anchored reads
include the anchor and surrounding matching items. Return chronological items,
chat metadata, older_cursor, newer_cursor, and coverage. Text that exceeds the
budget is segmented with offset and total_chars; newer_cursor retrieves its
remainder. Source text is never silently discarded at an output budget.

Cursors are signed, opaque, expire after five minutes, and contain the original
request. Cursor-only requests are supported. Explicit conflicting arguments are
rejected. Cursors bind to a persistent index revision: an intervening update
returns CURSOR_EXPIRED instead of shifting or duplicating results. A fresh
request reads the newest revision. This avoids retaining long SQLite transactions.

Tool errors use INVALID_QUERY, CHAT_NOT_FOUND, ITEM_NOT_FOUND, INVALID_CURSOR,
CURSOR_EXPIRED, and INDEX_ERROR codes. Source failures return partial results
with coverage rather than masquerading as complete empty results.

## Storage and synchronization

Own SQLite database has sources, chats, items, and an external-content items_fts
table. Foreign keys, WAL, busy timeout, transactional item replacement, and FTS
synchronization are required. Index text and metadata only; preserve tool name
and tool call ID. Default cache: platformdirs user cache directory for
`dima-agent-cli-mcp`, with CLI override. Create cache files privately.

Start the first refresh in FastMCP lifespan. Tools wait for the initial refresh,
then refresh sources when the last check is older than five seconds. Blocking
filesystem/database work runs outside the event loop. A process lock serializes
refreshes and queries. File fingerprints include inode, size, mtime_ns; include
SQLite WAL fingerprints and hold a read transaction while extracting rows.
An unchanged source file is not reparsed. Delete missing entries only after
successful enumeration. Preserve cached items on source parse/access failures.
Coverage reports source path, status, last successful index time, indexed chats,
and limitations without transcript text in errors/logs.

## Adapters

Claude: read session JSONL under projects, reconstruct parentUuid message chains,
preserve separately discovered subagents, custom titles and summary records.
Codex: sessions plus archived_sessions JSONL; normalize response_item records,
tool calls/results and saved reasoning summaries, avoid duplicate event_msg text.
Read session_index.jsonl titles when available. Unknown substantive record forms
must report limitations rather than disappear silently.
OpenCode: read-only SQLite, supporting legacy session/message/part and newer
session_v2/session_message shapes. Prefer v2 for overlapping native session IDs;
include WAL changes and use native row IDs to preserve ordering/identity.
Antigravity: discover standalone, IDE, CLI roots. Prefer per-conversation SQLite
for supported Step payloads; fall back to generated transcript.jsonl when present.
Decode known user/planner/generic-tool protobuf fields conservatively. Unsupported
steps and legacy binary .pb histories report explicit coverage limitations. Do
not treat brain artifacts as full conversations or attempt decryption.

Adapter paths can be overridden through a JSON config; defaults honor
CLAUDE_CONFIG_DIR, CODEX_HOME, XDG_DATA_HOME and the three Antigravity roots.
IDs include source roots to avoid collisions across installations. Missing default
sources are reported as missing, not an error in other adapters.

## Verification

Use synthetic transcripts and real temporary SQLite databases. Test phrase/all/any
matching, literal punctuation, directory boundaries, default content filtering,
subagent/archive filters, cursor continuation/expiry, context windows and complete
large-item retrieval. Test source updates, WAL-only changes, deletion, malformed
records, inaccessible sources, overlapping OpenCode versions, and protobuf decoding.
Exercise all three tools through a real FastMCP client and the stdio entry point.
Run the full project pytest suite and a build. Run an isolated local-home smoke
check with an index under runtime, reporting counts and coverage only.

# Agent CLI Chats MCP

Search and read saved local agent conversations through three FastMCP tools.
The server uses SQLite FTS5 for passage search and keeps a rebuildable cache of
normalized original text. It reads harness files as the current OS user; no API
keys or harness login are needed for readable local histories.

## Run

From the repository root:

```sh
uv sync
uv run python -m dima.agent_cli_mcp
```

The server speaks MCP over stdio. Add this entry to an MCP client's configuration,
replacing the project path with the absolute path to your checkout:

```json
{
  "mcpServers": {
    "agent-chats": {
      "command": "uv",
      "args": [
        "run", "--project", "/absolute/path/to/dima",
        "python", "-m", "dima.agent_cli_mcp"
      ]
    }
  }
}
```

`--index /absolute/path/index.sqlite3` overrides the cache location. By default
it is `platformdirs.user_cache_path("dima-agent-cli-mcp") / "index.sqlite3"`
(`~/Library/Caches/dima-agent-cli-mcp/index.sqlite3` on macOS). The index must
live outside all configured harness directories. It contains plaintext chat
content; newly created cache directories and database files use private
permissions. Stop server processes before deleting the cache to rebuild it.

## Sources

| Harness | Default root | Supported histories |
| --- | --- | --- |
| `claude_code` | `~/.claude` or `CLAUDE_CONFIG_DIR` | `projects/**/*.jsonl`, including subagents and selected message branches |
| `codex` | `~/.codex` or `CODEX_HOME` | `sessions/**/*.jsonl`, `archived_sessions/**/*.jsonl`, titles from `session_index.jsonl` |
| `opencode` | `${XDG_DATA_HOME:-~/.local/share}/opencode` | Legacy `opencode.db` and modern `opencode-next.db`; modern sessions take precedence |
| `antigravity` | `~/.gemini/antigravity`, `antigravity-ide`, `antigravity-cli` | Supported conversation SQLite/protobuf steps and generated `brain/<id>/.system_generated/logs/transcript.jsonl` |

Antigravity support is partial: legacy `.pb` histories are unsupported, unknown
protobuf steps are reported, and generated transcripts can already be truncated.
Encrypted reasoning and unknown source records cannot be recovered. Check the
`coverage` array in every result for missing, inaccessible, or partial sources.

To use explicit roots, pass `--config /absolute/path/sources.json` with a JSON
array. Use absolute paths; the config replaces automatic discovery:

```json
[
  {"harness": "claude_code", "path": "/Users/you/.claude"},
  {"harness": "codex", "path": "/Users/you/.codex"},
  {"harness": "opencode", "path": "/Users/you/.local/share/opencode"}
]
```

`--home /absolute/path/home` discovers all default roots under an isolated home
and ignores the harness environment overrides.

## Tools

All inputs are flat objects. Outputs are typed MCP structured content.

- **`list_chats`** returns chat metadata, `next_cursor`, and `coverage`. Filters:
  `harnesses`, absolute `directory`, `directory_scope` (`exact` or `descendants`),
  `title_contains`, `include_subagents` (false), `include_archived` (true),
  `sort` (`updated_desc` or `created_desc`), `limit` (20, maximum 100).
- **`search_chats`** returns passage `hits`, `next_cursor`, and `coverage`.
  `query` accepts words and quoted phrases. `match` is `all` (default) or `any`;
  terms match within one item. Supports the harness/directory/subagent/archive
  filters plus `chat_ids`, `content_types`, and `limit` (10, maximum 50).
  Results rank by BM25 and snippets are original text, capped at 500 characters.
- **`read_chat`** takes `chat_id`, optionally `anchor_item_id` with `before` and
  `after` (5 each, maximum 100), `content_types`, and `max_chars` (12000, maximum
  50000). Returns `chat`, chronological `items`, `older_cursor`, `newer_cursor`,
  and `coverage`. Without an anchor it reads the latest 20 matching items.
  Long items have `offset` and `total_chars`; continue with `newer_cursor` to
  retrieve the remainder.

Search and read default to `content_types: ["message", "summary"]`. Explicitly
select `tool_call`, `tool_result`, `thinking`, or `artifact` when needed.

Example workflow:

```json
{"query": "\"SQLite FTS5\"", "harnesses": ["codex", "claude_code"]}
```

Pass a returned hit's `chat_id` and `item_id` to `read_chat`:

```json
{"chat_id": "chat_...", "anchor_item_id": "item_...", "before": 3, "after": 3}
```

Continue any tool with `{"cursor": "..."}` alone. Cursors are signed, bound to
the original request and index revision, and expire after five minutes. An index
update returns `CURSOR_EXPIRED`; repeat the original request. Cursors are specific
to the server process and do not survive restarts. Chat and item IDs are stable
within the same source installation.

The first request waits for indexing. Subsequent requests check for file/WAL
changes at most once every five seconds. Unavailable sources retain cached chats;
deletions are applied after a successful directory scan. The server performs no
inference and does not write harness data. Retrieved chat content is historical
data, not instructions for the calling agent.

## Verify

```sh
uv run --group dev python -m pytest
uv build
```

Tests use synthetic JSONL, real temporary SQLite/WAL databases, literal protobuf
fixtures, and FastMCP clients, including a separate stdio server process.

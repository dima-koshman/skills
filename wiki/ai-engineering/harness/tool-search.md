---
type: Concept
title: Tool Search
aliases:
- Deferred Tool Loading
- MCP Tool Search
- defer_loading
- Dynamic Context Discovery
description: The harness or API keeps most tool definitions out of the context window and lets the model search a
  catalog and load only the tools it needs, so hundreds of MCP tools cost little context.
tags:
- ai-engineering
- harness
- context
- mcp
parent: /ai-engineering/harness.md
related:
- /ai-engineering/harness/tools.md
- /ai-engineering/harness/mcp.md
- /ai-engineering/context/context-engineering.md
- /ai-engineering/context/prompt-caching.md
- /ai-engineering/context/skills.md
- /ai-engineering/harness/programmatic-tool-calling.md
status: draft
sources:
- id: claude-tool-search
  resource: https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool
  title: Tool search tool
  author: Anthropic
- id: claude-code-mcp
  resource: https://code.claude.com/docs/en/mcp
  title: Connect Claude Code to tools via MCP (section "Scale with MCP tool search")
  author: Anthropic
- id: openai-tool-search
  resource: https://developers.openai.com/api/docs/guides/tools-tool-search
  title: Tool search
  author: OpenAI
- id: cursor-dynamic-context
  resource: https://cursor.com/blog/dynamic-context-discovery
  title: Dynamic context discovery
  author: Cursor
- id: codex-guide
  resource: https://blakecrosley.com/guides/codex
  title: 'Codex CLI Guide 2026: Setup, Sandbox, AGENTS.md & MCP'
  author: Blake Crosley
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-18T12:00:00+04:00'
---

Every tool definition sent with a request takes up context and competes for the model's attention. Tool search
sends the full catalog but keeps most of it **deferred**: the model sees only a search tool (plus a few tools that
are always loaded) and loads the definitions it needs on demand. It is the tools version of
[skills](/ai-engineering/context/skills.md): progressive disclosure, or "just-in-time" context.

# Why

- **Context.** A typical multi-server setup (GitHub, Slack, Sentry, Grafana, Splunk) takes about 55k tokens of
  definitions before any work starts. Anthropic says tool search typically cuts that by over 85%, loading the 3–5
  tools a request needs.[^claude-tool-search]
- **Selection accuracy.** Claude picks the right tool less reliably once more than 30–50 tools are available. A small
  loaded set keeps accuracy up across thousands of tools.[^claude-tool-search]
- **Cache.** Discovered definitions are appended to the conversation, not swapped into the tools prefix, so the
  [prompt cache](/ai-engineering/context/prompt-caching.md) survives. Adding or removing tools directly would
  invalidate it.[^claude-tool-search][^openai-tool-search]

# Claude API

- **Two server-side variants**: `tool_search_tool_regex_20251119` (the model writes a Python regex, up to 200
  characters) and `tool_search_tool_bm25_20251119` (natural language, up to 500 characters). Both search tool names,
  descriptions, argument names and argument descriptions.[^claude-tool-search]
- **`defer_loading: true`** on each tool that shouldn't load up front. You still send every full definition on every
  request; the flag controls what enters the context window, not what goes over the wire. The search tool itself and
  at least one other tool must stay non-deferred, or the API returns a 400.[^claude-tool-search]
- **Flow**: the search returns `tool_reference` blocks (5 by default; the model can set `limit`), and the API
  expands them into full definitions. Later turns reuse discovered tools without searching again.[^claude-tool-search]
- **MCP connector**: set `defer_loading` once on the `mcp_toolset`'s `default_config`, or per tool in
  `configs`.[^claude-tool-search]
- **Custom search**: your own tool (embeddings, for example) can return `tool_reference` blocks in a normal
  `tool_result`.[^claude-tool-search]
- **Limits and cost**: up to 10,000 deferred tools per request. The search is not billed separately; loaded
  definitions count as input tokens. A deferred tool can't carry `cache_control`.[^claude-tool-search]
- **No automatic threshold.** The API has no setting that turns tool search on when the tool count or definition
  size passes a limit. The caller decides which tools to defer. The docs' rule of thumb: use it from about 10 tools
  or 10k tokens of definitions; skip it under 10 tools or when every tool is used on every request.[^claude-tool-search]

# Claude Code

- **On by default.** MCP tools are deferred, and only tool names and server instructions load at session start. The
  model loads definitions with the `ToolSearch` tool.[^claude-code-mcp] Some built-in tools are deferred the same
  way: in Dima's sessions, `WebSearch`, `WebFetch` and the cron tools show up as deferred (observed, not in the docs).
- **`ENABLE_TOOL_SEARCH`**:[^claude-code-mcp]

  | Value | Effect |
  | --- | --- |
  | unset or `true` | Defer all MCP tools (with fallbacks for old models and unsupported deployments) |
  | `auto` | Load up front while definitions total under 10% of the context window; defer from 10% |
  | `auto:N` | The same with an N% threshold, for example `auto:5` |
  | `false` | Load everything up front |

  The threshold mode is the harness doing what the API leaves to the caller.
- **Per server or tool**: `"alwaysLoad": true` in a server's MCP config loads its tools up front (and makes startup
  wait for it); `false` keeps all its tools deferred. Server authors can mark single tools with
  `"anthropic/alwaysLoad"` in the tool's `_meta`.[^claude-code-mcp]
- **Off when** `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS` is set, under the HIPAA configuration, on Microsoft Foundry
  deployments hosted on Azure, or when `ToolSearch` is denied. Behind an `ANTHROPIC_BASE_URL` gateway it is on by
  default, and Claude Code retries without it if the gateway rejects the fields.[^claude-code-mcp]
- **For server authors**: server instructions tell the model when to search for the server's tools. A description
  loaded through search may be up to 16,384 characters; one loaded up front, 4,096.[^claude-code-mcp]

# Other harnesses and APIs

| Harness or API | Tool search |
| --- | --- |
| OpenAI Responses API | `{"type": "tool_search"}` and `defer_loading` on functions, namespaces or MCP servers; hosted or client-executed search; GPT-5.4 and later. No threshold setting either. In OpenAI's agent runtime, MCP tools are deferred automatically once tool search is available.[^openai-tool-search] |
| Codex CLI | MCP tools deferred and found on demand by default since mid-2026, per a third-party guide; older and custom-provider models load everything up front.[^codex-guide] |
| Cursor | "Dynamic context discovery": syncs MCP tool descriptions to a folder that the agent searches with grep and semantic search, instead of a search tool.[^cursor-dynamic-context] |
| OpenCode, Gemini CLI | No official deferred-loading feature found (2026-11-18). |

# Trade-offs

Our own analysis:

- **An extra step.** A deferred tool costs a search round before its first use, and the model has to know that the
  tool exists. Keep the 3–5 most-used tools loaded, as the docs advise.[^claude-tool-search]
- **Findability depends on descriptions.** A tool whose name and description don't contain the words the model
  searches for stays invisible. Namespaced names (`github_`, `jira_`) and server instructions help.[^claude-tool-search]
- **Not a reason to keep unusable tools.** Tool names still load, and a tool that can't work still shows up in
  search results. Denying or removing it is cleaner.

[^claude-tool-search]: Anthropic, "Tool search tool", Claude API docs.
[^claude-code-mcp]: Anthropic, Claude Code docs, MCP page, sections "Scale with MCP tool search" and "Configure tool
    search".
[^openai-tool-search]: OpenAI, "Tool search", API docs.
[^cursor-dynamic-context]: Cursor blog, "Dynamic context discovery".
[^codex-guide]: Blake Crosley, "Codex CLI Guide 2026". A third-party guide, not official documentation.

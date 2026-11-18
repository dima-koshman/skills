---
type: Practice
title: Tool Result Offloading
description: Store a large tool result outside the context window and keep only a path and preview, so the model can fetch the rest when it needs it.
tags:
- ai-engineering
- context
parent: /ai-engineering/context.md
related:
- /ai-engineering/context/context-engineering.md
- /ai-engineering/context/prompt-caching.md
- /ai-engineering/harness/tools.md
- /ai-engineering/harness.md
- /ai-engineering/harness/llm-browser-use.md
sources:
- id: chase-late-2026
  resource: https://www.langchain.com/blog/context-engineering-challenges-late-2026
  title: New context engineering challenges in late 2026
  author: Harrison Chase
  last_modified: '2026-11-02'
- id: deepagents-context-management
  resource: https://www.langchain.com/blog/context-management-for-deepagents
  title: Context Management for Deep Agents
  author: Chester Curme and Mason Daugherty
  last_modified: '2026-01-28'
- id: deepagents-remember
  resource: https://www.langchain.com/blog/context-engineering-deep-agents-remember
  title: 'Context Engineering: How Deep Agents Remember'
  author: Jess Weng
  last_modified: '2026-10-14'
- id: deepagents-context-docs
  resource: https://docs.langchain.com/oss/python/deepagents/context-engineering
  title: Context engineering in Deep Agents
  author: LangChain
- id: deepagents-backends
  resource: https://docs.langchain.com/oss/python/deepagents/backends
  title: Deep Agents backends
  author: LangChain
- id: claude-code-mcp
  resource: https://code.claude.com/docs/en/mcp
  title: Connect Claude Code to tools via MCP
  author: Anthropic
- id: claude-context-editing
  resource: https://platform.claude.com/docs/en/build-with-claude/context-editing
  title: Context editing
  author: Anthropic
- id: anthropic-context-engineering
  resource: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
  title: Effective context engineering for AI agents
  author: Anthropic
  last_modified: '2025-09-29'
- id: manus-context-engineering
  resource: https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus
  title: 'Context Engineering for AI Agents: Lessons from Building Manus'
  author: Yichao Ji
  last_modified: '2025-07-18'
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-04T10:40:00+04:00'
stale_after: '2027-05-04T00:00:00+04:00'
---

One large tool result can fill much of the context window, then stay there and get resent on every turn. Offloading writes the full result to storage outside the context and leaves a pointer and a short preview. The agent reads more only if it needs it. Harrison Chase lists it among the "standard-ish" solutions in [context engineering](/ai-engineering/context/context-engineering.md) as of late 2026.[^chase-late-2026]

The idea is older than the name. Anthropic's advice is to keep lightweight identifiers, such as file paths or stored queries, and load the data at runtime.[^anthropic-context-engineering] Manus calls the same thing restorable compression: a web page can leave the context as long as its URL stays.[^manus-context-engineering]

# How harnesses do it

| Harness | Trigger | Stored in | Left in context | Reading it back |
| --- | --- | --- | --- | --- |
| [Deep Agents](/ai-engineering/harness.md#deep-agents) | Result over about 20,000 tokens, user message over 50,000[^deepagents-remember] | Configured backend, under `/large_tool_results/{tool_call_id}`[^deepagents-remember] | Path and preview[^deepagents-context-docs] | Pages with `read_file`, or searches[^deepagents-remember][^deepagents-context-management] |
| [Claude Code](/ai-engineering/harness.md#claude-code) | MCP text result over 50,000 characters[^claude-code-mcp] | A file[^claude-code-mcp] | A note with the file path[^claude-code-mcp] | Reads the file when needed[^claude-code-mcp] |
| Manus | No threshold given | Sandbox file system[^manus-context-engineering] | URL or path[^manus-context-engineering] | Reads files on demand[^manus-context-engineering] |

Deep Agents sources disagree on the preview: the docs say the first 10 lines, and the October 2026 blog says the first and last few lines.[^deepagents-context-docs][^deepagents-remember]

# Storage

The store only has to survive as long as the agent may need the data, and it doesn't have to be a real disk. Deep Agents shows the range, because it exposes every backend through the same file tools:[^deepagents-backends]

| Backend | Where data lives | Lifetime |
| --- | --- | --- |
| `StateBackend` (default) | LangGraph agent state | The thread, through checkpoints |
| `FilesystemBackend` | Real files under `root_dir` | Until deleted |
| `StoreBackend` | LangGraph `BaseStore`, such as `InMemoryStore` for local development | Across threads, depending on the store |

Offloaded results go to the default backend, and the docs recommend `StateBackend` there to keep them ephemeral.[^deepagents-backends]

# Compared with other techniques

| Technique | What stays in context | Can the model get it back? |
| --- | --- | --- |
| Offloading | Path and preview | Yes, with file tools |
| Truncation | The kept part | No |
| Tool result clearing | Placeholder text[^claude-context-editing] | Only if it saved the data to memory first[^claude-context-editing] |
| Summarization or compaction | A summary | Only if the harness stores the original, as Deep Agents does[^deepagents-context-management] |

LangChain's rule is "Large inputs should be offloaded, not truncated."[^deepagents-remember] Offloading handles each spike when it arrives, while summarization handles the slow climb.[^deepagents-remember] Deep Agents offloads results as they occur, replaces old tool inputs with file pointers at 85% of the context window, and summarizes only when nothing is left to offload.[^deepagents-context-management][^deepagents-context-docs]

Anthropic's API offers clearing rather than offloading: by default it removes old tool results above 100,000 input tokens and keeps the last 3 tool uses, and the client keeps the full history.[^claude-context-editing] Clearing invalidates the cached prefix, so it is worth tuning against [prompt caching](/ai-engineering/context/prompt-caching.md).[^claude-context-editing] Offloading at arrival avoids that for the result itself, because no earlier message changes. That last point is my reading, not a claim from the sources.

# Limits

- The sources give thresholds, not results. None of them measures the benefit of offloading on its own. Deep Agents shows a token-use figure from terminal-bench-2 but no pass rates.[^deepagents-context-management]
- Coverage is uneven. Claude Code's documented threshold covers MCP results, and the OpenCode tools page doesn't mention offloading. I did not check Codex.
- Images need separate handling. Deep Agents' compression does not resize them or lower their resolution.[^deepagents-context-docs]
- Previews can mislead. If the useful part is deep in the file, the agent has to know to look for it. This is my reading, not a documented failure mode.

[^chase-late-2026]: Harrison Chase, LangChain blog, 2026-11-02.
[^deepagents-context-management]: Chester Curme and Mason Daugherty, LangChain blog, 2026-01-28.
[^deepagents-remember]: Jess Weng, LangChain blog, 2026-10-14.
[^deepagents-context-docs]: Deep Agents context engineering docs, read 2026-11-04.
[^deepagents-backends]: Deep Agents backends docs, read 2026-11-04.
[^claude-code-mcp]: Claude Code MCP docs, read 2026-11-04. The storage note and read-back behavior were read from a summary of the page.
[^claude-context-editing]: Claude context editing docs, read 2026-11-04.
[^anthropic-context-engineering]: Anthropic Engineering, 2025-09-29.
[^manus-context-engineering]: Yichao Ji, Manus blog, 2025-07-18.

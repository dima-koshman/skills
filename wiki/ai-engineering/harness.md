---
type: Knowledge Area
title: Agent Harness
aliases:
- Claude Code
- Codex
- Antigravity
- Deep Agents
- OpenCode
description: 'The runtime scaffolding around the model loop: tool dispatch, state, sandboxing, and loop
  control, with Claude Code, Codex, Antigravity, OpenCode and Deep Agents as implementations.'
tags:
- ai-engineering
- agents
parent: /ai-engineering.md
related:
- /ai-engineering/harness/programmatic-tool-calling.md
- /ai-engineering/multi-agent/dynamic-subagents.md
- /ai-engineering/context/prompt-caching.md
- /ai-engineering/models/scaledown.md
- /ai-engineering/models/providers/claude.md
- /ai-engineering/models/providers/gpt.md
- /ai-engineering/models/providers/gemini.md
status: draft
sources:
- id: claude-code-docs
  resource: https://code.claude.com/docs
  title: Claude Code documentation
  author: Anthropic
- id: claude-code-caching
  resource: https://claude.com/blog/lessons-from-building-claude-code-prompt-caching-is-everything
  title: Lessons from building Claude Code - Prompt caching is everything
  author: Anthropic
- id: langsmith-claude-code
  resource: https://docs.langchain.com/langsmith/trace-claude-code
  title: Trace Claude Code with LangSmith
  author: LangChain
- id: codex
  resource: https://openai.com/codex/
  title: Codex
  author: OpenAI
- id: antigravity
  resource: https://antigravity.google
  title: Google Antigravity
  author: Google
- id: opencode
  resource: https://opencode.ai
  title: OpenCode
  author: SST
- id: langsmith-opencode
  resource: https://docs.langchain.com/langsmith/trace-with-opencode
  title: Trace OpenCode with LangSmith
  author: LangChain
- id: deepagents-docs
  resource: https://docs.langchain.com/oss/python/deepagents/overview
  title: Deep Agents overview
  author: LangChain
- id: langchain-scaledown
  resource: https://www.langchain.com/blog/building-long-running-agents-with-scaledown-and-deep-agents
  title: Building long-running agents with ScaleDown and Deep Agents
  author: LangChain
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-18T12:00:00+04:00'
topics:
- /ai-engineering/harness/advisor.md
- /ai-engineering/harness/agents-as-tools.md
- /ai-engineering/harness/llm-browser-use.md
- /ai-engineering/harness/mcp.md
- /ai-engineering/harness/model-routing.md
- /ai-engineering/harness/programmatic-tool-calling.md
- /ai-engineering/harness/sandboxes.md
- /ai-engineering/harness/tool-search.md
- /ai-engineering/harness/tools.md
---

The harness is the runtime that drives the agent loop around the model: it parses each model response, dispatches the tool calls, feeds results back, manages context and memory, enforces sandboxing and limits (retries, max steps, budgets), and decides when to stop. It is the concrete implementation of an [agent](/ai-engineering.md#agent) — the model and the tools plug into it. It runs workflows or full agent loops and can support [programmatic tool calling](/ai-engineering/harness/programmatic-tool-calling.md). Frameworks like [Deep Agents](/ai-engineering/harness.md#deep-agents) ship a ready-made harness.

What the harness can call is defined by [tools](/ai-engineering/harness/tools.md) and, across processes, [MCP](/ai-engineering/harness/mcp.md). Delegating to other agents is covered in [Multi-Agent Systems](/ai-engineering/multi-agent.md).

How to place the sandbox relative to the harness is covered in [Agent Sandboxes](/ai-engineering/harness/sandboxes.md); choosing a model per task in [Model Routing](/ai-engineering/harness/model-routing.md); consulting a stronger model mid-task in [Advisor Tool](/ai-engineering/harness/advisor.md); wrapping a scoped subagent as a tool in [Agents as Tools](/ai-engineering/harness/agents-as-tools.md); loading tool definitions on demand in [Tool Search](/ai-engineering/harness/tool-search.md); driving a real web browser in [LLM Browser Use](/ai-engineering/harness/llm-browser-use.md).

## Implementations

| Harness | Maker | Models | Surfaces | Kind |
| --- | --- | --- | --- | --- |
| [Claude Code](/ai-engineering/harness.md#claude-code) | Anthropic | [Claude](/ai-engineering/models/providers/claude.md) | CLI, IDE extension, SDK | Coding agent |
| [Codex](/ai-engineering/harness.md#codex) | OpenAI | [GPT](/ai-engineering/models/providers/gpt.md) | CLI, cloud environments, IDE integration | Coding agent |
| [Antigravity](/ai-engineering/harness.md#antigravity) | Google | [Gemini](/ai-engineering/models/providers/gemini.md) | IDE, desktop app, CLI | Agent-first development platform |
| [Deep Agents](/ai-engineering/harness.md#deep-agents) | LangChain | Any, on LangGraph | Python library | Framework for building your own agent |
| [OpenCode](/ai-engineering/harness.md#opencode) | SST | Model-agnostic | Local terminal | Coding agent |

### Claude Code

Claude Code is Anthropic's coding agent: a terminal-native harness running Claude.[^claude-code-docs]

Its runtime is built around [prompt caching](/ai-engineering/context/prompt-caching.md) to keep latency and token cost low in multi-turn coding sessions:[^claude-code-caching]

- **Strict prefix ordering**: Base system instructions and tools are positioned first (globally cached), followed by project guidelines like `CLAUDE.md` and memory (cached per project), session environment context (cached per session), and finally append-only conversation messages.
- **Invariant tool definitions**: The harness never adds or removes tools mid-session. Modes such as Plan Mode are modeled as tools (`EnterPlanMode`, `ExitPlanMode`) that adjust instructions via conversation messages rather than modifying tool definitions. MCP tools use deferred loading (`defer_loading: true`) with tool search so schemas are discovered on demand without breaking prefix stability.
- **Message-based updates**: Dynamic data and context refreshes are injected into the message flow (e.g., via `<system-reminder>` blocks) rather than mutating the system prompt.
- **Cache-safe compaction**: When approaching context limits, compaction forks a call using the exact same system prompt, tools, and message prefix with a summarization prompt at the end, reusing the cached conversation history at cache-hit rates.
- **Operational observability**: Cache hit ratio is treated as a critical production health metric, with automated alerting and incident escalation when hit rates drop.

Claude Code usage can be traced in LangSmith with a plugin.[^langsmith-claude-code]

### Codex

Codex is OpenAI's coding agent: an open-source terminal CLI plus cloud environments and IDE integration, powered by OpenAI's frontier coding models. It runs tasks end-to-end — features, refactors, migrations — with agents working in parallel across git worktrees.[^codex]

### Antigravity

Antigravity is Google's agent-first development platform built on Gemini: an IDE, a desktop app, and a CLI that share one harness, where agents operate across the editor, terminal, and browser to build software from a prompt.[^antigravity]

### OpenCode

OpenCode is an open-source, terminal-native coding agent by the SST team. It is model-agnostic: it connects to many model providers rather than a single vendor, runs locally, and stores its sessions on disk. It is a vendor-neutral counterpart to [Claude Code](/ai-engineering/harness.md#claude-code).[^opencode] It can be used with Codex or Antigravity subscriptions, but not with Claude.

OpenCode usage can be traced in LangSmith with a plugin.[^langsmith-opencode]

### Deep Agents

Deep Agents is the LangChain library that packages production agent patterns — planning, [subagents](/ai-engineering/multi-agent/subagents.md), durable [memory](/ai-engineering/context/context-engineering.md#memory), human-in-the-loop, and [programmatic tool calling](/ai-engineering/harness/programmatic-tool-calling.md) — on top of LangGraph, which serves as its harness.[^deepagents-docs]

Middleware can hand Deep Agents' frequent context chores to small models. For example, [ScaleDown](/ai-engineering/models/scaledown.md) replaces the built-in history summarization, compresses tool output, extracts fields into state, and acts as a classifier circuit breaker for looping runs.[^langchain-scaledown]

[^claude-code-docs]: Anthropic, Claude Code documentation.
[^claude-code-caching]: Anthropic, "Lessons from building Claude Code: Prompt caching is everything".
[^langsmith-claude-code]: LangChain, "Trace Claude Code" in the LangSmith docs.
[^codex]: OpenAI, Codex product page.
[^antigravity]: Google, Antigravity site.
[^opencode]: opencode.ai.
[^langsmith-opencode]: LangChain, "Trace OpenCode" in the LangSmith docs.
[^deepagents-docs]: LangChain, Deep Agents overview.
[^langchain-scaledown]: LangChain blog, 2026-10-13.

---
type: Concept
title: Tools
aliases:
- Provider-Side Tools
- Frontend Tools
description: 'The primitive that turns an LLM into an agent: functions the model can call to act on and read from
  its environment, by where they run (backend, frontend, provider-side).'
tags:
- ai-engineering
- harness
parent: /ai-engineering/harness.md
related:
- /ai-engineering/harness/programmatic-tool-calling.md
- /ai-engineering/multi-agent/subagents.md
- /ai-engineering/harness/mcp.md
- /ai-engineering/harness/tool-search.md
status: draft
sources:
- id: ref-1
  resource: https://docs.langchain.com/oss/python/deepagents/tools
  title: docs.langchain.com
- id: provider-tools-ref-1
  resource: https://platform.claude.com/docs/en/agents-and-tools/tool-use/server-tools
  title: server tools
- id: ref-2
  resource: https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool
  title: web search
- id: ref-3
  resource: https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool
  title: web fetch
- id: ref-4
  resource: https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool
  title: code execution
- id: ref-5
  resource: https://developers.openai.com/api/docs/guides/tools
  title: built-in tools
- id: ref-6
  resource: https://developers.openai.com/api/docs/guides/tools-web-search
  title: web search
- id: ref-7
  resource: https://developers.openai.com/api/docs/guides/tools-file-search
  title: file search
- id: ref-8
  resource: https://developers.openai.com/api/docs/guides/tools-code-interpreter
  title: Code Interpreter
- id: ref-9
  resource: https://developers.openai.com/api/docs/guides/tools-image-generation
  title: image generation
- id: ref-10
  resource: https://ai.google.dev/gemini-api/docs/tools
  title: built-in tools
- id: ref-11
  resource: https://ai.google.dev/gemini-api/docs/google-search
  title: Google Search
- id: ref-12
  resource: https://ai.google.dev/gemini-api/docs/url-context
  title: URL context
- id: ref-13
  resource: https://ai.google.dev/gemini-api/docs/code-execution
  title: code execution
- id: frontend-tools-ref-1
  resource: https://a2ui.org
  title: Google's A2UI
- id: frontend-tools-ref-2
  resource: https://docs.langchain.com/oss/python/langchain/frontend/headless-tools
  title: LangChain's headless tools
- id: frontend-tools-ref-3
  resource: https://gofastmcp.com/apps/fastmcp-app
  title: FastMCP's implementation of MCP apps
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-18T12:00:00+04:00'
---

Reference: <https://docs.langchain.com/oss/python/deepagents/tools>

Tools are the main thing needed to convert an LLM into a capable agent. Without
them, most agent actions would end after one turn; with them, agents can interact
with the environment, fetch new context to condition their output on, and perform
complex tasks. They are like control statements in programming languages.
Additionally, tools are generic and can be used for almost any use case — ranging
from direct actions like querying a database to meta operations like
[programmatic tool calling](/ai-engineering/harness/programmatic-tool-calling.md) or recursive
[subagent](/ai-engineering/multi-agent/subagents.md) calling. Tools are exposed to models through
provider APIs and protocols like [MCP](/ai-engineering/harness/mcp.md).

## Where tools run

Tools for LLMs can be generally organized by where they execute:

- **Client-side tools** — executed by the client.
  - **Backend tools** — executed on the client's backend; the majority of tools
    fall into this category.
  - **[Frontend tools](/ai-engineering/harness/tools.md#frontend-tools)** — executed on the client's
    frontend, typically for UI interactions; a newer, less standardized category.
- **[Provider-side tools](/ai-engineering/harness/tools.md#provider-side-tools)** — defined and executed by the
  model provider (built-in web search, code execution, etc.); clients just enable
  them in API calls.

## Provider-side tools

Provider-side [tools](/ai-engineering/harness/tools.md) are defined and executed by the model
provider rather than the client — built-in capabilities like web search, code
execution, or hosted file search that a client simply enables in its API call. The
provider runs them and returns results inline, so the client never sees or hosts the implementation.

### Examples

- **Anthropic (Claude)** — Anthropic's
  [server tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/server-tools)
  include [web search](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool),
  [web fetch](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool),
  and [code execution](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool).
  Anthropic executes these inside the Claude API turn and returns the tool-use
  and result blocks to the client.
- **OpenAI (GPT models; analogous capabilities appear in ChatGPT)** — the
  Responses API provides [built-in tools](https://developers.openai.com/api/docs/guides/tools)
  including [web search](https://developers.openai.com/api/docs/guides/tools-web-search),
  [file search](https://developers.openai.com/api/docs/guides/tools-file-search),
  [Code Interpreter](https://developers.openai.com/api/docs/guides/tools-code-interpreter),
  and [image generation](https://developers.openai.com/api/docs/guides/tools-image-generation).
  ChatGPT product availability and API model support are related but separate.
- **Google (Gemini)** — Gemini's
  [built-in tools](https://ai.google.dev/gemini-api/docs/tools) include
  [Google Search](https://ai.google.dev/gemini-api/docs/google-search),
  [URL context](https://ai.google.dev/gemini-api/docs/url-context), and
  [code execution](https://ai.google.dev/gemini-api/docs/code-execution).
  Google executes these within the API request; custom function calls and
  Computer Use instead require the client to execute the requested action.

## Frontend tools

Frontend [tools](/ai-engineering/harness/tools.md) run on the client's frontend rather than its
backend, typically to drive UI interactions (rendering components, reading UI
state). It is a much newer and less standardized category than backend tools.
Examples:

- [Google's A2UI](https://a2ui.org)
- [LangChain's headless tools](https://docs.langchain.com/oss/python/langchain/frontend/headless-tools)
- [FastMCP's implementation of MCP apps](https://gofastmcp.com/apps/fastmcp-app)

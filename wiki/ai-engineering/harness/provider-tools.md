---
type: Concept
title: Provider-Side Tools
description: Tools defined and executed by the model provider — built-in web search, code execution —
  that clients just enable.
tags:
- ai-engineering
- harness
parent: /ai-engineering/harness.md
related:
- /ai-engineering/harness/tools.md
sources:
- id: ref-1
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
generated:
  by: codex/gpt-6
  at: '2026-10-15T15:23:06+04:00'
---

Provider-side [tools](/ai-engineering/harness/tools.md) are defined and executed by the model
provider rather than the client — built-in capabilities like web search, code
execution, or hosted file search that a client simply enables in its API call. The
provider runs them and returns results inline, so the client never sees or hosts the implementation.

## Examples

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

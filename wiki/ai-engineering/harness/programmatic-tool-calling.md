---
type: Concept
title: Programmatic Tool Calling
aliases:
- PTC
- Code Mode
- Code Execution with MCP
description: Code mode and programmatic tool calling move tool or subagent orchestration into generated code, keeping intermediate results outside the main model context.
tags:
- ai-engineering
- harness
- code-mode
- programmatic-tool-calling
parent: /ai-engineering/harness.md
related:
- /ai-engineering/agents/agent.md
- /ai-engineering/harness/subagents.md
- /ai-engineering/harness/dynamic-subagents.md
- /ai-engineering/context/mcp.md
- /ai-engineering/context/context-engineering.md
- /ai-engineering/security/risks/unexpected-code-execution.md
sources:
- id: claude-workflows
  resource: https://code.claude.com/docs/en/workflows
  title: Claude Workflows
- id: deepagents-dynamic-subagents
  resource: https://docs.langchain.com/oss/python/deepagents/dynamic-subagents
  title: LangChain Dynamic Subagents
- id: fastmcp-code-mode
  resource: https://gofastmcp.com/servers/transforms/code-mode
  title: FastMCP Code Mode
- id: cloudflare-code-mode
  resource: https://blog.cloudflare.com/code-mode/
  title: 'Code Mode: the better way to use MCP'
  author: Kenton Varda and Sunil Pai
- id: anthropic-mcp-execution
  resource: https://www.anthropic.com/research/code-execution-with-mcp
  title: Code execution with MCP for efficient agents
- id: anthropic-programmatic-tools
  resource: https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling
  title: Programmatic tool calling
- id: codeact
  resource: https://arxiv.org/abs/2402.01030
  title: Executable Code Actions Elicit Better LLM Agents
  author: Xingyao Wang et al.
- id: smolagents
  resource: https://github.com/huggingface/smolagents
  title: smolagents
  author: Hugging Face
- id: cloudflare-api-code-mode
  resource: https://blog.cloudflare.com/code-mode-mcp/
  title: 'Code Mode: give agents an entire API in 1,000 tokens'
  author: Matt Carey
- id: anthropic-dynamic-filtering
  resource: https://claude.com/resources/articles/improved-web-search-with-dynamic-filtering
  title: Increase web search accuracy and efficiency with dynamic filtering
  author: Anthropic
- id: bitter-lesson-tool-calling
  resource: https://arxiv.org/html/2608.06370v1
  title: The Bitter Lesson of Tool Calling
  author: Ishan Patel et al.



generated:
  by: codex/gpt-6
  at: '2026-10-22T13:46:52+04:00'
---

## Core pattern

An [agent](/ai-engineering/agents/agent.md) writes a program that calls tools or
[subagents](/ai-engineering/harness/subagents.md), handles loops and branches, and
filters or combines their outputs. Intermediate results stay in runtime variables;
only selected output returns to the coordinating model. This can reduce model
round trips and context use, especially when many calls return large datasets.[^anthropic-programmatic-tools]

For example, code can fetch expenses for 20 employees, calculate totals, and return
only those over budget. The model need not read every expense line or decide each
addition and comparison itself.[^anthropic-programmatic-tools]

## Names and implementations

These names overlap, but describe different scopes:

| Name | Meaning / implementation |
| --- | --- |
| **Code mode** | Cloudflare's name for presenting MCP tools as a TypeScript API and having the model write code against it. FastMCP implements the same approach using Python and MCP meta-tools.[^cloudflare-code-mode][^fastmcp-code-mode] |
| **Programmatic tool calling (PTC)** | A useful name for the general mechanism; also an Anthropic API feature where generated code invokes tools and processes results in a code execution container.[^anthropic-programmatic-tools] |
| **Code execution with MCP** | Anthropic's description of exposing MCP tools as code interfaces, loading definitions on demand, and processing tool results outside the model context.[^anthropic-mcp-execution] |
| **CodeAct / executable code actions** | A research formulation from Wang et al. (2024): Python code is the agent's action representation. Broader than MCP orchestration; the interpreter can perform computation as well as tool calls.[^codeact] |
| **Code agents** | Hugging Face's `smolagents.CodeAgent` writes actions as Python snippets within a ReAct-style loop. It can compose tools in one action; execution logs still feed subsequent model steps.[^smolagents] |
| **Dynamic workflows / dynamic subagents** | Claude Code workflows use JavaScript to coordinate subagents through `agent()`, `pipeline()`, and `parallel()`. Deep Agents supports JavaScript subagent orchestration through `task()` inside an interpreter.[^claude-workflows][^deepagents-dynamic-subagents] |

Claude Code workflows and FastMCP CodeMode therefore share an architectural idea,
but work at different layers: the former coordinates agents; the latter composes
MCP tool calls. A subagent may run its own model/tool loop internally even when
the outer orchestration is scripted.[^claude-workflows][^fastmcp-code-mode]

## Two separate optimizations

1. **Code orchestration:** move control flow and intermediate data into a runtime.
2. **Progressive tool discovery:** load only relevant tool definitions instead of
   the full catalog. FastMCP combines these through `search`, `get_schema`, and
   `execute`; discovery can also be used independently of code execution.[^fastmcp-code-mode]

Code mode does not inherently require discovery: Cloudflare's original 2025
implementation loaded the complete generated API into context.[^cloudflare-code-mode]
Both optimizations are forms of [context engineering](/ai-engineering/context/context-engineering.md).

## Boundaries and trade-offs

- The word **workflow** is broader than this pattern: a fixed, developer-written
  pipeline need not involve model-generated orchestration code.
- Ordinary code execution, such as calculating a value in Python, becomes this
  tool-orchestration pattern when the generated program can invoke the agent's tools.
- A single small tool call may not justify code-generation and runtime overhead.
  If every next step needs fresh model judgment, scripting cannot remove those
  model calls.[^anthropic-programmatic-tools]
- Model-written code requires an appropriate execution boundary; see
  [Agent Sandboxes](/ai-engineering/harness/sandboxes.md) and
  [Unexpected Code Execution](/ai-engineering/security/risks/unexpected-code-execution.md).

## What PTC provides, and what the harness provides

PTC controls tool execution and data flow. Task decomposition is still a planning
decision made by the model or developer; separate model contexts require subagents
or another isolation mechanism. Checkpointing, recovery after a crash, scheduling,
and handling user input during a long task require runtime support. A long script
does not provide durable execution by itself. For example, Anthropic's managed
PTC has container expiration and tool-result waiting deadlines.[^anthropic-programmatic-tools]

## Dynamic subagents

[Dynamic Subagents](/ai-engineering/harness/dynamic-subagents.md) is the narrower
application of PTC where generated code invokes agents as tools. That concept
covers aliases, cost comparisons, and Claude Code, Codex and OpenCode support.
**Code mode is the generic PTC mechanism**, whether the called tools are ordinary
APIs or subagents. Ordinary delegation can use separate contexts without any
programmatic orchestration.

## Adoption and improving models (2026-10-22)

There is concrete product adoption, although the sources below do not establish
industry-wide usage rates:

- Cloudflare's API MCP server uses code mode to expose more than 2,500 endpoints
  through `search()` and `execute()`. This is a deployed integration, rather than
  only an SDK demonstration.[^cloudflare-api-code-mode]
- Anthropic integrated code-based result filtering into web search and web fetch
  in February 2026. Its vendor evaluation reported higher accuracy and 24% fewer
  input tokens on average across two benchmarks. Price-weighted token use fell for
  Sonnet 4.6 but rose for Opus 4.6: fewer input tokens did not guarantee lower
  total cost.[^anthropic-dynamic-filtering]

**Assessment, not a measured explanation of adoption:** improving models can
reduce the need to work around weak reasoning or limited usable context. They do
not remove the potential cost of repeatedly reading large intermediate results
or generating one call per item. A stronger code model can also write better
orchestration programs, making PTC complementary to model improvement. Whether
those savings justify integration depends on the workload and available harness.
This argument does not require predicting a model-capability ceiling.

Plausible reasons PTC may be less visible as a distinct feature:

1. **The benefit is concentrated.** Bulk lookups, joins, filtering, and aggregation
   can run in code without fresh judgment at every step. Exploratory tasks that
   need model reasoning after each observation offer less opportunity to remove
   model turns.[^anthropic-programmatic-tools]
2. **Existing interfaces overlap with it.** A coding agent with shell and SDK
   access can already compose API calls in scripts. Cloudflare discusses CLIs,
   dynamic tool search, and client/server code mode as alternative approaches.
   Adoption of the behavior can therefore be less visible than adoption of the
   PTC name.[^cloudflare-api-code-mode]
3. **Integration has a cost.** Generated programs need reliable result schemas,
   an execution boundary, and error handling. Provider implementations can also
   restrict tool compatibility; Anthropic's managed PTC currently excludes tools
   exposed through its MCP connector. This restriction does not apply to the
   general pattern or server-side MCP code mode.[^anthropic-programmatic-tools]

One August 2026 preprint found PTC matched or exceeded JSON calling in 11 of 14
models, with better results in newer generations. Its benchmark used echo-return
stubs rather than real APIs, so it measures argument serialization rather than
end-to-end task correctness. Small ablations and fixed prompt overhead further
limit conclusions about production performance or scaling trends.[^bitter-lesson-tool-calling]

The useful design question is whether several actions can be expressed reliably
as code before another model judgment is needed. For small interactive tasks,
direct calls can be sufficient; for bulk data processing, PTC can remain valuable
even with a much more capable model.[^anthropic-programmatic-tools]

[^claude-workflows]: [Claude Code dynamic workflows](https://code.claude.com/docs/en/workflows).
[^deepagents-dynamic-subagents]: [Deep Agents dynamic subagents](https://docs.langchain.com/oss/python/deepagents/dynamic-subagents).
[^fastmcp-code-mode]: [FastMCP Code Mode](https://gofastmcp.com/servers/transforms/code-mode).
[^cloudflare-code-mode]: Kenton Varda and Sunil Pai, [Code Mode: the better way to use MCP](https://blog.cloudflare.com/code-mode/), September 26, 2025.
[^anthropic-mcp-execution]: Anthropic, [Code execution with MCP for efficient agents](https://www.anthropic.com/research/code-execution-with-mcp).
[^anthropic-programmatic-tools]: [Programmatic tool calling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling).
[^codeact]: Wang et al., [Executable Code Actions Elicit Better LLM Agents](https://arxiv.org/abs/2402.01030), 2024.
[^smolagents]: Hugging Face, [smolagents](https://github.com/huggingface/smolagents).
[^cloudflare-api-code-mode]: Matt Carey, [Code Mode: give agents an entire API in 1,000 tokens](https://blog.cloudflare.com/code-mode-mcp/), February 20, 2026.
[^anthropic-dynamic-filtering]: Anthropic, [Increase web search accuracy and efficiency with dynamic filtering](https://claude.com/resources/articles/improved-web-search-with-dynamic-filtering), February 17, 2026.
[^bitter-lesson-tool-calling]: Patel et al., [The Bitter Lesson of Tool Calling](https://arxiv.org/html/2608.06370v1), August 6, 2026, especially section 7 (Limitations).

---
type: Concept
title: Agents as Tools
aliases:
- Agent as Tool
- AgentTool
- Subagent as a Tool
- Context Quarantine
description: Wrapping a scoped agent behind a tool call, so the parent gets one distilled answer back while the
  noisy reading, searching and retries stay in the agent's own context.
tags:
- ai-engineering
- harness
- context
- subagents
parent: /ai-engineering/harness.md
related:
- /ai-engineering/multi-agent/subagents.md
- /ai-engineering/harness/advisor.md
- /ai-engineering/harness/tools.md
- /ai-engineering/context/context-engineering.md
- /ai-engineering/context/tool-result-offloading.md
status: draft
sources:
- id: openai-agents-multi-agent
  resource: https://openai.github.io/openai-agents-python/multi_agent/
  title: Agent orchestration
  author: OpenAI Agents SDK
- id: adk-agent-tool
  resource: https://codelabs.developers.google.com/devsite/codelabs/build-agents-with-adk-empowering-with-tools
  title: 'Building AI Agents with ADK: Empowering with Tools'
  author: Google
- id: breunig-fix-context
  resource: https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html
  title: How to Fix Your Context
  author: Drew Breunig
  last_modified: '2025-06-26T00:00:00Z'
- id: anthropic-research-system
  resource: https://www.anthropic.com/engineering/multi-agent-research-system
  title: How we built our multi-agent research system
  author: Anthropic
- id: mikhail-webfetch
  resource: https://mikhail.io/2025/10/claude-code-web-tools/
  title: "Inside Claude Code's Web Tools: WebFetch vs WebSearch"
  author: Mikhail Shilkov
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-18T11:00:00+04:00'
---

An agent with its own model, prompt, tools and context is exposed to a parent agent as an ordinary tool. The parent
calls it with a task, the agent works in its own context, and only its final answer comes back as the tool result.
The parent keeps control of the conversation throughout.

# Names

- **Agents as tools**: OpenAI's Agents SDK turns an agent into a tool with `Agent.as_tool()`. The orchestrator calls
  it and keeps reasoning, unlike a **handoff**, which passes the conversation to the other agent.[^openai-agents-multi-agent]
- **`AgentTool`**: Google ADK's wrapper. Google's codelab uses it to give a root agent a search specialist, so the
  root agent can delegate web searches without being able to search itself.[^adk-agent-tool]
- **Context quarantine**: Drew Breunig's name for the reason it works: "isolating contexts in their own dedicated
  threads".[^breunig-fix-context]
- **Compression**: Anthropic's research system describes subagents exploring in their own context windows "before
  condensing the most important tokens for the lead research agent".[^anthropic-research-system]

# Agent as tool vs subagent

The line is blurry: the two names describe the same mechanism from different angles. This section is our own
analysis.

- **Same interface.** To the caller, every one of these is a tool call: input in, text out. A Claude Code subagent
  is started through a tool too (`Agent`). What runs behind the call, whether a fixed pipeline, one model call or a
  full agent loop, is invisible to the caller and can change without the caller noticing.
- **"Agent as tool" names the packaging**: a fixed contract, with a tool name, description and input schema,
  defined ahead of time by whoever builds the tool, and an implementation that the caller can't see.
- **"Subagent" names the relationship**: an agent that a parent starts and directs, usually with a free-form task
  the parent writes on the spot, working in the parent's workspace under its permissions.

Inherited context does **not** separate them. In Claude Code a regular subagent starts cold, with only the prompt
the parent wrote; only a fork inherits the parent's conversation. The axes that do vary, for both names:

| Axis | One end | Other end |
| --- | --- | --- |
| Control | Returns to the caller (tool, subagent) | Takes over the conversation (handoff)[^openai-agents-multi-agent] |
| Context | Cold: only the prompt | Fork: the parent's whole conversation |
| Defined by | The developer, ahead of time (`web-fetch`, `Explore`) | The parent, at run time (general-purpose agent and a custom prompt) |
| Lifetime | One call | Addressable later, keeping its context |
| Owner | The same harness and workspace | A remote service, for example over [A2A](/ai-engineering/multi-agent/a2a.md) |

## What a loop changes behind the same interface

An implementation without a loop, such as Claude Code's WebFetch (fetch the page, convert it to Markdown, answer the
caller's prompt with a small fast model[^mikhail-webfetch]), and one with a loop, such as a `web-fetch` subagent that
can try other pages, look the same to the caller. The difference shows up elsewhere:

- **Cost and latency**: a pipeline's cost is bounded, while a loop's varies with the task.
- **Recovery**: a loop can retry, follow links and look further, but a pipeline answers from what it was given.
- **Blast radius**: an agent with tools can act. Injected instructions in what it reads can make it do things, not
  only say things, so give it read-only tools where possible.

In both, the raw material never enters the parent's context. Only the answer does.

# Good fits

The pattern fits work that reads a lot and returns a little, has a clear question, and can be checked. Examples
(our own list):

- **Web reading and research**: read the pages, answer the question, cite the URLs.
- **Codebase search**: "where is X configured and who calls it", returning paths and lines, not file dumps.
- **Logs, traces and metrics**: scan a large log or trace and return the error pattern with a few sample lines.
- **Test triage**: run the suite and return only the failures, with their root-cause guess.
- **Long documents**: a PDF, a spec or a ticket history, read against one question.
- **History search**: find the past session or chat where something was decided.
- **Data questions**: explore tables with SQL and return the answer and the final query.
- **Independent checks**: verify one claim, or review one diff, without seeing the parent's reasoning.

# Costs and risks

Our own analysis:

- **Lossy by design.** The parent sees only what the agent chose to report and can't tell what was dropped. A
  summarizer can also paraphrase text that was needed verbatim.
- **The report is model output.** Check the claims that matter. Ask for quotes and source locations so they can be
  checked.
- **A cold start.** The agent shares none of the parent's context, so the task prompt must carry everything it
  needs: the question, the constraints, and what a good answer looks like.
- **Latency and cost.** Each call is a separate loop. For one small file, reading it directly is cheaper.
- **Prompt injection is reduced, not removed.** Untrusted pages are read in the agent's context, but its report
  can still carry their instructions. The parent should treat the report as data.

# How to scope the call

- Ask a question, not "summarize this".
- Say what to return and how long it should be: a table, file paths with lines, quotes with URLs.
- Give the agent only the tools the task needs, read-only where possible.
- Name what "not found" looks like, so the agent reports a gap instead of guessing.

[^openai-agents-multi-agent]: OpenAI Agents SDK docs, "Agent orchestration".
[^adk-agent-tool]: Google codelab, "Building AI Agents with ADK: Empowering with Tools".
[^breunig-fix-context]: Drew Breunig, "How to Fix Your Context", 2025-06-26, section on context quarantine.
[^anthropic-research-system]: Anthropic Engineering, "How we built our multi-agent research system".
[^mikhail-webfetch]: Mikhail Shilkov, "Inside Claude Code's Web Tools", 2025-10. A third-party analysis, not official
    documentation.

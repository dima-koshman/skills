---
type: Concept
title: Dynamic Subagents
aliases:
- Programmatic Subagents
- Programmatic Subagent Orchestration
- Dynamic Workflows
description: An agent writes code that dispatches subagents, branches on their results, and controls what returns to the coordinating model.
tags:
- ai-engineering
- harness
- subagents
parent: /ai-engineering/harness.md
subtype_of: /ai-engineering/harness/programmatic-tool-calling.md
related:
- /ai-engineering/harness/subagents.md
- /ai-engineering/agents/deep-agents.md
- /ai-engineering/harness/sandboxes.md
- /ai-engineering/context/prompt-caching.md
sources:
- id: deepagents-dynamic-subagents
  resource: https://docs.langchain.com/oss/python/deepagents/dynamic-subagents
  title: Dynamic subagents
  author: LangChain
- id: langchain-dynamic-subagents-post
  resource: https://www.langchain.com/blog/introducing-dynamic-subagents-in-deep-agents
  title: Introducing Dynamic Subagents in Deep Agents
  author: Sydney Runkle, Colin Francis and Hunter Lovell
- id: claude-workflows
  resource: https://code.claude.com/docs/en/workflows
  title: Orchestrate subagents at scale with dynamic workflows
- id: codex-subagents
  resource: https://learn.chatgpt.com/docs/agent-configuration/subagents
  title: Subagents
- id: codex-config
  resource: https://learn.chatgpt.com/docs/config-file/config-reference
  title: Configuration Reference
- id: opencode-v2-tools
  resource: https://dev.opencode.ai/v2/docs/tools/
  title: OpenCode V2 Tools
generated:
  by: codex/gpt-6
  at: '2026-10-22T13:46:52+04:00'
---

## Meaning and taxonomy

Here, **dynamic subagents** means the programmatic orchestration pattern: the
coordinating agent writes a program that calls subagents as tools. The program
handles loops, branches, concurrency and intermediate results. This is a subtype
of [Programmatic Tool Calling](/ai-engineering/harness/programmatic-tool-calling.md)
whose tools are agents with their own model/tool loops.[^deepagents-dynamic-subagents]

The aliases are overlapping product vocabulary, not a standard: LangChain uses
**dynamic subagents** and **programmatic subagents**; Claude Code calls its
implementation **dynamic workflows**.[^langchain-dynamic-subagents-post][^claude-workflows]
The broader phrase “dynamically spawning subagents” can also describe ordinary
model-driven delegation, which need not use PTC. A fixed developer-written agent
pipeline is programmatic orchestration, but need not involve model-generated code.

**Code mode belongs with generic PTC.** It describes the code execution interface;
dynamic subagents describes using that mechanism to coordinate agents. The same
code mode could instead query databases or compose API calls without any workers.

## What scripting adds

Ordinary [subagents](/ai-engineering/harness/subagents.md) already isolate worker
contexts. Code additionally lets the coordinator dispatch a whole task set,
inspect structured results, and launch follow-up workers without another parent
model turn for every decision. A planning worker can return the task list; the
script can send selected findings to a verifier and return a compact synthesis.
LangChain demonstrates this with interpreter-accessible `task()` calls.[^deepagents-dynamic-subagents]

For example, a review can process an explicit file list in bounded batches,
collect findings, verify only plausible findings, and report completed, failed
and skipped files. A loop makes coverage inspectable; successful completion still
depends on handling failures, limits and incomplete worker outputs. Running all
workers simultaneously is optional.[^langchain-dynamic-subagents-post]

## Cost and useful small cases

Keep two comparisons separate:

- **Same workers, scripted versus model-coordinated:** scripting can save parent
  inference and prevent intermediate worker results from entering its context.
- **Many workers versus one agent:** worker inference still costs tokens; reducing
  coordinator overhead does not establish lower total cost.

Small designs worth measuring include an investigator/verifier chain that skips
verification when there are no findings, and a repair loop with a check, a bounded
retry count and an explicit stop condition. These are design possibilities, not
measured cost wins. Compare quality, elapsed time and billed usage against a
single-agent baseline. Context isolation comes from subagents; checkpointing and
recovery come from the runtime; task decomposition still requires judgment.

## Harness support checked on 2026-10-22

| Harness | Confirmed support and boundary |
| --- | --- |
| Claude Code | JavaScript workflows coordinate workers through `agent()`, `pipeline()` and `parallel()`. They can be explicitly requested or rerun from saved commands; opting into ultracode permits automatic selection. Docs emphasize large tasks but also show bounded check/fix loops and a `small` size guideline.[^claude-workflows] |
| Codex | Ordinary subagent workflows are available by default, subject to delegation instructions. The separate `features.code_mode.enabled` option is under development and off by default. These facts alone do not establish code-callable worker tools or a Claude-style saved workflow facility.[^codex-subagents][^codex-config] |
| OpenCode V2 | Documents both a JavaScript `execute` Code Mode tool and a `subagent` tool for child sessions. The tools page alone does not establish that `subagent` is callable inside `execute`, or a saved workflow facility.[^opencode-v2-tools] |

Claude Code also documents sibling prompt-prefix reuse: a new worker thread need
not start with an entirely cold cache. Matching model and agent configuration
matter. This reduces duplicated prefix processing, not the cost of each worker's
own reasoning and tool work.[^claude-workflows]

[^deepagents-dynamic-subagents]: LangChain, [Dynamic subagents](https://docs.langchain.com/oss/python/deepagents/dynamic-subagents).
[^langchain-dynamic-subagents-post]: Runkle, Francis and Lovell, [Introducing Dynamic Subagents in Deep Agents](https://www.langchain.com/blog/introducing-dynamic-subagents-in-deep-agents), June 29, 2026.
[^claude-workflows]: [Claude Code dynamic workflows](https://code.claude.com/docs/en/workflows), including size guidelines and prompt caching.
[^codex-subagents]: [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents), official OpenAI documentation.
[^codex-config]: [Configuration Reference](https://learn.chatgpt.com/docs/config-file/config-reference), official OpenAI documentation.
[^opencode-v2-tools]: [OpenCode V2 Tools](https://dev.opencode.ai/v2/docs/tools/).

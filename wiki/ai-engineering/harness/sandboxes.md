---
type: Practice
title: Agent Sandboxes
description: Run the harness outside the sandbox and call the sandbox as a tool, keeping session state in a
  durable store, so harness, sandbox and session can each fail or be replaced on their own ("cattle, not pets").
tags:
- ai-engineering
- harness
- security
parent: /ai-engineering/harness.md
related:
- /ai-engineering/harness/tools.md
- /ai-engineering/agents/deep-agents.md
- /ai-engineering/harness/subagents.md
- /ai-engineering/security.md
sources:
- id: anthropic-managed-agents
  resource: https://www.anthropic.com/engineering/managed-agents
  title: 'Scaling Managed Agents: Decoupling the brain from the hands'
  author: Lance Martin, Gabe Cemaj, Michael Cohen (Anthropic)
  last_modified: '2026-04-08T00:00:00Z'
- id: deepagents-sandboxes
  resource: https://docs.langchain.com/oss/python/deepagents/sandboxes
  title: Deep Agents sandboxes (LangChain docs, read 2026-10-16)
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-10-16T16:00:00+04:00'
---

A sandbox is the isolated environment where an agent runs code and edits files. The design question is
where the harness — the loop that calls the model — runs relative to it.

## Two patterns

| | Agent in the sandbox | Sandbox as a tool |
| --- | --- | --- |
| Where the harness runs | Inside the container, next to the files | On your server; calls the sandbox through tools |
| Secrets | API keys must be inside the sandbox | Stay on the host; authenticated calls run in host-side tools |
| Failure | Container dies → session lost | Each part fails and restarts on its own |
| Good for | A single developer's local agent (Claude Code style) | Multi-user platforms and production agents |

Deep Agents recommends sandbox-as-tool for most cases: you pass a sandbox backend (LangSmith, Daytona,
E2B, Modal, Runloop, Vercel and others) to `create_deep_agent(backend=...)` and the agent gets file tools
plus an `execute` tool. A provider only implements `execute()`; file operations are built on
it.[^deepagents-sandboxes]

## Pets vs cattle

An ops metaphor. **Pets** are servers you name and nurse back to health, because their state lives inside
them. **Cattle** are identical and disposable: when one fails, you replace it.

Anthropic's first Managed Agents design ran session, harness and sandbox in one container. That made each
container a pet: a failed container lost the session, unresponsive ones were revived by hand, and
debugging meant opening a shell in containers holding user data. A harness bug, a dropped event and a dead
container also looked the same from outside. Every session paid full container setup before the first
token, and reaching customer networks meant peering or running the harness in their
environment.[^anthropic-managed-agents]

## What makes it work

Separating the processes is only half of it. Each part must also be disposable:

1. **Stateless harness.** Session state lives in a durable store — Anthropic uses an append-only event
   log — so a new harness instance can resume after a crash.[^anthropic-managed-agents]
2. **One interface to the sandbox.** Anthropic calls tools through a single `execute(name, input)`
   interface and provisions containers only when a session needs one. p50 time-to-first-token dropped
   ~60% and p95 by over 90%.[^anthropic-managed-agents]
3. **Scoped, short-lived sandboxes.** One per thread by default, with an idle TTL; sandboxes shared by an
   assistant accumulate state and need snapshots or cleanup.[^deepagents-sandboxes]
4. **Least privilege.** No secrets in the sandbox, network blocked unless needed, and everything the
   sandbox returns treated as untrusted input.[^deepagents-sandboxes]

## Costs

Every tool call crosses the network, files move across the boundary with `upload_files()` and
`download_files()`, and there are more services to run and monitor.[^deepagents-sandboxes]

[^anthropic-managed-agents]: Anthropic Engineering, 2026-04-08.
[^deepagents-sandboxes]: LangChain Deep Agents docs, read 2026-10-16.

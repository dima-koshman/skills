---
type: Technique
title: Agent Skills
description: Packaged instruction files an agent loads on demand — most useful as behavior control, and a context tax when installed indiscriminately.
resource: https://code.claude.com/docs/en/skills
timestamp: 2026-07-20
---

A skill is a directory holding a `SKILL.md` — YAML frontmatter (`name`,
`description`) plus a markdown body — that an [agent](/agents/agent.md) loads on
demand when the description matches the task. The [harness](/harness/harness.md)
keeps every installed skill's name and description in context every turn, and
pulls the body in only when the skill is invoked. This two-tier design is
[context engineering](/context/context-engineering.md): descriptions are the
always-on index, bodies are the progressive disclosure.

Skills are portable across harnesses — [Claude Code](/agents/claude-code.md),
[OpenCode](/agents/opencode.md), and [Codex](/agents/codex.md) all read the same
format, though each scans different directories. Installers such as `npx skills`
copy a skill into a canonical store and symlink it into each harness's directory.

# Knowledge source vs. behavior control

Skills serve two distinct purposes, and their value is diverging.

**As a knowledge source**, a skill supplies facts the model lacks: a proprietary
API's shape, an internal schema, a house style guide. This is durable value for
private or fast-moving knowledge — but it decays as frontier models improve.
Content restating widely-known practice (what TDD is, how to bisect a bug) buys
little from a frontier model that already knows it, while still costing context.
For public library documentation specifically, live retrieval via
[MCP](/context/mcp.md) beats a vendored snapshot, which silently goes stale.

**As behavior control**, a skill changes what the agent does by default at a
decision point — investigate before patching, design before implementing. Here
the value is real and does not decay with model capability, because it targets
tendency rather than knowledge. The model knows the practice; the skill makes it
the default.

This second purpose is where skills are weakest structurally. A skill is invoked
on demand, so it only fires when the agent recognizes the moment — and the moments
that most need discipline are exactly the ones an agent doesn't flag. A skill
demanding fresh verification before claiming success never triggers, because an
agent about to over-claim is by definition not feeling cautious. Skills work as
**entry points to a workflow** the agent deliberately enters; they fail as
**always-on constraints**.

Always-on constraints belong in `AGENTS.md` / `CLAUDE.md`, which is loaded once
per session and stays in context. That file is also project-scoped and
hand-edited, so it can be tuned to a codebase and a team in a way a generic
third-party skill cannot.

# Where skills cost more than they return

- **Listing tax.** Every installed skill's description sits in context every turn
  whether relevant or not. Harnesses cap this (Claude Code reserves ~1% of the
  window by default), so a bloated listing crowds out genuinely relevant entries.
- **Bulk installation.** Publishing an entire directory of skills globally because
  it is one command is the common failure. Scope skills to the projects that need
  them; install globally only what is genuinely cross-cutting.
- **Plugins are all-or-nothing.** A plugin bundles skills with hooks and commands.
  Per-skill visibility controls (Claude Code's `skillOverrides`) explicitly do not
  apply to plugin skills, so a plugin's entire skill set is accepted or refused
  together. Installing the same skills directly makes them individually tunable.
- **Session-start injection.** Plugins may register a `SessionStart` hook that
  injects instructions into every session, unconditionally and outside the skill
  system's budget. This is how a plugin enforces its discipline — and it is a
  standing context cost that survives compaction.
- **Duplicate registration.** Harnesses scan several directories; the same skill
  reachable through two of them registers twice. Installing a project-local skill
  into a project-scoped directory can produce a copy that silently drifts from
  the original.
- **Third-party skills execute with full agent permissions** and may ship scripts.
  Treat an installed skill as a dependency with the trust level of code, not
  documentation — see [supply chain compromise](/security/risks/supply-chain-compromise.md)
  and [agent goal hijack](/security/risks/agent-goal-hijack.md).

# Design considerations

- **Prefer `AGENTS.md` to a generic plugin** for controlling agent behavior. It is
  project-scoped, always in context, editable, and it can state which skills to use
  and when — giving explicit control over skill invocation that an installed skill
  cannot exert over itself.
- **Install skills selectively and knowingly.** Prefer naming individual skills over
  installing a repository wholesale, and prefer project scope over global.
- **Audit against actual usage.** Harnesses record skill invocation counts. In
  practice a small minority of installed skills accounts for nearly all invocations;
  the remainder are pure listing tax. Skills that are valuable but never invoked are
  a signal to move their rules into `AGENTS.md`, not to keep waiting.
- **Extract, don't import wholesale.** When a third-party skill contains a few good
  rules inside a long document, lift the rules into `AGENTS.md` and skip the skill.
  Prose written to argue a weaker model out of rationalizing is wasted on a frontier
  model — state the rule.
- **Track provenance.** Remote-sourced skills should be lock-tracked so they can be
  refreshed from upstream rather than vendored and forgotten.
- **Reserve skills for what they are good at**: workflows with a clear entry point,
  genuinely private knowledge, and executable tooling the agent invokes.

# Citations

- [Claude Code — Agent Skills](https://code.claude.com/docs/en/skills)
- [Anthropic — Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [anthropics/skills](https://github.com/anthropics/skills)
- [obra/superpowers](https://github.com/obra/superpowers)

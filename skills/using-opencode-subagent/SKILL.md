---
name: using-opencode-subagent
description: >
  Use when delegating a task to opencode (GPT-5 via the user's ChatGPT subscription) — for a
  second opinion, cross-checking a tricky result, when a GPT model is better suited, or to have
  GPT-5 implement file edits autonomously. Covers the non-interactive command, the
  --dangerously-skip-permissions authorization gate, self-contained prompts, session continuation,
  background runs, and the review gate on opencode-written code.
---

# Using opencode as a Subagent

## Overview

`opencode` is installed (`/opt/homebrew/bin/opencode`) and authenticated with the user's ChatGPT
subscription. Use it to delegate a task to a GPT-5 model — for a second opinion, for cross-checking
a tricky result, when a GPT model is better suited, or to have GPT-5 implement features directly in
the working tree. Docs: <https://opencode.ai/docs/>

## Quick Reference

Run non-interactively (always use `gpt-5.5` for now):

```bash
opencode run --model openai/gpt-5.5 --variant high --dangerously-skip-permissions "<self-contained prompt>"
```

| Flag | Purpose |
|------|---------|
| `--model openai/gpt-5.5` | The model. Always `gpt-5.5` for now. |
| `--variant high` | Reasoning effort (`minimal`, `high`, `max`). |
| `--dangerously-skip-permissions` | Required for any non-interactive run (see below). |
| `--format json` | Emit parseable events; carries a server-generated `sessionID` (`ses_...`). |
| `-c` | Continue the most recent session. |
| `--session <id>` | Continue a specific session by id (from a prior run's JSON). |

## The authorization gate (read first)

**`--dangerously-skip-permissions` is required for non-interactive runs.** Without it, opencode
pauses to ask before each tool call (read, edit, command) and stalls a piped/background run waiting
for input that never comes. The flag auto-approves those gates.

The Claude Code auto-mode classifier BLOCKS this flag unless the user has authorized it — **get
explicit user sign-off first.** It's their call, since the flag disables opencode's own safety
gates. Once authorized, it applies to read-only second-opinion runs too, not just file-editing ones.

## Writing the prompt

- The prompt MUST be fully self-contained. opencode does NOT see this conversation's context —
  paste in any code, file contents, or background it needs.
- opencode runs from the current working directory and can read project files, so you may reference
  paths instead of pasting when the file is in-repo.
- Capture stdout and integrate/relay the result; note clearly when an answer came from
  opencode/GPT-5 vs. from you.

## Continuing a session

To continue a prior opencode session instead of starting cold, add `-c` (most recent) or
`--session <id>` (the id from a prior run's JSON). The session id is allocated server-side; you
cannot pin an arbitrary one upfront. Use `--format json` to capture the id from the run you want
to resume.

## Delegating implementation work (file edits), not just answers

`opencode run` can also implement features — it edits files directly in the working tree, runs
commands, and self-verifies. Lessons from doing this:

- **Permissions.** Editing autonomously needs `--dangerously-skip-permissions` (see the
  authorization gate above) — without it opencode blocks on per-edit prompts.
- **Run it in the background.** A multi-file task takes minutes; launch with `run_in_background:
  true` and wait for the completion notification rather than polling.
- **Output capture is unreliable; the filesystem is the truth.** opencode's TUI renders to a
  pseudo-terminal that does NOT flush to the piped output file until it exits — the captured stdout
  is often empty mid-run and only partially populated at the end. To check progress, look at
  `git status` / the files it was asked to create, not the output file.
- **Give it a design-locked, self-contained brief.** It works best when the design is already
  decided and the brief is precise: repo facts (how to run tests/lint/types), the exact style
  rules, the files to read first, a numbered spec of what to change, and the verification commands
  to run. Tell it explicitly NOT to commit (leave changes in the working tree) since the user
  handles git here.
- **You own the review gate regardless of who wrote the code.** Do not trust opencode's
  self-reported "all green." Independently re-run ruff + basedpyright + pytest, read the diff for
  style/correctness, and do real end-to-end verification (opencode tends to run unit tests + a
  smoke check but skip true e2e). It performed well on a well-specified, design-locked task; keep
  ambiguous or design-sensitive work in-house where the review loop is tighter.

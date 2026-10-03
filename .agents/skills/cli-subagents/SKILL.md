---
name: cli-subagents
description: Delegate a task to another coding-agent CLI — Claude Code (`claude`), OpenCode (`opencode`), or Google Antigravity (`agy`) — running headlessly as a subagent, to reach a different model family or subscription from inside the current agent. Use when the user wants a second opinion or cross-model review, asks to have Claude, Gemini, Antigravity, GPT, ChatGPT, OpenCode or agy look at or do something, wants to use their Google (Antigravity), Claude or ChatGPT subscription from this session, wants a huge codebase read with Gemini's 1M-token context, or wants answers compared across models — even if they never say "subagent".
---

# CLI Subagents

Run `claude`, `opencode` or `agy` non-interactively through `scripts/delegate.sh` (in this skill's
directory). The script applies each CLI's safe flags, prepends ground rules for a non-interactive
run, and prints only the final answer plus a session ID, so the other agent's transcript doesn't
flood your context.

## Pick the CLI

| CLI | Bills | Models | Pick it for |
| --- | --- | --- | --- |
| `claude` | Claude Pro/Max subscription | `opus`, `sonnet`, `haiku` | Claude-quality coding and review from another harness |
| `opencode` | Whatever providers opencode is logged into, e.g. a ChatGPT subscription | `opencode models` | GPT models, or any provider opencode has configured |
| `agy` | Google AI Pro/Ultra subscription (Antigravity) | `agy models`: Gemini 3.x, plus Claude Opus/Sonnet and GPT-OSS on the Google plan | Gemini's 1M-token context, or a second opinion billed to Google |

Don't delegate to the CLI you are already running in: your own native subagents are cheaper and
share your session. Run `<cli> --version` first if you're unsure it's installed — the script exits
127 when it isn't.

## Run it

```bash
<skill-dir>/scripts/delegate.sh <claude|opencode|agy> [--write] [--model MODEL] [--resume ID] [--cd DIR] <<'EOF'
<task>
EOF
```

Output:

```text
<final answer>

[delegate] cli=agy session=0864b371-...
[delegate] denied: write_file
```

The `denied:` line appears only when the subagent was blocked from something. A failed run exits
non-zero with the error on stderr.

## Write the task for a cold start

The subagent has none of your context. State the goal, the relevant paths, the constraints, what
"done" looks like, and the shape of the answer you want back — a vague task produces vague work.
The script already tells it that it runs unattended, must not delegate further, and should end with
a report, so don't repeat that.

## Read-only unless the user wants changes

| CLI | Default (read-only) | `--write` |
| --- | --- | --- |
| `claude` | plan mode: reads, no edits or shell | `acceptEdits`: edits files; shell commands are still denied unless the user's settings allow them |
| `opencode` | `plan` agent | `build` agent: edits files **and runs shell commands without asking** |
| `agy` | plan mode | `accept-edits`: edits files; other actions are denied |

Pass `--write` only when the user wants the other agent to change files. Two agents editing one
working tree clobber each other, so point the subagent at a separate git worktree (`--cd <path>`) or
pause your own edits until it finishes. Afterwards, read its diff yourself (`git diff`) before
reporting — its summary is a claim, not evidence.

A `denied:` line means part of the task didn't happen. Tell the user what was blocked rather than
silently escalating permissions.

## Follow up and choose models

- `--resume <session>` continues the same conversation with its context; the footer gives the ID.
- `--model`: `claude` takes `opus`/`sonnet`/`haiku` or a full model ID; `opencode` takes
  `provider/model#variant` (list with `opencode models`); `agy` takes an ID from `agy models`, such as
  `gemini-3.1-pro-high` or `claude-opus-5-5-high`. Without it, each CLI uses its configured default.
- `--cd DIR` runs the subagent in another directory; the CLIs work in their current directory, and
  `opencode run` has no directory flag of its own.

## Long tasks

A delegated run takes from seconds to many minutes, and your shell tool may time out first (Claude
Code's Bash defaults to two minutes). For anything beyond a quick question, run it in the background
with output redirected to a file, and read the file when the run finishes:

```bash
<skill-dir>/scripts/delegate.sh agy < task.md > review.txt 2>&1 &
```

## Report back

Say which CLI and model answered. Treat the answer as a second opinion to check against the code,
not as ground truth — especially when it disagrees with you.

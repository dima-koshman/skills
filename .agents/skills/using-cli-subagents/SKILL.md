---
name: using-cli-subagents
description: >
  Use when delegating a self-contained task to an external AI agent CLI — codex or opencode (via a
  ChatGPT subscription) or agy (Gemini / Claude / GPT-OSS via a Google AI Pro subscription) — for a
  second opinion, cross-checking a tricky result, when a non-Claude model is better suited, or to
  have another model implement file edits autonomously. Claude acts as the main orchestrator;
  subagents handle well-scoped implementation or verification tasks. Covers non-interactive
  commands, the --dangerously-skip-permissions authorization gate, self-contained prompts, session
  continuation, background runs, and the review gate on subagent-written code.
---

# Using External Agent CLIs as Subagents

## Philosophy

Claude (you) is the **orchestrator**. Your Claude usage should go toward reasoning, planning, and
review — not grinding out boilerplate or implementation that a cheaper model can handle. Delegate
self-contained, well-scoped tasks to subagent CLIs that ride the user's existing subscriptions
instead of burning Claude tokens:

| CLI | Path | Subscription | Lab | Non-interactive entry |
|-----|------|-------------|-----|-----------------------|
| `codex` | `/opt/homebrew/bin/codex` | ChatGPT | OpenAI (codex) | `codex exec` |
| `opencode` | `/opt/homebrew/bin/opencode` | ChatGPT | OpenAI | `opencode run` |
| `agy` | `~/.local/bin/agy` | Google AI Pro | Gemini / Claude / GPT-OSS | `agy -p` |

> **Models are not pinned here.** Each CLI picks its model from its own config — for opencode that's
> the project's `.opencode/opencode.jsonc` (or global `~/.config/opencode/opencode.json`); for codex
> it's `~/.codex/config.toml`; for agy its default model. Pass a `--model`/`-m` override only when you
> deliberately want a different one. Don't hardcode a specific model version in commands or briefs.

Pick the CLI/lab that fits the task:
- **Large / design-locked implementation** → **prefer `codex`** (`codex exec`). In this repo's
  testing it completed a large file-writing+verify task reliably (~2 min) where `opencode` **hung**
  on the same class of task (see Reliability below).
- **Second opinion / cross-check** → use a different lab than Claude (Gemini via `agy`; OpenAI
  via `codex`/`opencode`).
- **Quick one-shot answer** → `opencode run` is fast for short, no-tool prompts.
- **Parallel fan-out** → launch multiple background runs across the CLIs simultaneously.

## Quick Reference

### codex (OpenAI, via ChatGPT) — preferred for large / implementation tasks

```bash
codex exec --dangerously-bypass-approvals-and-sandbox "<self-contained prompt>" < /dev/null
```

| Flag | Purpose |
|------|---------|
| `exec` | Non-interactive subcommand (one prompt → run → exit). |
| `--dangerously-bypass-approvals-and-sandbox` | Auto-approve + no sandbox (full access; needs user sign-off — see the authorization gate). Prefer `--sandbox workspace-write` to confine writes to the repo. |
| `-m <model>` | Override the model. |
| `-C, --cd <dir>` | Working root. |
| `--json` | Emit JSONL events. |
| `-o, --output-last-message <file>` | Write the final message to a file. |
| `exec resume --last` / `exec resume <id>` | Continue a previous session. |

**`< /dev/null` is mandatory** for non-interactive/background runs: without it codex prints
"Reading additional input from stdin..." and **hangs forever** waiting on stdin (it would append
piped stdin as a `<stdin>` block). Redirecting from /dev/null gives an immediate EOF.

Docs: <https://developers.openai.com/codex/>

### opencode (OpenAI, via ChatGPT)

```bash
opencode run --variant high --dangerously-skip-permissions "<self-contained prompt>"
```

The model comes from the project's `.opencode/opencode.jsonc` (or global `~/.config/opencode/opencode.json`) —
don't pass `--model` unless you deliberately want to override it.

| Flag | Purpose |
|------|---------|
| `--model <provider/model>` | Override the model. Omit to use the project/global opencode config. |
| `--variant high` | Reasoning effort (`minimal`, `high`, `max`). |
| `--dangerously-skip-permissions` | Required for any non-interactive run (see below). |
| `--format json` | Emit parseable events; carries a server-generated `sessionID` (`ses_...`). |
| `-c` | Continue the most recent session. |
| `--session <id>` | Continue a specific session by id (from a prior run's JSON). |

Docs: <https://opencode.ai/docs/>

### agy (Gemini / Claude / GPT-OSS via Google AI Pro)

```bash
agy -p "<self-contained prompt>" --dangerously-skip-permissions
```

| Flag | Purpose |
|------|---------|
| `-p` / `--print` | Non-interactive mode: run one prompt, print response, exit. |
| `--dangerously-skip-permissions` | Auto-approve all tool calls (see below). |
| `--model "<name>"` | Override the default model (agy uses labelled variants, e.g. `"Gemini Pro (High)"`). |
| `--print-timeout <dur>` | Wait timeout for print mode (default 5m). |
| `-c` / `--continue` | Continue the most recent conversation. |
| `--conversation <id>` | Resume a previous conversation by id. |
| `--sandbox` | Enforce sandbox isolation (nsjail on Linux, sandbox-exec on macOS). |
| `--log-file <path>` | Write logs to a file for debugging. |
| `--add-dir <path>` | Add a directory to the workspace (repeatable). |

**Known issue:** `agy -p` may drop stdout in non-TTY contexts on Windows or older versions
(< 1.0.6). This did NOT reproduce on macOS with agy 1.0.12 — piping to `cat`, capturing stdout,
and background runs all work cleanly. If you do hit empty output, wrap with a pseudo-TTY
(`script -qec 'agy -p "..."' /dev/null`) or check the transcript at
`~/.gemini/antigravity-cli/log/cli-*.log`. Tracked in
[issue #76](https://github.com/google-antigravity/antigravity-cli/issues/76).

## Reliability, timeouts & stdin (observed 2026-06 — apply to every run)

- **Always wrap the run in `timeout`.** None of these CLIs have a dependable idle-timeout
  (`opencode run` has **no** timeout flag at all). `opencode` was observed to **hang indefinitely**
  on a large task — the gpt-5.5 stream opened, then went silent ~49 min at ~0% CPU (a stalled HTTP
  stream, no keepalive). Fail fast, then retry once or fall back: `timeout 300 <cli> … || echo stalled`.
- **Always redirect stdin: `< /dev/null`.** `codex exec` blocks on "Reading additional input from
  stdin..." in non-TTY/background; `< /dev/null` fixes it. Harmless for the others — apply to all.
- **`codex` > `opencode` for large tasks (observed).** Same large file-write+verify task: `codex
  exec … < /dev/null` finished clean in ~2 min (even ran the example code); `opencode` hung. Use
  codex first for substantial implementation; keep opencode for quick one-shots / a 2nd GPT lab.
- **opencode is fine for small/simple tool tasks** non-TTY (verified: writes a file in ~30 s, no TTY
  needed) — its failure mode is task size / long generation, not tool-use or TTY.
- **Filesystem is truth.** stdout flushes only on exit. Check created files / `git status` for
  progress, not the (empty) live output. opencode log: `~/.local/share/opencode/log/opencode.log`.
- **Big briefs stall more.** Split large delegations into smaller pieces, or lower the reasoning effort.

## The authorization gate (read first)

Each CLI needs an auto-approve flag for non-interactive runs, or it pauses for per-tool-call
approval and stalls a piped/background run waiting for input that never comes:
`--dangerously-skip-permissions` (opencode, agy) /
`--dangerously-bypass-approvals-and-sandbox` (codex; or the safer `--sandbox workspace-write` to
confine writes to the repo).

The Claude Code auto-mode classifier BLOCKS this flag unless the user has authorized it — **get
explicit user sign-off first.** It's their call, since the flag disables the subagent's own safety
gates. Once authorized, it applies to read-only second-opinion runs too, not just file-editing ones.

## Output capture quirks

- **opencode** emits TUI artifacts in plain mode (e.g. `> build · gpt-5.5`, `Patch 1 file`) —
  these are not part of the model's answer. Use `--format json` when you need parseable output;
  the `text` events contain the clean response. Session id is in the `sessionID` field of every
  JSON event.
- **agy** output is clean on macOS (1.0.12) but may include `file://` URI links and a
  "Summary of Work" section after the answer — strip these when relaying results.
- For both CLIs, stdout is only available after the process exits. Do not poll mid-run; check
  `git status` / created files for progress instead.

## Writing the prompt

- The prompt MUST be fully self-contained. Subagents do NOT see this conversation's context —
  paste in any code, file contents, or background they need.
- Both CLIs run from the current working directory and can read project files, so you may reference
  paths instead of pasting when the file is in-repo.
- Capture stdout and integrate/relay the result; note clearly when an answer came from a subagent
  vs. from you.

## Continuing a session

Both CLIs support session continuation:
- **opencode:** add `-c` (most recent) or `--session <id>` (from a prior run's JSON). Use
  `--format json` to capture the session id.
- **agy:** add `-c` / `--continue` (most recent) or `--conversation <id>`.

## Delegating implementation work (file edits), not just answers

Both CLIs can implement features — they edit files directly in the working tree, run commands, and
self-verify. Lessons from doing this:

- **Permissions.** Editing autonomously needs `--dangerously-skip-permissions` (see the
  authorization gate above) — without it the subagent blocks on per-edit prompts.
- **Run it in the background, wrapped in `timeout`, with `< /dev/null`.** A multi-file task takes
  minutes; launch with `run_in_background: true` and wait for the completion notification rather
  than polling. Always `timeout 300 <cli> … < /dev/null` — these CLIs can hang indefinitely (see
  Reliability above). On timeout, retry once or fall back to native/another CLI.
- **Output capture is unreliable mid-run; the filesystem is the truth.** Both CLIs flush stdout
  only on exit — the captured output is empty mid-run and partially populated at the end. To
  check progress, look at `git status` / the files it was asked to create, not the output file.
  See also the output capture quirks section above for per-CLI noise patterns.
- **Give it a design-locked, self-contained brief.** Subagents work best when the design is already
  decided and the brief is precise: repo facts (how to run tests/lint/types), the exact style
  rules, the files to read first, a numbered spec of what to change, and the verification commands
  to run. Tell it explicitly NOT to commit (leave changes in the working tree) since the user
  handles git here.
- **You own the review gate regardless of who wrote the code.** Do not trust a subagent's
  self-reported "all green." Independently re-run ruff + basedpyright + pytest, read the diff for
  style/correctness, and do real end-to-end verification (subagents tend to run unit tests + a
  smoke check but skip true e2e). They perform well on well-specified, design-locked tasks; keep
  ambiguous or design-sensitive work in-house where the review loop is tighter.

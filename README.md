# skills

Personal skill collection for AI coding agents. Each skill lives in `.agents/skills/<name>/SKILL.md`
and is loaded on demand by any agent that supports the `SKILL.md` standard (Claude Code, Codex,
opencode, …). This repo is the **single source of truth** — `npx skills add` copies skills into each
agent's directory. Run `npx skills update` after editing a skill to propagate changes.

## Engineering knowledge with OpenWiki

The Markdown notes in [`wiki/`](wiki/) are the maintained sources. OpenWiki reads only
those notes and its own output, as configured by [`.openwikiignore`](.openwikiignore)
and [`openwiki/INSTRUCTIONS.md`](openwiki/INSTRUCTIONS.md). Source notes can be
plain Markdown without YAML frontmatter, generated indexes, or maintenance logs.
OpenWiki generates its output separately under `openwiki/`. The old OKF skills,
index generators, and HTML renderer are retired.

For a reversible return to manual curation, see the
[manual OKF restoration guide](docs/manual-okf-restoration.md), including the last
committed snapshot, generation commands, and visualization setup.

Use the workspace's **OpenWiki: update CLI**, **OpenWiki: init**, **OpenWiki: update**,
and **OpenWiki: visualize** tasks. Initialize once; a fresh `--init` replaces generated
pages, while an interrupted init resumes its checkpoint.
Routine `openwiki --update` runs use OpenWiki's saved provider and model independently
of the coding agent. Review and commit generated changes after each update.

The pre-push hook runs `openwiki --update --print` when a push changes source notes,
the generation instructions, or the ignore configuration. Install hooks with the
**Pre-commit: install** task. This run consumes model tokens and requires provider
access. Initialize the wiki before the first push. If generation changes tracked
files, pre-commit blocks the push; review and commit the output before retrying.
Also check for newly generated untracked files with `git status` before pushing;
pre-commit's modification check does not cover those. The hook never commits output.

The legacy GitHub Pages deployment is retired with its renderer. Use
`openwiki visualize openwiki` locally after generating the wiki.

### Decisions and operating boundaries (2026-10-03)

- **Keep sources separate from generated output.** The two former manual OKF
  bundles became 58 plain Markdown notes under `wiki/ai-engineering/` and
  `wiki/software-engineering/`. We removed their YAML frontmatter, two generated
  indexes, and two maintenance logs, preserving titles, summaries, reference URLs,
  dated context, and relative links. `wiki/` was renamed from `okf/`; it is not an
  OKF input-format requirement. Legacy project skills, generators, tasks, hooks,
  and the custom-renderer Pages deployment were removed. This did not uninstall
  separately published global skill copies.
- **Use the standalone CLI for predictable model selection.** It uses OpenWiki's
  configured provider/model independently of whichever coding harness is open.
  Agent-integrated generation instead uses the host's model and available tools.
  CLI generation is not inherently more reliable: this session encountered real
  provider and recovery failures. The successful init used `gpt-5.6-luna`.
- **Keep the brief supplemental.** `openwiki/INSTRUCTIONS.md` supplies subject
  scope, organization, and evidence preferences. OpenWiki appends it to its own
  planning instructions and passes relevant preferences to page workers. Its
  built-in prompts own the output format, Claims, and maintenance flow; we do not
  need to pin an OKF version in the brief. `.openwikiignore` scopes repository
  reading to the source notes and OpenWiki output/control files.
- **Research sources before regeneration.** In the inspected OpenWiki 0.7.0
  repository pipeline, workers have no web search or URL-fetch tool, and provider
  web search is not enabled. A URL in a note is a reference, not fetched evidence.
  Refresh source notes with a browsing-capable agent, then run `--update`.
  Personal mode has a separate Tavily web-search ingestion connector; repository
  updates do not use it. Searches found no dedicated repository-mode browsing
  request; related requests are [connector mode isolation #444](https://github.com/langchain-ai/openwiki/issues/444)
  and [extensible task plugins #271](https://github.com/langchain-ai/openwiki/issues/271).
- **Distinguish automatic triggers from successful maintenance.** The scoped
  pre-push hook is configured, but manual updates are preferable while assessing
  reliability and token costs. OpenWiki itself created
  [the GitHub Actions workflow](.github/workflows/openwiki-update.yml) during init:
  it schedules 08:00 UTC / 12:00 Baku updates and creates a PR. Its generated
  ChatGPT-login configuration does not supply unattended credentials. Local login
  does not authenticate a GitHub runner; CI authentication remains to be arranged.

### Run state and failures observed

Repository generation stores its interrupted-run checkpoint in
`openwiki/.run.json`, last-run metadata in `openwiki/.last-update.json`, page
baselines in `openwiki/.page-manifest.json`, and Claim records under
`openwiki/.claims/`. A matching `--init` or `--update` resumes a checkpoint; a
different mode is rejected. Without a checkpoint, init starts fresh and update
uses existing knowledge and its baselines. Successful finalization removes the
active checkpoint. The brief is preserved during fresh initialization.

“Restore” in an error means rolling back an individual unsubmitted page, not
necessarily resuming an earlier run. A fresh init can therefore hit the same
restore bug:

- [#871: missing-parent ENOENT during page rollback](https://github.com/langchain-ai/openwiki/issues/871)
  was open when checked. The installed error guard recognizes `file_not_found`
  and “not found”, but misses “ENOENT: no such file or directory”. This failure is
  model-independent and can mask the original worker error. Creating planned
  parent directories reproduced a workaround, but we discarded that workaround
  at the user's request and restarted from a backed-up output directory. Do not
  manually scaffold page directories as the normal workflow.
- [#921: encrypted reasoning rejected through ChatGPT authentication](https://github.com/langchain-ai/openwiki/issues/921)
  was open when checked. Reports include Luna, Sol, and Terra, so changing models
  is not a known fix. Changing provider may avoid that transport, but cannot fix
  filesystem rollback. One fresh attempt also failed with a connection error.
- The user subsequently completed init: metadata records OpenWiki 0.7.0's Luna
  run as `complete` at **2026-10-03 15:10:22 UTC**. Completion is a pipeline status,
  not proof of correct links, complete topic coverage, or factual entailment.

### Review of the first completed generation

Reviewed the 10 generated concept/navigation pages and all 91 Claim statements;
checked evidence references and versions, generated-page hashes, source coverage,
and Markdown file targets. Semantic comparison focused on the source notes and
their qualifications; external websites and current provider prices were not
revalidated, and the visualizer and Mermaid rendering were not exercised.

| Measure | Result |
| --- | --- |
| Source notes | 58; approximately 11,709 whitespace-delimited body words |
| Generated concept/navigation pages | 10; approximately 13,639 body words, excluding YAML and indexes |
| Claims | 91 in 10 JSON sidecars, totaling 136,611 bytes |
| Evidence references | 126; all paths/ranges valid and all stored versions match current evidence using OpenWiki's resolver |
| Generated page hashes | All 10 match their Claim sidecars |
| Directly cited source files | 48 of 58; citation coverage is not proof of complete semantic coverage |
| Broken Markdown file links | 11 occurrences across two pages, also annotated by OpenWiki itself |

The result mostly preserves the source concepts and key caveats: Jev versus the
separately trained CLM, candidate-selection versus independent benchmark solving,
LabEx practice versus production competence, and the unverified Linux Foundation
lesson bookmark. Its thematic organization, cross-topic explanations, diagrams,
and versioned evidence are useful improvements. However, it is an expanded
synthesis, about 16.5% longer than the notes, not a lossless or smaller replacement.

Outstanding findings, in priority order:

1. **Broken navigation survives completion.**
   [Security and observability](openwiki/operations/security-and-observability.md)
   has seven bad link occurrences and
   [distributed systems](openwiki/software-engineering/distributed-systems.md)
   has four. They point to source-note paths as though those notes lived inside
   the generated tree. They need correct links back to `wiki/` or generated
   destinations; placeholder directories are not a fix.
2. **Provider-tool execution is misrepresented in diagrams.**
   [Agent systems](openwiki/architecture/agent-systems.md) routes provider tools
   through harness dispatch and calls harness mediation of every tool effect an
   invariant. [Skills and tooling](openwiki/concepts/skills-and-tooling.md) also
   draws a client-to-hosted-tool execution step. The
   [source note](wiki/ai-engineering/harness/provider-tools.md) says providers
   execute these tools within their API turn; the client enables capabilities
   beforehand and receives results. The generated prose partly preserves this
   distinction, but its universal diagram/control claims do not.
3. **Historical tooling is promoted into current advice.**
   [Knowledge format and visualization](openwiki/concepts/knowledge-format-and-visualization.md)
   recommends the retired `okf_site.py`, speaks of existing v0.1 bundles, and gives
   commands targeting deleted skill directories. Its dated source comparison is
   relevant history, not today's setup. The source notes need explicit retirement
   context before regeneration; the brief already asked for this distinction.
4. **Old OpenWiki source material blurs personal and repository modes.**
   [Quickstart](openwiki/quickstart.md),
   [context and knowledge](openwiki/concepts/context-and-knowledge.md), and
   [maintenance](openwiki/operations/maintenance-and-provenance.md) generalize the
   connector/raw-snapshot pipeline from the
   [older source note](wiki/ai-engineering/context/openwiki.md). This follows that
   note but is misleading for our repository-native Claims workflow. Source
   agreement does not establish current product accuracy.
5. **Claims are useful pointers, not semantic proof or exhaustive coverage.**
   The first [integration Claim](openwiki/.claims/integrations/models-and-protocols.json)
   includes harness authority and termination, but its cited spans describe
   protocols and gateways; it omits the harness source supporting that clause.
   Other pages add extensive operational recommendations beyond their small
   source notes. Matching hashes establish unchanged evidence, not that every
   clause, diagram, or recommendation is entailed. The 10 source files without
   direct Claim references are the five concrete coding-agent notes, peer agents,
   and four individual security-risk notes. Some topics are mentioned indirectly,
   but product distinctions and the richer peer-governance discussion are not
   preserved at the original level of detail.

Compared with the manual OKF, keep OpenWiki as a derived overview and retrieval
layer over the curated notes. The manual collection offered smaller concepts,
direct editorial control, and detailed topic links; OpenWiki adds synthesis,
generated navigation, Claims, and automated change tracking, at the cost of model
runs, larger pages, and additional review. A `verified` stamp should not be read
as independent web verification or human approval. Generated pages and Claims
were left unchanged by this review. These findings are still open; the next
maintenance pass should update stale sources, preserve missing distinctions,
correct the generated links and tool-boundary diagrams, and validate the result
before relying on automatic updates.

## How `npx skills` tracks installed skills

`npx skills` maintains a lock file at the root of each scope:

- **Project scope**: `skills-lock.json` (next to `.agents/skills/`)
- **Global scope**: `~/.agents/.skill-lock.json`

Each entry records the source repo, skill path, and a content hash. `npx skills update` re-fetches
the source, compares hashes, and re-copies only changed skills. `npx skills list` reads the lock
file to show what's installed and where. `npx skills remove` deletes the skill files and the lock
entry.

Skills installed from a **local path** (like `.agents/skills/`) are tracked with `sourceType:
"local"`. `npx skills update` re-copies from the local path, so edits to the source are picked up on
the next update.

## Making these skills global (all agents)

Agents discover global skills from per-tool directories. [`npx skills`](https://github.com/vercel-labs/skills)
copies each skill into a canonical location in `~/.agents/skills/` (shared by OpenCode + Codex),
then symlinks from there to `~/.claude/skills/` for Claude Code:

| Agent | `--agent` flag | Global skills dir |
| ----- | -------------- | ----------------- |
| Claude Code | `claude-code` | `~/.claude/skills/` (symlink → `~/.agents/skills/`) |
| Codex | `codex` | `~/.agents/skills/` (universal) |
| opencode | `opencode` | `~/.agents/skills/` (universal) |

### One-shot setup

Run the **"Skills: install local (all)"** VS Code task (`.vscode/tasks.json`), or:

```bash
npx skills add ./.agents/skills --agent claude-code --agent opencode --agent codex --global --yes
```

This copies every `.agents/skills/<name>/` dir into `~/.agents/skills/` and symlinks from there to
`~/.claude/skills/`. Use `npx skills list` to see installed skills, `npx skills update` to
re-copy after editing a skill, and `npx skills remove` to uninstall.

## Installing third-party skills

```bash
# Search the registry
npx skills find superpowers

# Install from GitHub (owner/repo shorthand)
npx skills add pydantic/skills              # interactive selection
npx skills add obra/superpowers --global    # all superpowers skills, globally

# Install a specific skill
npx skills add obra/superpowers@systematic-debugging --global
```

Third-party skills are installed the same way — copied to `.agents/skills/` (project) or
`~/.agents/skills/` (global) and tracked in the lock file for updates.

## Spec-driven development tools (on the radar, not adopted)

Deliberately **not** installed. The superpowers chain (`brainstorming` → `writing-plans` →
`subagent-driven-development` → `requesting-code-review`) already covers prompt-only spec/plan/execute
on plain files, with no runtime binary. Revisit these only if a project needs *stricter* specs —
enforced validation, dependency-ordered artifacts, delta/archive traceability — which prompts can
describe but can't guarantee:

- **[OpenSpec](https://github.com/Fission-AI/OpenSpec)** — its `openspec-*` skills are just a prompt
  layer that shells out to the `openspec` CLI (`allowed-tools: Bash(openspec:*)`); the validation and
  delta/archive logic lives in the binary. Skills without the CLI are non-functional, so adopting it
  means `npx openspec@latest init` per project, ceremony included.
- **[Spec Kit](https://github.com/github/spec-kit)** — `specify init` scaffolds slash-command prompts
  once, then `/speckit.specify|plan|tasks|implement` run in-agent on markdown (no runtime binary).
  Closer to "SDD as prompts + files," but heavier ceremony than superpowers.

Skip **BMAD-METHOD** for this purpose (full runtime engine, needs Node + Python + uv).

## Project-scoped skills

Skills in `.agents/skills/` are read by all agents at the project level (Claude, Codex, opencode).
This is where our own skills live, alongside any third-party skills installed without `--global`.

## Per-tool docs

- Claude Code — `~/.claude/skills/`, project `.claude/skills/`
- opencode — <https://opencode.ai/docs/skills/>
- Codex — <https://developers.openai.com/codex/skills>

## Personal preferences

Hook for direnv:

```sh
eval "$(direnv hook zsh)"
```

Aliases for common commands:

```sh
alias ga='git add .'
alias gs='git status'
alias gp='git pull'
alias gm='git checkout main'
alias da='direnv allow'
```

Alias for preferred IDE launcher ():

```sh
alias ide='"/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code" --new-window'
```

Aliases to open a whole project group at once — one IDE window per folder, since the launcher opens each
folder argument in its own window:

```sh
alias ide-main='ide ~/Projects/consul-config-loader ~/Projects/dima'
alias ide-mcp='ide ~/Projects/mcp/bir_mcp ~/Projects/mcp/bir_mcp-gateway ~/Projects/mcp/bir_mcp-servers ~/Projects/mcp/bir_mcp-ui'
alias ide-sanitizer='ide ~/Projects/sanitizer/pii-sanitizer-evaluation ~/Projects/sanitizer/pii-sanitizer-ner ~/Projects/sanitizer/sanitizer'
alias ide-skills='ide ~/Projects/skills/*/'
```

Alias for uv run python - mostly for coding agents.

```sh
alias python='uv run python'
```

Disable macOS quarantine for Homebrew casks (which causes macOS to prompt for confirmation when opening apps on each update):

```sh
export HOMEBREW_CASK_OPTS="--no-quarantine"
```

### Pinned files in VS Code

Keep these frequently edited host config files pinned as editor tabs (right-click tab → Pin, or
`cmd+K shift+enter`), so they are one click away in any window:

- `~/.zshrc`
- `~/.zshenv`
- `~/.claude/settings.json`
- `~/Library/Application Support/Claude/claude_desktop_config.json`
- `~/.config/git/ignore`

Pins are per-window workspace state (not settings), so they are not synced by the
"Sync: VSCode settings and tasks to Code User" task and must be re-pinned once per workspace.

`~/.config/direnv/env/` is also worth keeping at hand, but VS Code cannot pin a directory. Instead,
add it as an extra workspace folder — File → Add Folder to Workspace — which shows the whole
directory tree in the Explorer sidebar. Alternatively open all of its files at once from a terminal:

```sh
code --reuse-window ~/.config/direnv/env/*.env
```

## Voice chat with Claude through Siri

Say **"Hey Siri, Ask Claude"** to start a spoken conversation with Claude Code: you talk, it answers out loud,
and it keeps listening for follow-ups. Each turn runs headless Claude Code from your home folder, in auto
mode, so it can run commands and edit files to act on what you ask. Its safety classifier blocks risky actions,
and it is told to confirm before deleting, sending, installing or changing settings.

How it fits together:

- The **Ask Claude** shortcut loops: Dictate Text → `voice_chat.sh` → Speak Text.
- [`scripts/voice_chat.sh`](scripts/voice_chat.sh) runs one turn. Turns less than 10 minutes apart continue one
  Claude session, so you can pick a conversation back up with another "Hey Siri, Ask Claude".
- Say **"stop"**, **"goodbye"**, **"that's all"** or **"never mind"** (or stay silent) to end it, and
  **"new conversation"** to start over.

Setup on a new Mac:

1. Run the **Setup: link scripts and IDE to ~/.local/bin** task, which puts `voice_chat.sh` on a stable path.
2. In Shortcuts → Settings → Advanced, turn on **Allow Running Scripts**.
3. Run the **Setup: install Ask Claude Siri shortcut** task and click **Add Shortcut** in the dialog. If an
   **Ask Claude** shortcut already exists, delete it first: a duplicate comes in as "Ask Claude 2", which
   Siri won't match.
4. In System Settings → Apple Intelligence & Siri, turn on Siri and "Listen for 'Siri' or 'Hey Siri'".

The `shortcuts` CLI can't create shortcuts, so
[`scripts/install_ask_claude_shortcut.py`](scripts/install_ask_claude_shortcut.py) builds the shortcut file
itself, signs it with `shortcuts sign`, and opens it to import.

Tuning, via environment variables in the shortcut's Run Shell Script action: `VOICE_CHAT_MODEL` (default
`sonnet`, chosen for speed), `VOICE_CHAT_RESUME_MINUTES` (default 10). To test a turn without Siri, run
`printf 'What time is it?' | voice_chat.sh`. Expect 4–7 seconds per turn, and you can't interrupt a reply
while it is being spoken.

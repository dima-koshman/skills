# skills

Personal skill collection for AI coding agents. Each skill lives in `.agents/skills/<name>/SKILL.md`
and is loaded on demand by any agent that supports the `SKILL.md` standard (Claude Code, Codex,
opencode, …). This repo is the **single source of truth** — `npx skills add` copies skills into each
agent's directory. Run `npx skills update` after editing a skill to propagate changes.

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

Alias for preferred IDE launcher:

```sh
alias ide="/Applications/Devin.app/Contents/Resources/app/bin/devin-desktop"
```

Alias for uv run python - mostly for coding agents.

```sh
alias python='uv run python'
```

Disable macOS quarantine for Homebrew casks (which causes macOS to prompt for confirmation when opening apps on each update):

```sh
export HOMEBREW_CASK_OPTS="--no-quarantine"
```

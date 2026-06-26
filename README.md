# skills

Personal skill collection for Claude Code. Each skill lives in `skills/<name>/SKILL.md` and is
auto-discovered when symlinked into `~/.claude/skills/`.

## Injecting skills into Claude Code

Claude Code discovers skills from `~/.claude/skills/<skill-name>/SKILL.md` (user-level) or
`.claude/skills/<skill-name>/SKILL.md` (project-level). To expose these skills globally without
copying files, symlink each skill directory into `~/.claude/skills/`:

```bash
ln -sf "$PWD/skills/portfolio"               ~/.claude/skills/portfolio
ln -sf "$PWD/skills/python-styleguide"       ~/.claude/skills/python-styleguide
ln -sf "$PWD/skills/using-cli-subagents"     ~/.claude/skills/using-cli-subagents
```

Or run the **"Symlink skills to Claude"** VS Code task (`.vscode/tasks.json`) to do all of them at
once.

Symlinking keeps the repo as the single source of truth — edits are picked up live by Claude Code
with no restart needed.

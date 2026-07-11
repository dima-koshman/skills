---
name: development-best-practices
description: Cross-project local development hygiene and preferences — git branch/worktree cleanup, and other day-to-day dev workflow conventions. Use when asked to clean up local git branches, prune merged/deleted branches, tidy worktrees, or when setting up recurring local-dev maintenance.
---

# Development Best Practices

Shared local-development hygiene and workflow preferences across internal projects.
Ships small, host-agnostic helper scripts under `scripts/`.

## Prune merged/deleted local branches

Over time, local branches pile up after their PRs/MRs are merged and the remote
branch is deleted. Delete them with:

```bash
bash scripts/prune-merged-branches.sh            # delete gone branches
bash scripts/prune-merged-branches.sh --dry-run  # preview only
```

**Agent safety rule: always `--dry-run` first, then eyeball the list before the real run.**
`-D` is a force delete, so git's "refuse unmerged" guard is off by design (needed to catch
squash-merges). The `[gone]` marker means "remote branch was deleted after prune" — in the normal
workflow (create local branch → push → merge & delete on the host, no renames, no extra local
commits after merge) that always equals "safely merged." But if the dry-run list contains anything
you don't recognize as a merged feature branch — a branch you never pushed, one with local-only
work, or an unexpectedly large set (a sign the remote was renamed/removed) — **stop and confirm
with the user** instead of deleting. Deletions are recoverable via `git reflog` for a while.

Key facts:

- **Reliable signal is `[gone]`, not `--merged`.** `git branch --merged main` misses
  **squash-merged** branches (no commit-ancestry link). The script instead runs
  `git fetch --prune` and deletes any local branch whose upstream is `[gone]` — the
  marker git sets once the remote-tracking ref is pruned.
- **Host-agnostic.** Uses only git plumbing (no `gh`/`glab`/API calls), so it works
  with GitHub, GitLab, Bitbucket, or any remote unchanged.
- Skips the current branch and prunes stale worktrees afterward.
- Deletions are recoverable via `git reflog` for a while.

### Wiring it into a project

Reference the script by absolute path from a project so it stays version-controlled
here rather than copied into each repo.

- **VSCode task** (`.vscode/tasks.json`):
  ```json
  {
    "label": "Prune merged branches",
    "command": "bash /Users/dima/Projects/skills/.agents/skills/development-best-practices/scripts/prune-merged-branches.sh"
  }
  ```
- **Git alias** (terminal convenience, per-clone):
  ```bash
  git config alias.prune-gone '!bash /Users/dima/Projects/skills/.agents/skills/development-best-practices/scripts/prune-merged-branches.sh'
  # then: git prune-gone   (or: git prune-gone --dry-run)
  ```

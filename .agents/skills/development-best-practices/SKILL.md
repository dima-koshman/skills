---
name: development-best-practices
description: Cross-project local development hygiene and preferences — the worktree-to-main workflow, git branch/worktree cleanup, VS Code task conventions, and other day-to-day dev workflow conventions. Use when starting feature work in a worktree, finishing a branch, merging to main, pushing to main, monitoring or fixing a GitHub Actions run after a push, cleaning up local git branches, pruning merged/deleted branches, tidying worktrees, creating or renaming VS Code tasks, updating OpenCode plugins, setting or changing a container's timezone in a Dockerfile or deployment, or setting up recurring local-dev maintenance.
---

# Development Best Practices

Shared local-development hygiene and workflow preferences across internal projects.
Ships small, host-agnostic helper scripts under `scripts/`.

## Name VS Code tasks consistently

Prefer `<Category>: <action>` labels so related tasks group together in the command palette and
quick-pick lists. Use a stable, capitalized tool or domain category such as `Pytest:`, `Git:`,
`Docker:`, or `Setup:`.

Name a package's full pytest suite `Pytest: <project-or-package>`. Add a suffix only for a narrower
scope such as `unit`, and name a workspace-wide aggregate `Pytest: all packages`:

```json
{
  "label": "Pytest: sanitizer-core",
  "command": "uv run pytest packages/sanitizer-core/tests"
}
```

Hoist properties shared by every task to the root of `tasks.json` instead of repeating them. This
commonly applies to `type`, `problemMatcher`, and `presentation`:

```json
{
  "version": "2.0.0",
  "type": "shell",
  "problemMatcher": [],
  "tasks": [
    {
      "label": "Pytest: sanitizer-core",
      "command": "uv run pytest packages/sanitizer-core/tests"
    }
  ]
}
```

Do not add `group` unless the project intentionally uses VS Code task groups or default tasks. The
category prefix already organizes labels in task pickers; an unused `group` field adds configuration
without changing the team's workflow.

When renaming a task, update every `dependsOn` reference in the same edit; VS Code resolves
dependencies by the literal label and does not report stale references until the task runs.

## Update OpenCode plugins

OpenCode has no bulk plugin-update command. From the project root, read every external plugin entry
from `.opencode/opencode.jsonc` and force-install each string spec individually. For a tuple entry,
use its first element as the spec; preserve its options. Explicit version, tag, and commit pins do
not move automatically, so change the configured pin first when an upgrade is intended.

```bash
opencode plugin --force "<plugin-spec>"
```

Quit and restart OpenCode afterward because plugins are loaded at startup. For npm plugins, check
the matching cached package's `package.json` against the registry version; for git-backed plugins,
check the cache package lock's resolved commit against the configured ref. OpenCode can retain stale
versions despite `--force`. If that happens, quit OpenCode, identify and remove only that plugin's
exact directory under `~/.cache/opencode/packages/`, then restart OpenCode to reinstall it.

## Finishing work in a worktree

Worktrees are created by the user, via the **"Git: create worktree and open in IDE"** VSCode task.
Creating one is not your job — but knowing you are in one is, because it changes how work gets
integrated.

Check at the point you finish a piece of work:

```bash
[ "$(git rev-parse --path-format=absolute --git-dir)" != \
  "$(git rev-parse --path-format=absolute --git-common-dir)" ] \
  && echo "linked worktree" || echo "primary checkout"
```

If you are in a linked worktree, prefer landing the work with a local merge into `main` over
opening a PR.

**The agent in the worktree owns the merge.** It did the work, so it is the one that can resolve a
semantic conflict or diagnose a CI failure without re-deriving intent from a diff. Hand off to
whoever holds the primary checkout only when several branches must land together, or when the
worktree session is gone.

1. **Verify first.** Full check suite green in the worktree. Do not start integrating on a red tree.

2. **Check the primary checkout is clean.** Git will not let two worktrees check out `main` at
   once, so the merge runs against the primary checkout's working tree from here. If someone — or
   another agent — has work in progress there, merging into it is destructive.

   ```bash
   MAIN_ROOT="$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")"
   git -C "$MAIN_ROOT" status --porcelain
   ```

   **Agent safety rule: if that prints anything, stop and tell the user. Do not merge into a dirty
   primary checkout.**

3. **Merge locally.**

   ```bash
   git -C "$MAIN_ROOT" merge --no-ff <branch-name>
   ```

   If the merge conflicts, resolve it here — you have the context for it. If `main` has moved in a
   way that makes the merge wrong rather than merely conflicted, say so instead of forcing it.

4. **Ask before pushing.** A local merge is cheap to undo; a push to `main` is not, and it can
   trigger deploys. **Agent safety rule: never push to `main` unprompted — merge locally, report
   what landed, and ask for approval to push.**

5. **Watch CI if the push triggers it.** After an approved push, check whether a workflow actually
   started — workflows are often filtered by branch and by `paths:`, so many pushes legitimately
   trigger nothing. Don't wait on a run that will never exist:

   ```bash
   gh run list --branch main --limit 3
   ```

   If a run started, follow it to completion. `--exit-status` makes the command exit non-zero on
   failure, so it can gate what comes next:

   ```bash
   gh run watch "$(gh run list --branch main --limit 1 --json databaseId --jq '.[0].databaseId')" --exit-status
   ```

   On failure, pull the failing step's logs, fix the cause, and push the fix — a red pipeline on
   `main` is not "done":

   ```bash
   gh run view <run-id> --log-failed
   ```

Leave the worktree directory in place when you are done. Stale directories under `.worktrees/` are
harmless; they get cleaned up in batch (see below), not at the end of each task.

## Working in the primary checkout while worktrees are live

Worktree agents merge into the primary checkout's working tree asynchronously, at a time you do not
control. Check before starting work on `main`:

```bash
git worktree list   # more than one entry => linked worktrees exist
```

**If linked worktrees exist, treat the primary checkout as an integration point, not a workspace.**
Do the work in a worktree instead. If you must work on `main`, commit as you go and never leave the
tree dirty while you wait — an incoming merge only interacts badly with *uncommitted* work.

What git does and does not protect, if a merge lands while you are working:

- A merge that touches a file you have modified **aborts**, leaving `main` where it was. Safe.
- A merge touching only files you have *not* modified **succeeds**. Your changes survive, but
  `main` has moved beneath them: anything you verified is now stale, and your next commit lands on
  a base you never reviewed. Git gives no warning. This is the case to design around.
- Concurrent git commands collide on `index.lock` and fail outright rather than interleaving, so
  you get an error, not a corrupted tree.
- `git branch -f` and `git fetch . <branch>:main` refuse to move a branch that is checked out in
  another worktree.

**Agent safety rule: never use `git update-ref` to move a checked-out branch.** It bypasses every
guard above and leaves the primary worktree's index and files disagreeing with `HEAD` — a state
that looks like unexplained local modifications. Use `git merge` from the checkout that owns the
branch.

If `main` moved under you mid-task, re-run verification before claiming anything passes — the
earlier results describe a tree that no longer exists.

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

### Clean up merged worktrees

`git worktree prune` only drops metadata for directories that are already gone — it never deletes a
worktree that still exists on disk. So worktrees for merged branches accumulate under `.worktrees/`.
That is harmless, and there is no need to tidy up at the end of each task; clear them in batch when
convenient.

List them, then remove the ones whose work has landed:

```bash
git worktree list
git worktree remove .worktrees/<dir>   # add --force if the tree has stray untracked files
```

A branch cannot be deleted while a worktree still has it checked out, so remove the worktree before
running the prune script — otherwise its branch survives as a leftover.

### Wiring it into a project

Reference the script by absolute path from a project so it stays version-controlled
here rather than copied into each repo.

- **VSCode task** (`.vscode/tasks.json`):
  ```json
  {
    "label": "Prune merged branches",
    "command": "bash /Users/dima/Projects/dima/.agents/skills/development-best-practices/scripts/prune-merged-branches.sh"
  }
  ```
- **Git alias** (terminal convenience, per-clone):
  ```bash
  git config alias.prune-gone '!bash /Users/dima/Projects/dima/.agents/skills/development-best-practices/scripts/prune-merged-branches.sh'
  # then: git prune-gone   (or: git prune-gone --dry-run)
  ```

## Container timezone

Containers default to UTC, and the mainstream convention is to leave them there: UTC has no DST,
so no wall time is ever ambiguous or missing, and logs from every service and region line up
without conversion. Setting a local `TZ` is therefore a **deliberate deviation**, not a default —
do not add it to an image reflexively.

Take the deviation for an internal service whose operators all sit in one timezone, where the
console log is read by humans in that zone (a Kubernetes logs tab, `docker logs`) and local wall
time is what they want to match against a report of "it broke around 4pm". Prefer the operators'
zone there — for our projects, `Asia/Baku`:

```dockerfile
# Render console log timestamps in the operators' zone. The base image ships tzdata, so
# /usr/share/zoneinfo/Asia/Baku exists and no package install is needed. Timestamps exported
# over OTLP are unaffected: those are UTC epochs, not local renderings.
ENV TZ=Asia/Baku
```

Five things to settle before doing it, in order:

- **Audit every naive datetime in the codebase.** This is the real hazard, and it is silent.
    `datetime.timestamp()`, `datetime.fromtimestamp()` and `datetime.astimezone()` all resolve a
    naive value against the *process's* zone, so any code that treats a bare timestamp as UTC
    shifts by the offset the moment `TZ` changes — including timestamps written to a store or sent
    to an API. Grep for those three plus `datetime.now()` and `date.today()`, and pin each
    naive-input assumption explicitly (`replace(tzinfo=datetime.UTC)`) before flipping `TZ`, not
    after. A test that only ever passes offset-aware strings will not catch this.
- **Confirm the zone has no DST**, or accept the consequence. `Asia/Baku` has had none since 2016,
    so its offset is a constant `+04`. In a DST zone, one local hour repeats and another does not
    exist each year, which is exactly the ambiguity UTC was protecting against.
- **Always print the offset**, so a line is readable regardless of what the reader assumes. See
    the Rich logging section of the `python-styleguide` skill for the handler-level format.
- **Keep exported telemetry in UTC.** OTLP timestamps are UTC epochs and are not affected by `TZ`;
    do not "fix" that to match the console. The console rendering is a display choice, and the wire
    format should stay absolute.
- **Check tzdata is present.** Debian slim images ship it, so `ENV TZ` alone works; Alpine does not
    — it needs `apk add --no-cache tzdata` or the variable silently does nothing. Verify in the
    built image rather than assuming:

    ```bash
    docker run --rm <image> sh -c 'date; ls /usr/share/zoneinfo/$TZ'
    ```

Do **not** set a local `TZ` on a multi-region service, on anything whose logs are correlated with
another organization's, or on a batch job whose schedule or partitioning is derived from local
midnight. Note also that an image's `ENV TZ` is only a default — a Kubernetes Deployment setting
`TZ` in its own env wins, so check the manifests before concluding the image decides.

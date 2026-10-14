---
name: development-best-practices
description: Cross-project local development hygiene and preferences — the worktree-to-main workflow, git branch/worktree cleanup, VS Code task conventions, direnv/environment-variable layout, and other day-to-day dev workflow conventions. Use when starting feature work in a worktree, finishing a branch, merging to main, pushing to main, monitoring or fixing a GitHub Actions run after a push, cleaning up local git branches, pruning merged/deleted branches, tidying worktrees, creating or renaming VS Code tasks, writing a local helper or dev script (prefer Python over shell), writing or changing a project's `.envrc`, deciding where to keep environment variables or credentials for local development, updating OpenCode plugins, setting or changing a container's timezone in a Dockerfile or deployment, or setting up recurring local-dev maintenance.
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

## Write local and dev scripts in Python, not shell

Write helper scripts (sync and setup tasks, config editors, inventories, anything a VS Code task
runs) in Python. Use stdlib-only `python3` (3.11+ ships `tomllib`), or `uv run --no-project --with
<pkg> python script.py` when a dependency is needed. Keep shell for one-line task commands and
thin wrappers around a single tool.

- Python has real parsers (`json`, `tomllib`, `argparse`) where shell needs `sed`/`awk`/`jq`
  pipelines, and those pipelines break on quoting and on BSD-vs-GNU flag differences on macOS.
- Write config files atomically: write a temp file in the same directory, then `os.replace`. Use
  `Path.resolve()` first so a symlinked config stays a symlink.
- Pass inputs as explicit arguments with visible defaults (`--env-file ~/.config/direnv/env/x.env`,
  wired to a VS Code `inputs` entry). Don't read them silently from the ambient environment: the
  task then shows where values come from, and a stale variable that direnv exported into the
  shell can't leak in.
- Test a script that resolves credentials under `env -i HOME=<fake home> PATH=$PATH`, with dummy
  values, and never print what it generates unmasked.
- Write generated local output (rendered HTML sites, reports, caches) to a git-ignored `/dev/`
  directory at the repo root, never next to the sources. A task that writes there runs
  `mkdir -p dev` first, because the directory doesn't exist in a fresh clone.

Existing shell scripts can stay; port one to Python when you next change it substantially.

## Store env var combinations in ~/.config/direnv/env/

Keep every reusable set of environment variables in its own file under `~/.config/direnv/env/`,
outside any repo, and load it from the project's `.envrc`:

```bash
dotenv_if_exists .env
dotenv_if_exists ~/.config/direnv/env/vault-app-role.env
```

One file per combination, named for what it configures — `<service>.env` for the default set and
`<service>-<environment>.env` for a variant: `litellm.env`, `litellm-dev.env`, `litellm-sandbox.env`,
`openwebui.env`, `vault-app-role.env`. Switching a project between environments then means changing
which line the `.envrc` loads, not editing values in place.

Why this over a project-local `.env`:

- **Credentials never sit in a repo**, so there is nothing for a stray `git add -f` or a
  misconfigured `.gitignore` to leak.
- **One source of truth across clones and worktrees.** Every `.worktrees/<branch>` copy of `.envrc`
  loads the same host file, so a rotated token is updated once, not once per checkout.
- **Combinations compose.** List several lines to stack them; later files win on duplicate keys, so
  order the general set first and the override last.

Rules that matter in practice:

- **Use `dotenv_if_exists`, not `dotenv`.** A missing file is normal on a machine that has not been
  provisioned yet. `dotenv` logs a red `direnv: .env at <path> not found` on every entry into the
  directory and returns non-zero — harmless on its own, but fatal under an `.envrc` that runs
  `set -e`, where the remaining `export`s are silently skipped. `dotenv_if_exists` returns quietly.
- **Keep project-local, non-secret values in the repo's own gitignored `.env`**, loaded first. The
  host files are for credentials and for anything shared between projects.
- **Editing a loaded env file does not need `direnv allow` again.** `dotenv_if_exists` registers the
  file with `watch_file`, so direnv reloads on its next `cd` into the directory. Only changes to
  `.envrc` itself re-trigger the allow prompt.
- **Lock the directory down**: `chmod 700 ~/.config/direnv/env`. It holds plaintext secrets.
- It is not version-controlled by design — back it up with whatever holds your other host secrets.

### Load several environments side by side with `dotenv_prefixed`

Variant files often share variable names (`openwebui.env`, `openwebui-dev.env` and
`openwebui-sandbox.env` all define `OPEN_WEBUI_BASE_URL` and `OPEN_WEBUI_API_KEY`), so
stacking them keeps only the last. When a project needs several at once, for example a
script that picks its target environment from an argument, load each under a prefix
instead. direnv has no built-in prefix option; `dotenv_prefixed PREFIX FILE` provides one:

```bash
dotenv_prefixed PROD    ~/.config/direnv/env/openwebui.env          # PROD_OPEN_WEBUI_API_KEY, ...
dotenv_prefixed DEV     ~/.config/direnv/env/openwebui-dev.env      # DEV_OPEN_WEBUI_API_KEY, ...
dotenv_prefixed SANDBOX ~/.config/direnv/env/openwebui-sandbox.env
```

It parses the file with direnv's own dotenv parser, the same rules as `dotenv`. That
includes `$VAR` expansion inside double-quoted values, so single-quote a literal `$`. It
then re-exports each variable as `PREFIX_<NAME>`, re-quoted with `%q`. The parse runs in a
subshell, so the unprefixed names are never exported. A missing file is skipped like
`dotenv_if_exists`, and the file is registered with `watch_file`. The definition, shipped
as `scripts/dotenv_prefixed.sh`:

```bash
dotenv_prefixed() {
  local prefix=$1 file=$2
  [[ -f "$file" ]] || return 0
  watch_file "$file"
  eval "$(
    eval "$("${direnv:-direnv}" dotenv bash "$file")"
    sed -n -E 's/^[[:space:]]*(export[[:space:]]+)?([A-Za-z_][A-Za-z0-9_]*)=.*/\2/p' "$file" |
      while IFS= read -r name; do
        printf 'export %s_%s=%q\n' "$prefix" "$name" "${!name}"
      done
  )"
}
```

**It may already be available on the host.** direnv sources every
`~/.config/direnv/lib/*.sh` before each `.envrc`, so a copy there makes the function
available in every project with no definition in the `.envrc`. Check with
`declare -F dotenv_prefixed` inside an `.envrc`. Install it by symlinking this skill's
script, so the host copy follows the version-controlled one:

```bash
mkdir -p ~/.config/direnv/lib
ln -sf "$HOME/Projects/dima/.agents/skills/development-best-practices/scripts/dotenv_prefixed.sh" \
  ~/.config/direnv/lib/dotenv_prefixed.sh
```

**A committed `.envrc` template**, such as an `.envrc.example` for teammates, can't assume
the host copy exists. Define the function only when it's missing, so the global copy wins
where installed:

```bash
declare -F dotenv_prefixed >/dev/null || dotenv_prefixed() {
  ...  # the definition above
}
```

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
harmless; they get cleaned up in batch (see "Prune landed worktrees and branches"), not at the
end of each task.

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

## Prune landed worktrees and branches

Worktrees and local branches pile up after their work lands. Clear them in batch when convenient,
between tasks — there is no need to tidy up at the end of each one:

```bash
python3 scripts/prune_merged_branches.py --dry-run  # preview only
python3 scripts/prune_merged_branches.py            # remove landed worktrees, delete landed branches
```

A branch has **landed** when it is merged into the integration branch (whatever the primary
checkout has checked out, normally `main`), or when its upstream is `[gone]`. The script runs
`git fetch --prune`, removes the landed linked worktrees, deletes the landed branches that are no
longer checked out, and finishes with `git worktree prune`. It never touches the primary checkout
or the worktree it runs from.

**Git's own guards do the safety work:**

- `git worktree remove` refuses a worktree with modified or untracked files. The script keeps it,
  keeps its branch, and prints git's reason.
- `git branch -d` refuses an unmerged branch. Git also refuses to delete any branch that a
  worktree still has checked out — which is why worktrees are removed first.
- Uncommitted work lives in the worktree directory, not in the branch, so deleting a branch never
  loses it.

**What the guards do not cover:**

- **Ignored files are deleted with the worktree.** `.env`, `.venv` and caches do not count as
  dirty. In a worktree made by `create_worktree.sh` that is harmless: `.env` is a copy of the
  primary checkout's and the rest is rebuilt.
- **A fresh branch counts as merged.** A worktree created but not yet committed to points at a
  commit already in `main`, so a clean one is removed. No work is lost, but an agent still planning
  in it loses its directory — hence "between tasks".
- **`[gone]` branches are force-deleted (`-D`).** A squash merge leaves no ancestry for `-d` to
  check, so `[gone]` is the signal instead: in the normal workflow (push → merge and delete on the
  host) it means "merged". **Agent safety rule: always `--dry-run` first.** If the list contains a
  branch you don't recognize as landed — one with local-only commits after the merge, or an
  unexpectedly large set (a sign the remote was renamed or removed) — **stop and confirm with the
  user** instead of running it. Deleted branches are recoverable via `git reflog` for a while.

The script is host-agnostic: it uses only git, no `gh`/`glab`/API calls, so it works with GitHub,
GitLab, Bitbucket, or any remote unchanged.

### Wiring it into a project

Reference the script by absolute path from a project so it stays version-controlled
here rather than copied into each repo.

- **VSCode task** (`.vscode/tasks.json`):
  ```json
  {
    "label": "Git: prune landed worktrees and branches",
    "command": "python3 /Users/dima/Projects/dima/.agents/skills/development-best-practices/scripts/prune_merged_branches.py"
  }
  ```
- **Git alias** (terminal convenience, per-clone):
  ```bash
  git config alias.prune-landed '!python3 /Users/dima/Projects/dima/.agents/skills/development-best-practices/scripts/prune_merged_branches.py'
  # then: git prune-landed   (or: git prune-landed --dry-run)
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

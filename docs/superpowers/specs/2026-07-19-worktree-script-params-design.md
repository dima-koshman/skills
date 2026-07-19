# Design: Parameterized `create_worktree` script and VS Code task

Date: 2026-07-19
Status: Approved

## Goal

Make `src/create_worktree.sh` accept the branch name as a **required** first
argument and an **optional** second argument for the worktree directory. The
directory argument may be absolute or relative. When omitted, the directory
defaults to the normalized branch name placed as a sibling of the repository
(matching current behavior).

Wire the same two inputs into the existing VS Code task so it can be launched
from the editor with the optional directory supplied.

## Current behavior (baseline)

- `src/create_worktree.sh <branch-name>`
  - Requires `branch-name`; errors with usage if missing.
  - Computes `SAFE_BRANCH="${BRANCH//\//-}"`.
  - Hardcodes destination as `../${REPO_NAME}-${SAFE_BRANCH}` where
    `REPO_NAME=$(basename "$PWD")` (a sibling of the repo parent dir).
  - Copies `.env` if present.
  - Runs `direnv allow`, `pre-commit install`, `uv sync` in the destination.
  - Launches `ide` on the destination.
- `.vscode/tasks.json` defines:
  - Input `worktreeBranch` (type `promptString`, no default).
  - Task `Create worktree and open in IDE` →
    `bash src/create_worktree.sh ${input:worktreeBranch}`.

The repository is a normal checkout on `main`; no nested worktree is active.

## New interface

### `src/create_worktree.sh`

Signature:

```bash
create_worktree.sh <branch-name> [dir]
```

- `branch-name` (required): errors clearly if missing.
  Implementation: `BRANCH="${1:?Usage: $0 <branch-name> [dir]}"`.
- `dir` (optional):
  - If provided, used as the destination path.
  - If omitted, defaults to `../$(basename "$PWD")-${NORMALIZED}`
    (sibling of the repo, normalized branch name).
- `NORMALIZED="${BRANCH//\//-}"` (replaces `/` with `-`).

Path resolution:

```bash
REPO_PARENT="$(dirname "$PWD")"
if [ -n "${2:-}" ]; then
  DEST="$2"
else
  DEST="../$(basename "$PWD")-${NORMALIZED}"
fi
DEST="$(realpath -m -- "$DEST")"
```

Resolution rules (guaranteed regardless of CWD):

- Absolute dir (e.g. `/tmp/foo`) → used as-is.
- Relative dir (e.g. `wt`) → resolved against the **repo parent** so it stays
  a sibling: `realpath -m -- wt` run from the repo yields
  `<parent-of-repo>/wt`. Implemented by `cd "$REPO_PARENT"` before the
  `realpath`, or by prefixing: `realpath -m -- "$REPO_PARENT/$DEST"` only when
  `DEST` is not absolute. Simplest: `cd "$REPO_PARENT" && realpath -m -- "$DEST"`.
- Omitted dir → `../<repo>-<normalized>` → sibling of repo, as before.

This makes the "relative dir → sibling" behavior explicit and independent of
where the script happens to be invoked from.

Recommended concrete implementation:

```bash
BRANCH="${1:?Usage: $0 <branch-name> [dir]}"
NORMALIZED="${BRANCH//\//-}"
REPO_PARENT="$(dirname "$PWD")"
if [ -n "${2:-}" ]; then
  DEST="$2"
else
  DEST="../$(basename "$PWD")-${NORMALIZED}"
fi
DEST="$(cd "$REPO_PARENT" && realpath -m -- "$DEST")"
```

After resolution, the remainder of the script is unchanged:

- `git worktree add "$DEST" "$BRANCH"`
- Copy `.env` if present.
- Run `direnv allow`, `pre-commit install`, `uv sync` in `$DEST`.
- Launch `ide "$DEST"`.

### `.vscode/tasks.json`

- Add input `worktreeDir`:
  - `type`: `promptString`
  - `description`: "Optional worktree directory (absolute or relative to repo; defaults to normalized branch name)"
  - No `default` (so it can be left blank = use default).
- Update task `Create worktree and open in IDE` command to:
  ```json
  "command": "bash src/create_worktree.sh ${input:worktreeBranch} ${input:worktreeDir}"
  ```
- `worktreeBranch` remains a required prompt (user must supply it).

## Behavior matrix

| branch     | dir arg    | resolved destination            |
|------------|------------|---------------------------------|
| `feat/x`   | —          | `../dima-feat-x`                |
| `feat/x`   | `wt`       | `../wt`                         |
| `feat/x`   | `/tmp/foo` | `/tmp/foo`                      |

(Assumes the script is run from the repository root, `dima`.)

## Out of scope

The following are conceptual discussion topics raised alongside this task and
are **not** implemented here:

- Whether coding agents (opencode, Claude Code, Codex) auto-detect worktrees
  vs. requiring prompt/harness support.
- The tradeoff between remote merge requests and local merge-to-`main` with
  worktrees.

These will be answered in prose, not as code changes.

## Verification

- `bash src/create_worktree.sh` (no args) → prints usage error, exits non-zero.
- `bash src/create_worktree.sh feat/x` → creates `../dima-feat-x`, opens IDE.
- `bash src/create_worktree.sh feat/x wt` → creates `../wt`.
- `bash src/create_worktree.sh feat/x /tmp/foo` → creates `/tmp/foo`.
- VS Code task prompts for branch; optional dir input left blank → default;
  supplied → used as destination.
- Existing `.env` copy and setup steps still run.

# Worktree Script Parameterization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Parameterize `src/create_worktree.sh` so the branch name is required and an optional worktree directory (absolute or relative) can be supplied, defaulting to a normalized sibling path; wire the same two inputs into the VS Code task.

**Architecture:** Small functional change to one bash script plus a matching VS Code `tasks.json` input. Path resolution normalizes the optional dir via `realpath -m` executed from the repo parent so relative dirs resolve as siblings of the repo. Verification is done with direct bash invocations and inspection of `git worktree list`; no new test framework is introduced.

**Tech Stack:** Bash (`set -euo pipefail`, `realpath`), Git worktree, VS Code `tasks.json` `promptString` inputs.

## Global Constraints

- Branch name is a **required** first argument; script must error with a usage message and non-zero exit if missing (spec: `${1:?Usage: $0 <branch-name> [dir]}`).
- Normalized branch name replaces `/` with `-`: `NORMALIZED="${BRANCH//\//-}"` (spec).
- Default destination when dir omitted: `../$(basename "$PWD")-${NORMALIZED}` (sibling of repo, spec).
- Optional dir arg: absolute paths used as-is; relative paths resolved against the **repo parent** so they stay siblings (spec behavior matrix: `feat/x` + `wt` → `../wt`).
- Resolution must use `realpath -m` so the path need not exist yet (spec).
- Remainder of script unchanged: `git worktree add`, `.env` copy, `direnv/pre-commit/uv` setup, `ide` launch (spec "remainder of the script is unchanged").
- `.vscode/tasks.json`: add a `worktreeDir` `promptString` input (no default) and pass it as the second arg to the script (spec).
- Do not change the conceptual-discussion scope (agent worktree detection, MR vs local merge) — out of scope per spec.

---

### Task 1: Parameterize `create_worktree.sh`

**Files:**
- Modify: `src/create_worktree.sh` (full file)

**Interfaces:**
- Consumes: nothing external beyond `git`, `realpath`, `basename`, `dirname`, and the existing `ide`/`direnv`/`pre-commit`/`uv` commands.
- Produces: a script with signature `create_worktree.sh <branch-name> [dir]` that prints the resolved destination and creates the worktree there.

- [ ] **Step 1: Replace the argument handling and path resolution in `src/create_worktree.sh`**

Replace lines 4-12 (the usage guard, `BRANCH`, `SAFE_BRANCH`, `REPO_NAME`, `DESTINATION`) with the required-arg + normalized + optional-dir logic. The full updated script should read:

```bash
#!/bin/bash
set -euo pipefail

BRANCH="${1:?Usage: $0 <branch-name> [dir]}"
NORMALIZED="${BRANCH//\//-}"
REPO_PARENT="$(dirname "$PWD")"

if [ -n "${2:-}" ]; then
  DEST="$2"
else
  DEST="../$(basename "$PWD")-${NORMALIZED}"
fi
DEST="$(cd "$REPO_PARENT" && realpath -m -- "$DEST")"

echo "Creating worktree at ${DEST} for branch ${BRANCH}..."
git worktree add "${DEST}" "${BRANCH}"

# Copy .env if it exists
if [ -f .env ]; then
  echo "Copying .env..."
  cp .env "${DEST}/.env"
fi

# Run setup commands in destination
(
  cd "${DEST}"
  echo "Running setup commands..."
  if command -v direnv >/dev/null 2>&1; then
    direnv allow || true
  fi
  if command -v pre-commit >/dev/null 2>&1; then
    pre-commit install || true
  fi
  if command -v uv >/dev/null 2>&1; then
    uv sync || true
  fi
)

# Launch IDE
echo "Launching IDE..."
if command -v ide >/dev/null 2>&1; then
  ide "${DEST}"
else
  echo "Warning: 'ide' command not found."
fi
```

- [ ] **Step 2: Verify the no-argument error path**

Run from the repo root:
```bash
bash src/create_worktree.sh
```
Expected: prints `src/create_worktree.sh: line 4: 1: Usage: src/create_worktree.sh <branch-name> [dir]` (or similar `${1:?}` message) and exits non-zero. Confirm with `echo $?` → non-zero (1).

- [ ] **Step 3: Verify default (omitted dir) resolves to a sibling**

Run (use a branch name that does not already exist as a worktree):
```bash
bash -x src/create_worktree.sh feat/verify-default 2>&1 | grep -E 'DEST=|Creating worktree' | head -3
```
Expected: `DEST=` line shows `<parent-of-dima>/dima-feat-verify-default` and the `git worktree add` uses that path. Note: this will actually create the worktree; clean it up in Step 5.

- [ ] **Step 4: Verify relative dir resolves to a sibling of the repo**

Run:
```bash
bash -x src/create_worktree.sh feat/verify-rel wt-rel 2>&1 | grep -E 'DEST=|Creating worktree' | head -3
```
Expected: `DEST=` shows `<parent-of-dima>/wt-rel` (sibling), not inside `dima/`. Clean up in Step 5.

- [ ] **Step 5: Verify absolute dir passes through and clean up test worktrees**

Run:
```bash
bash -x src/create_worktree.sh feat/verify-abs /tmp/wt-abs 2>&1 | grep -E 'DEST=|Creating worktree' | head -3
```
Expected: `DEST=` shows `/tmp/wt-abs`. Then remove all three test worktrees:
```bash
git worktree remove ../dima-feat-verify-default --force 2>/dev/null || true
git worktree remove ../wt-rel --force 2>/dev/null || true
git worktree remove /tmp/wt-abs --force 2>/dev/null || true
git worktree prune
git worktree list
```
Expected: `git worktree list` shows only the `dima` main checkout (no `feat/verify-*` or `wt-rel`/`wt-abs` entries).

- [ ] **Step 6: Commit**

```bash
git add src/create_worktree.sh
git commit -m "feat(worktree): require branch name, add optional dir arg (absolute or relative)

Relative dirs resolve against the repo parent so they stay siblings;
absolute paths pass through; default is ../<repo>-<normalized-branch>."
```

---

### Task 2: Add `worktreeDir` input and wire it into the VS Code task

**Files:**
- Modify: `.vscode/tasks.json`

**Interfaces:**
- Consumes: the script now expects `bash src/create_worktree.sh <branch> [dir]` (produced in Task 1).
- Produces: a VS Code task whose command passes both `${input:worktreeBranch}` and `${input:worktreeDir}`.

- [ ] **Step 1: Add the `worktreeDir` input**

In `.vscode/tasks.json`, inside the `"inputs"` array, add a new entry alongside the existing `worktreeBranch` and `pid` entries:

```json
        {
            "id": "worktreeDir",
            "type": "promptString",
            "description": "Optional worktree directory (absolute or relative to repo; defaults to normalized branch name)"
        },
```

- [ ] **Step 2: Update the task command to pass the optional dir**

Find the existing task:
```json
        {
            "label": "Create worktree and open in IDE",
            "command": "bash src/create_worktree.sh ${input:worktreeBranch}"
        },
```
Change its `"command"` to include the second input:
```json
        {
            "label": "Create worktree and open in IDE",
            "command": "bash src/create_worktree.sh ${input:worktreeBranch} ${input:worktreeDir}"
        },
```

- [ ] **Step 3: Validate JSON syntax**

Run:
```bash
python3 -c "import json,sys; json.load(open('.vscode/tasks.json')); print('OK')"
```
Expected: prints `OK` (no parse error).

- [ ] **Step 4: Confirm the branch input is still required and dir optional**

Inspect that `worktreeBranch` still has no `default` (user must supply it) and `worktreeDir` has no `default` (blank = default path). Read the relevant lines back to confirm.

- [ ] **Step 5: Commit**

```bash
git add .vscode/tasks.json
git commit -m "feat(vscode): add optional worktreeDir input to worktree task"
```

---

### Task 3: Document the new interface in the README (if a worktree section exists)

**Files:**
- Modify: `README.md` (only if it references `create_worktree.sh`); otherwise skip.

**Interfaces:**
- Consumes: the new script signature from Task 1.
- Produces: accurate usage docs.

- [ ] **Step 1: Check whether README mentions the worktree script**

Run:
```bash
grep -n "create_worktree" README.md || echo "NO_MENTION"
```
If `NO_MENTION`, skip to Step 3 (no commit needed for README).

- [ ] **Step 2: Update the README usage line**

If found, replace any existing usage like `bash src/create_worktree.sh <branch-name>` with:
```
bash src/create_worktree.sh <branch-name> [dir]
```
where `dir` is optional (absolute or relative; defaults to `../<repo>-<normalized-branch>`).

- [ ] **Step 3: Commit only if README was changed**

```bash
git add README.md
git commit -m "docs(readme): document optional dir arg for create_worktree.sh"
```
If no change was made, do not commit.

---

## Self-Review Notes

- **Spec coverage:** Task 1 covers required branch arg + optional dir + normalization + sibling default + absolute passthrough + unchanged remainder. Task 2 covers the VS Code input and command wiring. Task 3 covers docs. Conceptual questions are explicitly out of scope per spec.
- **Placeholder scan:** No TBD/TODO; all steps show exact code or commands. Task 3 gracefully skips when not applicable.
- **Type consistency:** Script signature `<branch-name> [dir]` matches the task command `${input:worktreeBranch} ${input:worktreeDir}` in both tasks. Path variable names (`BRANCH`, `NORMALIZED`, `DEST`) are consistent within Task 1.

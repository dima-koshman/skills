#!/usr/bin/env python3
"""Remove worktrees and local branches whose work has already landed.

A branch has landed when it is merged into the integration branch (the branch checked out in
the primary worktree, normally main), or when its upstream is gone: after a squash-merged
PR/MR deletes the remote branch, `git fetch --prune` leaves the local branch with a "[gone]"
upstream, and a squash merge leaves no ancestry for a merge check to find.

Git's own guards do the safety work. `git worktree remove` refuses a worktree with modified
or untracked files, and `git branch -d` refuses an unmerged branch; a refused worktree is
kept along with its branch, and git's reason is printed. Ignored files (.env, .venv, caches)
do not block removal and are deleted with the worktree. The primary worktree and the
worktree this runs from are never removed.

A branch created but not yet committed to also counts as merged, so run this between tasks,
not while a fresh worktree is being set up.

Host-agnostic: only git plumbing, no gh/glab/API calls.

Usage:
    prune_merged_branches.py            # remove landed worktrees and branches
    prune_merged_branches.py --dry-run  # only list what would be removed
"""

import argparse
import dataclasses
import pathlib
import subprocess
import sys


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Remove worktrees and local branches whose work has landed."
    )
    _ = parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List what would be removed, change nothing.",
    )
    args = parser.parse_args()
    try:
        prune(dry_run=args.dry_run)
    except subprocess.CalledProcessError as error:
        sys.exit(f"git {' '.join(error.cmd[3:])} failed: {error.stderr.strip()}")


def prune(dry_run: bool) -> None:
    """Remove landed worktrees, then delete landed branches that are no longer checked out."""
    current = pathlib.Path(
        _git_output("rev-parse", "--show-toplevel", cwd=pathlib.Path.cwd())
    ).resolve()
    worktrees = _list_worktrees(current)
    primary = worktrees[0]  # git always lists the primary worktree first
    if primary.branch is None:
        sys.exit(
            f"The primary worktree {primary.path} is on a detached HEAD; check out the integration branch."
        )

    # Run everything from the primary worktree, so `git branch -d` checks merges against its HEAD
    # (the integration branch) rather than whatever branch the current worktree has checked out.
    root = primary.path
    if _git_output("remote", cwd=root):
        print(">> git fetch --prune")
        _ = _git_output("fetch", "--prune", cwd=root)

    landed = _landed_branches(primary.branch, cwd=root)
    kept_branches = {
        primary.branch,
        *(worktree.branch for worktree in worktrees if worktree.path == current),
    }
    for worktree in worktrees[1:]:
        if worktree.path == current or worktree.branch not in landed:
            continue

        if dry_run:
            print(f"would remove worktree {worktree.path} ({worktree.branch})")
            continue

        result = _git("worktree", "remove", str(worktree.path), cwd=root)
        if result.returncode == 0:
            print(f"removed worktree {worktree.path}")
        else:
            print(f"kept worktree {worktree.path}: {result.stderr.strip()}")
            kept_branches.add(worktree.branch)

    for branch, merged in landed.items():
        if branch in kept_branches:
            continue

        if dry_run:
            print(f"would delete branch {branch}")
            continue

        # A gone-but-unmerged branch was squash-merged on the host, so -d would refuse it.
        result = _git("branch", "-d" if merged else "-D", branch, cwd=root)
        if result.returncode == 0:
            print(f"deleted branch {branch}")
        else:
            print(f"kept branch {branch}: {result.stderr.strip()}")

    if dry_run:
        print("(dry run, nothing removed)")
    else:
        _ = _git_output("worktree", "prune", cwd=root)


@dataclasses.dataclass(frozen=True)
class _Worktree:
    path: pathlib.Path
    branch: str | None  # None for a detached HEAD


def _list_worktrees(cwd: pathlib.Path) -> list[_Worktree]:
    worktrees: list[_Worktree] = []
    # Porcelain output is one block per worktree: "worktree <path>", then "branch refs/heads/<name>"
    # unless the HEAD is detached.
    for block in _git_output("worktree", "list", "--porcelain", cwd=cwd).split("\n\n"):
        fields = dict(line.partition(" ")[::2] for line in block.splitlines())
        branch = fields.get("branch")
        worktrees.append(
            _Worktree(
                path=pathlib.Path(fields["worktree"]).resolve(),
                branch=branch.removeprefix("refs/heads/") if branch else None,
            )
        )

    return worktrees


def _landed_branches(integration_branch: str, cwd: pathlib.Path) -> dict[str, bool]:
    """Map each landed branch to whether it is merged into the integration branch."""
    merged = set(
        _git_output(
            "for-each-ref",
            "--merged",
            integration_branch,
            "--format=%(refname:short)",
            "refs/heads/",
            cwd=cwd,
        ).splitlines()
    )
    tracking = _git_output(
        "for-each-ref",
        "--format=%(refname:short)\t%(upstream:track)",
        "refs/heads/",
        cwd=cwd,
    )
    gone = {
        branch
        for branch, _, track in (line.partition("\t") for line in tracking.splitlines())
        if track == "[gone]"
    }
    return {
        branch: branch in merged
        for branch in sorted(merged | gone)
        if branch != integration_branch
    }


def _git(*args: str, cwd: pathlib.Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(cwd), *args], capture_output=True, text=True, check=False
    )


def _git_output(*args: str, cwd: pathlib.Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(cwd), *args], capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


if __name__ == "__main__":
    main()

import os
import pathlib
import subprocess
import sys

import pytest


@pytest.fixture
def repo(tmp_path: pathlib.Path) -> "_Repo":
    return _Repo(tmp_path)


def test_removes_clean_worktree_of_merged_branch_and_deletes_branch(
    repo: "_Repo",
) -> None:
    worktree = repo.add_worktree("feat")
    repo.commit(worktree, "feat.txt")
    repo.merge("feat")

    _ = repo.prune()

    assert not worktree.exists()
    assert "feat" not in repo.branches()


def test_keeps_dirty_worktree_of_merged_branch(repo: "_Repo") -> None:
    worktree = repo.add_worktree("feat")
    repo.commit(worktree, "feat.txt")
    repo.merge("feat")
    _ = (worktree / "notes.txt").write_text("work in progress")

    result = repo.prune()

    assert worktree.exists()
    assert "feat" in repo.branches()
    assert "contains modified or untracked files" in result.stdout


def test_keeps_worktree_with_unmerged_commits(repo: "_Repo") -> None:
    worktree = repo.add_worktree("feat")
    repo.commit(worktree, "feat.txt")

    _ = repo.prune()

    assert worktree.exists()
    assert "feat" in repo.branches()


def test_removes_worktree_of_branch_whose_upstream_is_gone(repo: "_Repo") -> None:
    worktree = repo.add_worktree("feat")
    repo.commit(worktree, "feat.txt")
    repo.push(worktree, "feat")
    repo.delete_remote_branch("feat")

    _ = repo.prune()

    assert not worktree.exists()
    assert "feat" not in repo.branches()


def test_deletes_merged_branch_without_worktree(repo: "_Repo") -> None:
    repo.git("branch", "old")

    _ = repo.prune()

    assert "old" not in repo.branches()


def test_never_removes_worktree_it_runs_from(repo: "_Repo") -> None:
    worktree = repo.add_worktree("feat")
    repo.commit(worktree, "feat.txt")
    repo.merge("feat")

    _ = repo.prune(cwd=worktree)

    assert worktree.exists()
    assert "feat" in repo.branches()


def test_deletes_merged_branch_when_run_from_another_worktree(repo: "_Repo") -> None:
    current = repo.add_worktree("current")
    repo.commit(current, "current.txt")
    merged = repo.add_worktree("merged")
    repo.commit(merged, "merged.txt")
    repo.merge("merged")

    _ = repo.prune(cwd=current)

    assert not merged.exists()
    assert "merged" not in repo.branches()


def test_dry_run_lists_landed_worktree_without_removing_it(repo: "_Repo") -> None:
    worktree = repo.add_worktree("feat")
    repo.commit(worktree, "feat.txt")
    repo.merge("feat")

    result = repo.prune("--dry-run")

    assert worktree.exists()
    assert "feat" in repo.branches()
    assert str(worktree) in result.stdout


class _Repo:
    """A primary checkout cloned from a bare remote, with worktrees beside it."""

    def __init__(self, root: pathlib.Path):
        self.root: pathlib.Path = root.resolve()
        self.main: pathlib.Path = self.root / "main"
        gitconfig = self.root / "gitconfig"
        _ = gitconfig.write_text(
            "[user]\n\tname = Test\n\temail = test@example.com\n[init]\n\tdefaultBranch = main\n"
        )
        # Isolate from the host's git config and from GIT_* variables a terminal may inject.
        self.env: dict[str, str] = {
            name: value
            for name, value in os.environ.items()
            if not name.startswith("GIT_")
        } | {"GIT_CONFIG_GLOBAL": str(gitconfig), "GIT_CONFIG_NOSYSTEM": "1"}
        remote = self.root / "remote.git"
        _ = self._run("git", "init", "-q", "--bare", str(remote), cwd=self.root)
        _ = self._run("git", "clone", "-q", str(remote), str(self.main), cwd=self.root)
        self.commit(self.main, "README")
        self.git("push", "-q", "-u", "origin", "main")

    def git(self, *args: str) -> None:
        _ = self._run("git", *args, cwd=self.main)

    def add_worktree(self, branch: str) -> pathlib.Path:
        path = self.root / "worktrees" / branch
        self.git("worktree", "add", "-q", "-b", branch, str(path))
        return path

    def commit(self, cwd: pathlib.Path, filename: str) -> None:
        _ = (cwd / filename).write_text(filename)
        _ = self._run("git", "add", filename, cwd=cwd)
        _ = self._run("git", "commit", "-q", "-m", f"Add {filename}", cwd=cwd)

    def merge(self, branch: str) -> None:
        self.git("merge", "-q", "--no-ff", "--no-edit", branch)

    def push(self, cwd: pathlib.Path, branch: str) -> None:
        _ = self._run("git", "push", "-q", "-u", "origin", branch, cwd=cwd)

    def delete_remote_branch(self, branch: str) -> None:
        self.git("push", "-q", "origin", "--delete", branch)

    def branches(self) -> list[str]:
        return self._run(
            "git",
            "for-each-ref",
            "--format=%(refname:short)",
            "refs/heads/",
            cwd=self.main,
        ).splitlines()

    def prune(
        self, *args: str, cwd: pathlib.Path | None = None
    ) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, str(_SCRIPT), *args],
            cwd=cwd or self.main,
            env=self.env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, (
            f"prune exited {result.returncode}:\n{result.stdout}\n{result.stderr}"
        )
        return result

    def _run(self, *command: str, cwd: pathlib.Path) -> str:
        """Run a setup command, returning its stdout and raising if it fails."""
        return subprocess.run(
            command, cwd=cwd, env=self.env, capture_output=True, text=True, check=True
        ).stdout


_SCRIPT = (
    pathlib.Path(__file__).parent.parent
    / ".agents/skills/development-best-practices/scripts/prune_merged_branches.py"
)

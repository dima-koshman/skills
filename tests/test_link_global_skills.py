import os
import pathlib
import subprocess
from typing import final

import pytest

_SCRIPT = pathlib.Path(__file__).parent.parent / "scripts/link_global_skills.sh"


@pytest.fixture
def env(tmp_path: pathlib.Path) -> "_Env":
    return _Env(tmp_path)


def test_links_skill_into_agents_and_claude_dirs(env: "_Env") -> None:
    skill = env.skill("alpha")

    _ = env.run(str(skill))

    assert (env.agents / "alpha").resolve() == skill.resolve()
    assert os.readlink(env.claude / "alpha") == "../../.agents/skills/alpha"
    assert (env.claude / "alpha" / "SKILL.md").read_text() == (
        skill / "SKILL.md"
    ).read_text()


def test_rerun_is_idempotent(env: "_Env") -> None:
    skill = env.skill("alpha")
    _ = env.run(str(skill))

    result = env.run(str(skill))

    assert "already linked" in result.stdout
    assert (env.agents / "alpha").resolve() == skill.resolve()


def test_replaces_copy_of_the_same_skill(env: "_Env") -> None:
    skill = env.skill("alpha")
    copy = env.agents / "alpha"
    copy.mkdir(parents=True)
    _ = (copy / "SKILL.md").write_text(
        "---\nname: alpha\ndescription: stale copy\n---\n"
    )

    result = env.run(str(skill))

    assert (env.agents / "alpha").is_symlink()
    assert (env.agents / "alpha").resolve() == skill.resolve()
    assert "replaced copy" in result.stdout


def test_refuses_to_replace_unrelated_directory(env: "_Env") -> None:
    skill = env.skill("alpha")
    other = env.agents / "alpha"
    other.mkdir(parents=True)
    _ = (other / "notes.txt").write_text("not a skill")

    result = env.run(str(skill), check=False)

    assert result.returncode != 0
    assert not (env.agents / "alpha").is_symlink()
    assert (other / "notes.txt").exists()


def test_rejects_directory_without_skill_md(
    env: "_Env", tmp_path: pathlib.Path
) -> None:
    empty = tmp_path / "src" / "empty"
    empty.mkdir(parents=True)

    result = env.run(str(empty), check=False)

    assert result.returncode != 0
    assert not (env.agents / "empty").exists()


def test_unlink_removes_only_links_to_given_skill(env: "_Env") -> None:
    alpha, beta = env.skill("alpha"), env.skill("beta")
    _ = env.run(str(alpha), str(beta))

    _ = env.run("--unlink", str(alpha))

    assert not (env.agents / "alpha").exists()
    assert not (env.claude / "alpha").is_symlink()
    assert (env.agents / "beta").is_symlink()
    assert (alpha / "SKILL.md").exists()


def test_status_reports_linked_and_missing(env: "_Env") -> None:
    alpha, beta = env.skill("alpha"), env.skill("beta")
    _ = env.run(str(alpha))

    result = env.run("--status", str(alpha), str(beta))

    assert "alpha" in result.stdout and "linked" in result.stdout
    assert "beta" in result.stdout and "missing" in result.stdout


@final
class _Env:
    def __init__(self, root: pathlib.Path) -> None:
        self.home = root / "home"
        self.src = root / "src"
        self.agents = self.home / ".agents" / "skills"
        self.claude = self.home / ".claude" / "skills"
        self.home.mkdir()

    def skill(self, name: str) -> pathlib.Path:
        path = self.src / name
        path.mkdir(parents=True)
        _ = (path / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: test skill\n---\n"
        )
        return path

    def run(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            ["bash", str(_SCRIPT), *args],
            env={**os.environ, "HOME": str(self.home)},
            capture_output=True,
            text=True,
            check=False,
        )
        if check:
            assert result.returncode == 0, (
                f"exit {result.returncode}:\n{result.stdout}\n{result.stderr}"
            )
        return result

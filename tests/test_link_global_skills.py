import os
import pathlib
import subprocess
import tomllib
from typing import final

import pytest

_SCRIPT = pathlib.Path(__file__).parent.parent / "scripts/link_global_skills.py"


@pytest.fixture
def env(tmp_path: pathlib.Path) -> "_Env":
    return _Env(tmp_path)


def test_links_skill_into_every_installed_harness(env: "_Env") -> None:
    skill = env.skill("alpha")

    _ = env.run(str(skill))

    assert os.readlink(env.claude / "alpha") == str(skill)
    assert os.readlink(env.opencode / "alpha") == str(skill)
    assert os.readlink(env.antigravity / "alpha") == str(skill)
    assert env.codex_paths() == [str(skill / "SKILL.md")]
    assert not (env.home / ".agents/skills/alpha").exists()


def test_skips_harness_that_is_not_installed(env: "_Env") -> None:
    skill = env.skill("alpha")
    (env.home / ".gemini").rmdir()

    result = env.run(str(skill))

    assert "no harness" in result.stdout
    assert not (env.home / ".gemini").exists()
    assert (env.claude / "alpha").is_symlink()


def test_one_harness_only(env: "_Env") -> None:
    skill = env.skill("alpha")

    _ = env.run("--harness", "codex", str(skill))

    assert env.codex_paths() == [str(skill / "SKILL.md")]
    assert not (env.claude / "alpha").exists()
    assert not (env.opencode / "alpha").exists()


def test_rerun_is_idempotent(env: "_Env") -> None:
    skill = env.skill("alpha")
    _ = env.run(str(skill))
    before = env.codex_config.read_text()

    result = env.run(str(skill))

    assert result.stdout.count("already linked") == 4
    assert env.codex_config.read_text() == before


def test_unlink_one_harness_keeps_the_others(env: "_Env") -> None:
    alpha, beta = env.skill("alpha"), env.skill("beta")
    _ = env.run(str(alpha), str(beta))

    _ = env.run("--harness", "antigravity", "--unlink", str(alpha))
    _ = env.run("--harness", "codex", "--unlink", str(alpha))

    assert not (env.antigravity / "alpha").exists()
    assert env.codex_paths() == [str(beta / "SKILL.md")]
    assert (env.claude / "alpha").is_symlink()
    assert (env.antigravity / "beta").is_symlink()
    assert (alpha / "SKILL.md").exists()


def test_codex_block_keeps_other_config_and_disappears_when_empty(env: "_Env") -> None:
    skill = env.skill("alpha")
    original = 'model = "keep"\n\n[mcp_servers.x]\ncommand = "keep"\n'
    _ = env.codex_config.write_text(original)

    _ = env.run(str(skill))
    config = tomllib.loads(env.codex_config.read_text())
    _ = env.run("--unlink", str(skill))

    assert config["model"] == "keep"
    assert config["skills"]["config"] == [
        {"path": str(skill / "SKILL.md"), "enabled": True}
    ]
    assert env.codex_config.read_text() == original


def test_codex_tables_added_inside_the_block_survive(env: "_Env") -> None:
    alpha, beta = env.skill("alpha"), env.skill("beta")
    _ = env.run("--harness", "codex", str(alpha))
    # Codex inserts tables it adds before the file's last comment line, i.e. inside the block.
    _ = env.codex_config.write_text(
        env.codex_config.read_text().replace(
            "# END", '[hooks.state."x"]\nhash = "h"\n# END'
        )
    )

    _ = env.run("--harness", "codex", str(beta))
    _ = env.run("--harness", "codex", "--unlink", str(alpha))

    config = tomllib.loads(env.codex_config.read_text())
    assert config["hooks"]["state"]["x"] == {"hash": "h"}
    assert env.codex_paths() == [str(beta / "SKILL.md")]


def test_migrates_shared_link_keeping_who_saw_it(env: "_Env") -> None:
    skill = env.skill("alpha")
    shared = env.home / ".agents/skills"
    shared.mkdir(parents=True)
    (shared / "alpha").symlink_to(skill)
    (env.claude / "alpha").symlink_to("../../.agents/skills/alpha")
    env.antigravity.mkdir(parents=True)
    (env.antigravity / "alpha").symlink_to("../../../.agents/skills/alpha")

    result = env.run("--harness", "antigravity", "--unlink", str(skill))

    assert "migrated" in result.stdout
    assert not (shared / "alpha").exists()
    assert os.readlink(env.claude / "alpha") == str(skill)
    assert os.readlink(env.opencode / "alpha") == str(skill)
    assert env.codex_paths() == [str(skill / "SKILL.md")]
    assert not (env.antigravity / "alpha").exists()


def test_replaces_copy_of_the_same_skill(env: "_Env") -> None:
    skill = env.skill("alpha")
    copy = env.claude / "alpha"
    copy.mkdir()
    _ = (copy / "SKILL.md").write_text(
        "---\nname: alpha\ndescription: stale copy\n---\n"
    )

    result = env.run("--harness", "claude", str(skill))

    assert os.readlink(env.claude / "alpha") == str(skill)
    assert "replaced copy" in result.stdout


def test_refuses_to_replace_unrelated_directory(env: "_Env") -> None:
    skill = env.skill("alpha")
    other = env.claude / "alpha"
    other.mkdir()
    _ = (other / "notes.txt").write_text("not a skill")

    result = env.run("--harness", "claude", str(skill), check=False)

    assert result.returncode != 0
    assert not (env.claude / "alpha").is_symlink()
    assert (other / "notes.txt").exists()


def test_rejects_directory_without_skill_md(
    env: "_Env", tmp_path: pathlib.Path
) -> None:
    empty = tmp_path / "src" / "empty"
    empty.mkdir(parents=True)

    result = env.run(str(empty), check=False)

    assert result.returncode != 0
    assert not (env.claude / "empty").exists()


def test_status_reports_per_harness(env: "_Env") -> None:
    alpha, beta = env.skill("alpha"), env.skill("beta")
    _ = env.run("--harness", "claude", str(alpha))

    lines = env.run("--status", str(alpha), str(beta)).stdout.splitlines()

    assert lines[0].split() == ["skill", "claude", "codex", "opencode", "antigravity"]
    assert lines[1].split() == ["alpha", "linked", "missing", "missing", "missing"]
    assert lines[2].split() == ["beta", "missing", "missing", "missing", "missing"]


@final
class _Env:
    def __init__(self, root: pathlib.Path) -> None:
        self.home = root / "home"
        self.src = root / "src"
        self.claude = self.home / ".claude/skills"
        self.opencode = self.home / ".config/opencode/skills"
        self.antigravity = self.home / ".gemini/config/skills"
        self.codex_config = self.home / ".codex/config.toml"
        for path in (self.claude, self.opencode, self.home / ".codex"):
            path.mkdir(parents=True)
        (self.home / ".gemini").mkdir()

    def skill(self, name: str) -> pathlib.Path:
        path = self.src / name
        path.mkdir(parents=True)
        _ = (path / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: test skill\n---\n"
        )
        return path

    def codex_paths(self) -> list[str]:
        if not self.codex_config.exists():
            return []
        config = tomllib.loads(self.codex_config.read_text())
        return [entry["path"] for entry in config.get("skills", {}).get("config", [])]

    def run(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            ["python3", str(_SCRIPT), *args],
            env={"HOME": str(self.home), "PATH": os.environ["PATH"]},
            capture_output=True,
            text=True,
            check=False,
        )
        if check:
            assert result.returncode == 0, (
                f"exit {result.returncode}:\n{result.stdout}\n{result.stderr}"
            )
        return result

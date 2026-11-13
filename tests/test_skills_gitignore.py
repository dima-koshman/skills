"""Git tracks only the skills authored in this repo; skills-lock.json records the remote ones.

`npx skills add` always installs project skills into .agents/skills/<name>, so the
.gitignore ignores that directory by default and allowlists each owned skill.
"""

import json
import pathlib
import subprocess

_ROOT = pathlib.Path(__file__).parent.parent
_SKILLS = _ROOT / ".agents/skills"


def _is_ignored(path: pathlib.Path) -> bool:
    # --no-index applies the ignore rules to tracked files too, so a tracked skill
    # that the rules would hide still counts as ignored.
    result = subprocess.run(
        ["git", "check-ignore", "--no-index", "--quiet", str(path.relative_to(_ROOT))],
        cwd=_ROOT,
        check=False,
    )
    return result.returncode == 0


def _remote_skill_names() -> set[str]:
    lock = json.loads((_ROOT / "skills-lock.json").read_text(encoding="utf-8"))
    return {
        name for name, entry in lock["skills"].items() if entry["sourceType"] != "local"
    }


def test_a_newly_installed_skill_is_ignored() -> None:
    assert _is_ignored(_SKILLS / "some-remote-skill/SKILL.md")


def test_owned_skills_are_not_ignored() -> None:
    remote = _remote_skill_names()
    owned = [
        d for d in sorted(_SKILLS.iterdir()) if d.is_dir() and d.name not in remote
    ]

    ignored = [d.name for d in owned if _is_ignored(d / "SKILL.md")]

    assert owned
    assert ignored == [], "add a `!/.agents/skills/<name>/` line to .gitignore for each"

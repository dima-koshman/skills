#!/usr/bin/env python3
"""Remove installed agent skills, globally or from one project, without ever deleting a skill's source.

Where a skill can be installed (one name may be in several of these):
    global   ~/.agents/skills/ (Codex, OpenCode), ~/.claude/skills/, ~/.config/opencode/skills/, ~/.codex/skills/,
             ~/.gemini/antigravity-cli/skills/; lock ~/.agents/.skill-lock.json
    project  <project>/.agents/skills/, <project>/.claude/skills/, <project>/.opencode/skills/; lock <project>/skills-lock.json

Rules, per installed entry:
    symlink      remove the link only (link_global_skills.sh links and npx's ~/.claude/skills links point at a source)
    copy         delete the directory: a remote install (npx skills add owner/repo) or a copy of a local one
    source       never deleted: a git-tracked skill, or the directory a `sourceType: local` lock entry installs from
                 (`npx skills remove` would delete those, e.g. a project's own .agents/skills/<name> or, through a
                 global symlink, the skill in its repo)
The lock entry of a removed skill is dropped too, so `npx skills update` doesn't bring it back.

Without --confirm=yes this only prints what it would do.

Usage: remove_skills.py [--global] [--project DIR] [--confirm=yes] NAME [NAME ...]
"""

import argparse
import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import cast

HOME = Path.home()
GLOBAL_DIRS = [
    HOME / p
    for p in (
        ".agents/skills",
        ".claude/skills",
        ".config/opencode/skills",
        ".codex/skills",
        ".gemini/antigravity-cli/skills",
    )
]
GLOBAL_LOCK = HOME / ".agents/.skill-lock.json"
PROJECT_DIRS = [".agents/skills", ".claude/skills", ".opencode/skills"]

LockEntry = dict[str, str]
Lock = dict[str, object]  # {"version": ..., "skills": {name: LockEntry}, ...}


@dataclass
class Step:
    action: str  # unlink | delete | keep
    path: Path
    why: str


def lock_skills(lock: Lock) -> dict[str, LockEntry]:
    return cast(dict[str, LockEntry], lock.get("skills") or {})


def git_tracked(path: Path) -> bool:
    """True if the skill directory is part of a git repository's tracked files."""
    result = subprocess.run(
        ["git", "-C", str(path), "ls-files", "--error-unmatch", "SKILL.md"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def local_sources(lock: Lock, base: Path) -> set[Path]:
    """Directories that local lock entries install from: deleting them would delete the skill itself."""
    out: set[Path] = set()
    for entry in lock_skills(lock).values():
        if entry.get("sourceType") == "local" and entry.get("source"):
            src = Path(os.path.expanduser(entry["source"]))
            src = src if src.is_absolute() else base / src
            skill_md = entry.get("skillPath")
            out.add((src / skill_md).parent.resolve() if skill_md else src.resolve())
    return out


def plan(names: list[str], dirs: list[Path], lock: Lock, lock_base: Path) -> list[Step]:
    sources = local_sources(lock, lock_base)
    steps: list[Step] = []
    seen: set[str] = set()
    for name in names:
        for root in dirs:
            entry = root / name
            if root.is_symlink() and root.resolve() in {
                d.resolve() for d in dirs if d != root and d.exists()
            }:
                continue  # e.g. <project>/.claude/skills -> ../.agents/skills: the same entries, handled once
            if not (entry.is_symlink() or entry.exists()):
                continue
            key = str(entry.absolute())
            if key in seen:
                continue
            seen.add(key)
            if entry.is_symlink():
                steps.append(Step("unlink", entry, f"symlink -> {os.readlink(entry)}"))
            elif entry.resolve() in sources:
                steps.append(
                    Step(
                        "keep",
                        entry,
                        "source of a local install (lock sourceType local); delete it by hand if you mean it",
                    )
                )
            elif git_tracked(entry):
                steps.append(
                    Step(
                        "keep",
                        entry,
                        "git-tracked source skill; delete it by hand if you mean it",
                    )
                )
            else:
                steps.append(Step("delete", entry, "installed copy"))
    return steps


def tilde(path: Path) -> str:
    return str(path).replace(str(HOME), "~", 1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Remove installed agent skills without deleting their sources."
    )
    _ = parser.add_argument(
        "names", nargs="+", help="skill names (directory names under the skills dirs)"
    )
    _ = parser.add_argument(
        "--global",
        dest="global_",
        action="store_true",
        help="remove from the global skill dirs",
    )
    _ = parser.add_argument(
        "--project", default=".", help="project for project scope (default: cwd)"
    )
    _ = parser.add_argument(
        "--confirm", default="no", help="'yes' to apply; anything else is a dry run"
    )
    args = parser.parse_args()
    raw_names = cast(list[str], args.names)
    global_scope = cast(bool, args.global_)
    names = [n for raw in raw_names for n in raw.replace(",", " ").split() if n]

    if global_scope:
        dirs, lock_path, base = GLOBAL_DIRS, GLOBAL_LOCK, HOME
    else:
        base = Path(cast(str, args.project)).expanduser().resolve()
        dirs, lock_path = [base / d for d in PROJECT_DIRS], base / "skills-lock.json"
    lock = cast(Lock, json.loads(lock_path.read_text())) if lock_path.is_file() else {}
    steps = plan(names, dirs, lock, base)
    kept = {s.path.name for s in steps if s.action == "keep"}
    drop = [n for n in names if n in lock_skills(lock) and n not in kept]
    apply = cast(str, args.confirm).strip().lower() == "yes"

    scope = "global" if global_scope else tilde(base)
    print(f"{'Removing' if apply else 'Dry run (type yes to apply)'} — {scope} scope")
    for s in steps:
        print(f"  {s.action:<7} {tilde(s.path)}  ({s.why})")
    for name in drop:
        print(f"  {'unlock':<7} {name} from {tilde(lock_path)}")
    for name in sorted(set(names) - {s.path.name for s in steps} - set(drop)):
        print(f"  {'absent':<7} {name}: not installed in this scope")
    if not apply:
        return
    for s in steps:
        if s.action == "unlink":
            s.path.unlink()
        elif s.action == "delete":
            shutil.rmtree(s.path)
    if drop:
        skills = lock_skills(lock)
        for name in drop:
            del skills[name]
        _ = lock_path.write_text(json.dumps(lock, indent=2) + "\n")
    print("done; restart running agents to drop the skills from their sessions")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Install skills globally for chosen harnesses, by SYMLINK to the skill's source dir, so edits in the source repo
apply everywhere with no re-run. Re-run only to add or remove a skill, or to change which harnesses get it.

Each harness has its own global skill dir, so a skill can be installed for some harnesses and not others:

    claude       ~/.claude/skills/<name>          -> <skill dir>
    codex        ~/.codex/config.toml             [[skills.config]] path = "<skill dir>/SKILL.md", enabled = true,
                                                  in a block marked "link_global_skills.py" (Codex ignores
                                                  symlinked dirs in ~/.codex/skills)
    opencode     ~/.config/opencode/skills/<name> -> <skill dir>
    antigravity  ~/.gemini/config/skills/<name>   -> <skill dir>

OpenCode also reads ~/.claude/skills, so a skill installed for claude shows up in OpenCode too unless
OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1 is set.

~/.agents/skills is not used: Codex and OpenCode both read it (Antigravity too, when skills.json registers it), so a
skill there can't be limited to one harness. A skill found there (this script's earlier layout: a link to the skill
dir, or a copy of the same skill) is migrated first: it is installed per harness for Claude Code, Codex and
OpenCode, which saw it before, and the shared entry is removed. Links elsewhere that pointed through it are
repointed at the skill dir.

An existing link is repointed; a copy of the same skill (same `name:` in its SKILL.md) is replaced; anything else in
the way is refused, never clobbered. Only harnesses whose config dir exists are touched.

Usage: link_global_skills.py [--harness all|claude|codex|opencode|antigravity] [--unlink | --status] <skill-dir>...
"""

import argparse
import json
import os
import re
import shutil
import sys
import tomllib
from pathlib import Path

HOME = Path.home()
SHARED = HOME / ".agents/skills"
LINK_DIRS = {
    "claude": HOME / ".claude/skills",
    "opencode": HOME / ".config/opencode/skills",
    "antigravity": HOME / ".gemini/config/skills",
}
HARNESS_DIRS = {
    "claude": HOME / ".claude",
    "codex": HOME / ".codex",
    "opencode": HOME / ".config/opencode",
    "antigravity": HOME / ".gemini",
}
HARNESSES = list(HARNESS_DIRS)
SAW_SHARED = ["claude", "codex", "opencode"]
CODEX_CONFIG = HOME / ".codex/config.toml"
BEGIN = "# BEGIN link_global_skills.py"
END = "# END link_global_skills.py"


def skill_name(skill_dir: Path) -> str | None:
    try:
        text = (skill_dir / "SKILL.md").read_text(errors="ignore")
    except OSError:
        return None
    match = re.search(r"(?m)^name:\s*['\"]?([^'\"\n]+?)['\"]?\s*$", text)
    return match.group(1) if match else None


def is_copy_of(path: Path, name: str) -> bool:
    return path.is_dir() and not path.is_symlink() and skill_name(path) == name


def points_to(link: Path, target: Path) -> bool:
    return link.is_symlink() and link.resolve() == target.resolve()


def split_block(
    text: str, begin: str, end: str, enabled: bool
) -> tuple[str, list[str]]:
    """(text without the marked block, keeping anything in it that isn't one of its skill entries; the entries' paths).

    Codex inserts the tables it adds itself (e.g. [hooks.state."…"]) just before the file's last comment line, so a
    block at the end of the file can collect them; they are moved out, not dropped.
    """
    match = re.search(rf"(?ms)^{re.escape(begin)}\n(.*?)^{re.escape(end)}\n?", text)
    if not match:
        return text, []
    lines, paths, foreign, i = match.group(1).splitlines(), [], [], 0
    value = "true" if enabled else "false"
    while i < len(lines):
        if lines[i].strip() == "[[skills.config]]":
            j = i + 1
            while j < len(lines) and not lines[j].lstrip().startswith("["):
                j += 1
            body = [line for line in lines[i + 1 : j] if line.strip()]
            path = re.fullmatch(r'path = (".*")', body[0]) if len(body) == 2 else None
            if path and body[1] == f"enabled = {value}":
                paths.append(json.loads(path.group(1)))
                i = j
                continue
        foreign.append(lines[i])
        i += 1
    rest = (text[: match.start()] + text[match.end() :]).rstrip("\n")
    moved = "\n".join(foreign).strip("\n")
    joined = "\n\n".join(part for part in (rest, moved) if part)
    return (joined + "\n" if joined else ""), paths


class CodexConfig:
    """The skill paths in this script's block of ~/.codex/config.toml."""

    def paths(self) -> list[str]:
        if not CODEX_CONFIG.is_file():
            return []
        return split_block(CODEX_CONFIG.read_text(), BEGIN, END, enabled=True)[1]

    def write(self, paths: list[str]) -> None:
        text = CODEX_CONFIG.read_text() if CODEX_CONFIG.is_file() else ""
        rest, _ = split_block(text, BEGIN, END, enabled=True)
        entries = "".join(
            f"[[skills.config]]\npath = {json.dumps(p)}\nenabled = true\n\n"
            for p in sorted(paths)
        )
        block = f"{BEGIN}\n{entries}{END}\n" if paths else ""
        new = rest + ("\n" if rest and block else "") + block
        tomllib.loads(new)
        tmp = CODEX_CONFIG.with_name(f".{CODEX_CONFIG.name}.tmp")
        tmp.write_text(new)
        if CODEX_CONFIG.exists():
            os.chmod(tmp, CODEX_CONFIG.stat().st_mode & 0o777)
        os.replace(tmp, CODEX_CONFIG)


class Linker:
    def __init__(self, harnesses: list[str]):
        self.harnesses = harnesses
        self.codex = CodexConfig()
        self.failed = False

    def say(self, state: str, where: object) -> None:
        print(f"{state:<15} {where}")

    def installed(self, harness: str) -> bool:
        return HARNESS_DIRS[harness].is_dir()

    def link(self, harness: str, skill: Path, name: str) -> None:
        if harness == "codex":
            paths = self.codex.paths()
            entry = str(skill / "SKILL.md")
            if entry in paths:
                self.say("already linked", f"{CODEX_CONFIG} {name}")
            else:
                self.codex.write([*paths, entry])
                self.say("linked", f"{CODEX_CONFIG} {name}")
            return
        dest = LINK_DIRS[harness] / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.is_symlink():
            if os.readlink(dest) == str(skill):
                self.say("already linked", dest)
                return
            dest.unlink()
            dest.symlink_to(skill)
            self.say("relinked", f"{dest} -> {skill}")
        elif is_copy_of(dest, name):
            shutil.rmtree(dest)
            dest.symlink_to(skill)
            self.say("replaced copy", f"{dest} -> {skill}")
        elif dest.exists():
            print(
                f"Refusing: {dest} exists and is not a copy of skill '{name}'.",
                file=sys.stderr,
            )
            self.failed = True
        else:
            dest.symlink_to(skill)
            self.say("linked", f"{dest} -> {skill}")

    def unlink(self, harness: str, skill: Path, name: str) -> None:
        if harness == "codex":
            paths = self.codex.paths()
            entry = str(skill / "SKILL.md")
            if entry in paths:
                self.codex.write([p for p in paths if p != entry])
                self.say("unlinked", f"{CODEX_CONFIG} {name}")
            else:
                self.say("not linked here", f"{CODEX_CONFIG} {name}")
            return
        dest = LINK_DIRS[harness] / name
        if points_to(dest, skill):
            dest.unlink()
            self.say("unlinked", dest)
        else:
            self.say("not linked here", dest)

    def state(self, harness: str, skill: Path, name: str) -> str:
        if not self.installed(harness):
            return "-"
        if harness == "codex":
            return (
                "linked" if str(skill / "SKILL.md") in self.codex.paths() else "missing"
            )
        dest = LINK_DIRS[harness] / name
        if points_to(dest, skill):
            return "linked"
        if is_copy_of(dest, name):
            return "copy"
        return "other" if dest.exists() or dest.is_symlink() else "missing"

    def migrate(self, skill: Path, name: str) -> None:
        """Move a shared ~/.agents/skills entry of this skill to per-harness installs that keep who sees it."""
        shared = SHARED / name
        if not (points_to(shared, skill) or is_copy_of(shared, name)):
            return
        through = [
            d / name
            for d in LINK_DIRS.values()
            if (d / name).is_symlink() and (d / name).resolve() == shared.resolve()
        ]
        if shared.is_symlink():
            shared.unlink()
        else:
            shutil.rmtree(shared)
        self.say("migrated", f"{shared} (shared by Codex and OpenCode)")
        for harness in SAW_SHARED:
            if self.installed(harness):
                self.link(harness, skill, name)
        for link in through:
            if link.is_symlink() and not link.exists():
                link.unlink()
                link.symlink_to(skill)
                self.say("relinked", f"{link} -> {skill}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--harness", choices=["all", *HARNESSES], default="all")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--unlink",
        action="store_true",
        help="remove this script's links to the given skills",
    )
    mode.add_argument(
        "--status",
        action="store_true",
        help="show per skill and harness: linked / copy / other / missing",
    )
    parser.add_argument("skills", nargs="+", metavar="skill-dir")
    args = parser.parse_args()
    harnesses = HARNESSES if args.harness == "all" else [args.harness]
    linker = Linker(harnesses)

    if args.status:
        print(f"{'skill':<30} " + " ".join(f"{h:<12}" for h in harnesses))
    else:
        for harness in harnesses:
            if not linker.installed(harness):
                linker.say("no harness", f"{harness} ({HARNESS_DIRS[harness]} missing)")

    for arg in args.skills:
        skill = Path(arg).expanduser().resolve()
        if not (skill / "SKILL.md").is_file():
            print(f"Refusing: {arg} has no SKILL.md.", file=sys.stderr)
            linker.failed = True
            continue
        name = skill.name
        if args.status:
            shared = SHARED / name
            note = (
                "  (also shared in ~/.agents/skills)"
                if points_to(shared, skill) or is_copy_of(shared, name)
                else ""
            )
            print(
                f"{name:<30} "
                + " ".join(f"{linker.state(h, skill, name):<12}" for h in harnesses)
                + note
            )
            continue
        linker.migrate(skill, name)
        for harness in harnesses:
            if linker.installed(harness):
                (linker.unlink if args.unlink else linker.link)(harness, skill, name)

    sys.exit(1 if linker.failed else 0)


if __name__ == "__main__":
    main()

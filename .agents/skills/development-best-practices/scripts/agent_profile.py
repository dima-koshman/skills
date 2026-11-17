#!/usr/bin/env python3
"""Keep a coding-agent profile that shuts out the global skills, MCP servers and instructions.

A profile is a set of harness config dirs under ~/.config/agent-profiles/<name>/ that a project's .envrc switches
to with `use agent_profile <name>` (agent_profile.sh, installed in ~/.config/direnv/lib/):

    claude/       CLAUDE_CONFIG_DIR    its own settings, CLAUDE.md, MCP servers, plugins and skills; own login.
                                       Claude Code still finds ~/.claude/CLAUDE.md as the CLAUDE.md of the
                                       project's ancestor ~, so settings.json lists it in claudeMdExcludes
    codex/        CODEX_HOME           its own config.toml, AGENTS.md, MCP servers and hooks; own login. Codex
                                       still reads ~/.agents/skills, so config.toml disables each of them by path
    opencode/     OPENCODE_CONFIG_DIR  its own opencode.jsonc, AGENTS.md and MCP servers. OpenCode still finds
                                       ~/.agents/skills (it walks up from the project to /), so opencode.json
                                       denies them by name with `skill.use` policies, which hides them
    bin/opencode                       runs OpenCode with --standalone, because the shared background service
                                       keeps the env it was started with

Preferences are seeded once from the global files (no MCP servers, plugins, references or instructions) and are
yours to edit afterwards. The skill lists are regenerated on every run, so a skill installed globally later is shut
out on the next direnv load. Skills of the project itself stay. --keep names global skills to let through (linked
into claude/skills, left out of the Codex and OpenCode lists) unless the project ships its own skill of that name.
The keep list belongs to the profile: projects sharing a profile should pass the same one. Antigravity has no
config-dir switch and is not covered.

Usage: agent_profile.py [--profile personal] [--project DIR] [--root ~/.config/agent-profiles] [--keep SKILL ...]
"""

import argparse
import json
import os
import re
import sys
import tomllib
from pathlib import Path

HOME = Path.home()
SHARED_SKILLS = HOME / ".agents/skills"
GLOBAL_SKILL_ROOTS = [
    SHARED_SKILLS,
    HOME / ".claude/skills",
    HOME / ".config/opencode/skills",
    HOME / ".codex/skills",
]
PROJECT_SKILL_DIRS = [
    ".agents/skills",
    ".claude/skills",
    ".opencode/skills",
    ".codex/skills",
]

CLAUDE_KEYS = [
    "$schema",
    "model",
    "effortLevel",
    "modelSettings",
    "theme",
    "tui",
    "verbose",
    "showThinkingSummaries",
    "promptSuggestionEnabled",
    "switchModelsOnFlag",
    "enableWorkflows",
    "permissions",
    "hooks",
]
CODEX_KEYS = ["model", "model_reasoning_effort", "service_tier"]
OPENCODE_KEYS = [
    "model",
    "agents",
    "default_agent",
    "snapshots",
    "formatter",
    "plugins",
    "compaction",
    "experimental",
]

BEGIN = "# BEGIN agent_profile.py: global skills, regenerated on every run"
END = "# END agent_profile.py"

OPENCODE_WRAPPER = """#!/bin/sh
self=$(cd "$(dirname "$0")" && pwd)
PATH=$(printf '%s' "$PATH" | tr ':' '\\n' | grep -vxF "$self" | paste -sd: -)
case "$1" in
  service | upgrade | update | uninstall) exec opencode "$@" ;;
esac
exec opencode --standalone "$@"
"""


def write(path: Path, text: str, mode: int | None = None) -> None:
    """Write atomically, and only when the content changes."""
    if path.exists() and path.read_text() == text:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(text)
    if mode is not None:
        tmp.chmod(mode)
    os.replace(tmp, path)
    print(f"agent_profile: wrote {path}", file=sys.stderr)


def skill_name(skill_md: Path) -> str:
    match = re.search(
        r"(?m)^name:\s*['\"]?([^'\"\n]+?)['\"]?\s*$",
        skill_md.read_text(errors="ignore")[:2000],
    )
    return match.group(1) if match else skill_md.parent.name


def skills(root: Path) -> list[Path]:
    """SKILL.md files one level below root, skipping hidden dirs such as Codex's bundled .system."""
    if not root.is_dir():
        return []
    return sorted(
        p / "SKILL.md"
        for p in root.iterdir()
        if not p.name.startswith(".") and (p / "SKILL.md").is_file()
    )


def read_jsonc(path: Path) -> dict:
    if not path.is_file():
        return {}
    text = re.sub(r"(?m)^\s*//.*$", "", path.read_text())
    return json.loads(re.sub(r",(\s*[}\]])", r"\1", text))


def pick(source: dict, keys: list[str]) -> dict:
    return {k: source[k] for k in keys if k in source}


def seed(profile: Path, project: Path | None) -> None:
    claude = profile / "claude/settings.json"
    if not claude.exists():
        settings = pick(read_jsonc(HOME / ".claude/settings.json"), CLAUDE_KEYS)
        write(claude, json.dumps(settings, indent=2) + "\n")

    opencode = profile / "opencode/opencode.jsonc"
    if not opencode.exists():
        config = {"$schema": "https://opencode.ai/config.json"}
        config |= pick(
            read_jsonc(HOME / ".config/opencode/opencode.jsonc"), OPENCODE_KEYS
        )
        write(opencode, json.dumps(config, indent=4) + "\n")

    codex = profile / "codex/config.toml"
    if not codex.exists():
        global_config = HOME / ".codex/config.toml"
        base = (
            tomllib.loads(global_config.read_text()) if global_config.is_file() else {}
        )
        lines = [
            f"{k} = {json.dumps(v)}"
            for k, v in pick(base, CODEX_KEYS).items()
            if isinstance(v, str)
        ]
        write(codex, "\n".join(lines) + "\n")
    text = codex.read_text()
    if project and f'[projects."{project}"]' not in text:
        write(
            codex,
            text.rstrip("\n")
            + f'\n\n[projects."{project}"]\ntrust_level = "trusted"\n',
        )


def global_skills() -> dict[str, Path]:
    """Global skill dirs by name; the first root wins."""
    found: dict[str, Path] = {}
    for root in GLOBAL_SKILL_ROOTS:
        for p in skills(root):
            found.setdefault(skill_name(p), p.parent)
    return found


def link_skills(skills_dir: Path, wanted: dict[str, Path]) -> None:
    """Make the symlinks in skills_dir exactly `wanted`; leave anything that isn't a symlink alone."""
    skills_dir.mkdir(parents=True, exist_ok=True)
    for link in skills_dir.iterdir():
        if link.is_symlink() and (
            link.name not in wanted or link.readlink() != wanted[link.name]
        ):
            link.unlink()
            print(f"agent_profile: unlinked {link}", file=sys.stderr)
    for name, target in wanted.items():
        link = skills_dir / name
        if not link.exists() and not link.is_symlink():
            link.symlink_to(target)
            print(f"agent_profile: linked {link}", file=sys.stderr)


def kept(keep: set[str], outside_shared: bool = False) -> dict[str, Path]:
    """The kept global skills by name; with outside_shared, only those not in ~/.agents/skills."""
    shared = {skill_name(p) for p in skills(SHARED_SKILLS)}
    return {
        n: d
        for n, d in global_skills().items()
        if n in keep and not (outside_shared and n in shared)
    }


def sync_claude(profile: Path, keep: set[str]) -> None:
    """Link the kept global skills into the profile.

    Claude Code also loads ~/.claude/CLAUDE.md as the CLAUDE.md of an ancestor dir of any project under ~.
    """
    link_skills(profile / "claude/skills", kept(keep))

    path = profile / "claude/settings.json"
    settings = json.loads(path.read_text())
    excludes = settings.setdefault("claudeMdExcludes", [])
    for p in (HOME / ".claude/CLAUDE.md", HOME / "CLAUDE.md"):
        if str(p) not in excludes:
            excludes.append(str(p))
    write(path, json.dumps(settings, indent=2) + "\n")


def without_block(text: str) -> str:
    """The text without this script's block, keeping anything Codex added inside it.

    Codex inserts the tables it adds itself (e.g. [projects."…"]) just before the file's last comment line, so the
    block at the end of the file can collect them; they are moved out, not dropped.
    """
    match = re.search(rf"(?ms)^{re.escape(BEGIN)}\n(.*?)^{re.escape(END)}\n?", text)
    if not match:
        return text.rstrip("\n") + "\n"
    lines, foreign, i = match.group(1).splitlines(), [], 0
    while i < len(lines):
        if lines[i].strip() == "[[skills.config]]":
            j = i + 1
            while j < len(lines) and not lines[j].lstrip().startswith("["):
                j += 1
            body = [line for line in lines[i + 1 : j] if line.strip()]
            if (
                len(body) == 2
                and body[0].startswith("path = ")
                and body[1] in ("enabled = true", "enabled = false")
            ):
                i = j
                continue
        foreign.append(lines[i])
        i += 1
    rest = (text[: match.start()] + text[match.end() :]).rstrip("\n")
    moved = "\n".join(foreign).strip("\n")
    return "\n\n".join(part for part in (rest, moved) if part) + "\n"


def sync_codex(profile: Path, keep: set[str]) -> None:
    """Disable each ~/.agents/skills skill by path, except kept ones; enable kept skills found elsewhere.

    Codex reads the other global roots from CODEX_HOME only.
    """
    path = profile / "codex/config.toml"
    disabled = [p for p in skills(SHARED_SKILLS) if skill_name(p) not in keep]
    enabled = [d / "SKILL.md" for d in kept(keep, outside_shared=True).values()]
    entries = "".join(
        f"[[skills.config]]\npath = {json.dumps(str(p))}\nenabled = false\n\n"
        for p in disabled
    )
    entries += "".join(
        f"[[skills.config]]\npath = {json.dumps(str(p))}\nenabled = true\n\n"
        for p in enabled
    )
    new = without_block(path.read_text()) + f"\n{BEGIN}\n{entries}{END}\n"
    tomllib.loads(new)
    write(path, new)


def project_skills(project: Path | None) -> set[str]:
    if not project:
        return set()
    return {skill_name(p) for d in PROJECT_SKILL_DIRS for p in skills(project / d)}


def sync_opencode(profile: Path, keep: set[str], own: set[str]) -> None:
    """Deny every global skill by name, except kept ones and names the project ships itself.

    Kept skills outside ~/.agents/skills are linked into the profile, which OpenCode reads instead of ~/.config/opencode.
    """
    link_skills(profile / "opencode/skills", kept(keep, outside_shared=True))
    names = sorted(set(global_skills()) - keep - own)
    config = {
        "$schema": "https://opencode.ai/config.json",
        "policies": [
            {"action": "skill.use", "resource": n, "effect": "deny"} for n in names
        ],
    }
    write(profile / "opencode/opencode.json", json.dumps(config, indent=4) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--profile", default="personal")
    parser.add_argument(
        "--project", help="project dir: its skills stay, and Codex trusts it"
    )
    parser.add_argument("--root", default=str(HOME / ".config/agent-profiles"))
    parser.add_argument(
        "--keep",
        nargs="*",
        default=[],
        metavar="SKILL",
        help="global skills to keep, unless the project ships a skill of the same name",
    )
    args = parser.parse_args()
    profile = Path(args.root).expanduser() / args.profile
    project = Path(args.project).expanduser().resolve() if args.project else None
    own = project_skills(project)
    keep = set(args.keep) - own

    seed(profile, project)
    sync_claude(profile, keep)
    sync_codex(profile, keep)
    sync_opencode(profile, keep, own)
    write(profile / "bin/opencode", OPENCODE_WRAPPER, mode=0o755)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Keep a Markdown instructions file in every harness's GLOBAL instruction file, as a block marked with the source
path that this script owns; content outside the markers (incl. other sources' blocks) is never touched.

    ~/.claude/CLAUDE.md            Claude Code
    ~/.config/opencode/AGENTS.md   OpenCode
    ~/.codex/AGENTS.md             Codex
    ~/.gemini/GEMINI.md            Gemini CLI / Antigravity

Several projects can each sync their own instructions file; a block is identified by the file's path (with ~ for
the home directory), so after moving or renaming the file, `remove` with the old path and `sync` with the new one.

Only harnesses whose config dir exists are touched; a missing instruction file is created.

Usage: global_instructions.py {sync,remove,status} [--instructions-file PATH]
    sync    add the block if absent, replace it if the instructions changed (idempotent)
    remove  delete the block (and the file, if nothing else is left in it)
    status  show per file: current / outdated / absent / no harness
"""

import argparse
import os
import sys
from pathlib import Path

TARGETS = [
    Path.home() / ".claude/CLAUDE.md",
    Path.home() / ".config/opencode/AGENTS.md",
    Path.home() / ".codex/AGENTS.md",
    Path.home() / ".gemini/GEMINI.md",
]


def display(path: Path) -> str:
    """The path with the home directory as ~, so markers don't depend on who reads them."""
    home = str(Path.home())
    return (
        "~" + str(path)[len(home) :]
        if str(path).startswith(home + os.sep)
        else str(path)
    )


class Block:
    def __init__(self, source: Path):
        self.source = source
        self.begin_prefix = f"<!-- BEGIN global_instructions.py {display(source)} "
        self.begin = f"{self.begin_prefix}(managed by ~/Projects/dima/scripts/global_instructions.py: edit that file) -->"
        self.end = f"<!-- END global_instructions.py {display(source)} -->"

    def text(self) -> str:
        return f"{self.begin}\n{self.source.read_text().rstrip(chr(10))}\n{self.end}\n"

    def split(self, text: str) -> tuple[str, str | None]:
        """(the text without our block, trailing blank lines trimmed; our block or None)."""
        lines = text.splitlines(keepends=True)
        start = next(
            (i for i, line in enumerate(lines) if line.startswith(self.begin_prefix)),
            None,
        )
        if start is None:
            return (text.rstrip("\n") + "\n" if text.strip() else ""), None
        end = next(
            (i for i in range(start, len(lines)) if lines[i].rstrip("\n") == self.end),
            len(lines) - 1,
        )
        rest = "".join(lines[:start] + lines[end + 1 :]).rstrip("\n")
        return (rest + "\n" if rest.strip() else ""), "".join(lines[start : end + 1])

    def state(self, path: Path) -> str:
        if not path.parent.is_dir():
            return "no harness"
        if not path.is_file():
            return "absent"
        _, current = self.split(path.read_text())
        if current is None:
            return "absent"
        return "current" if current == self.text() else "outdated"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sync an instructions file into the global harness instruction files."
    )
    parser.add_argument(
        "command", nargs="?", default="status", choices=["sync", "remove", "status"]
    )
    parser.add_argument(
        "--instructions-file",
        default="global-instructions.md",
        help="Markdown to keep in the global instruction files (default ./global-instructions.md)",
    )
    args = parser.parse_args()
    cmd = args.command
    source = Path(args.instructions_file).expanduser().resolve()
    if cmd != "remove" and not source.is_file():
        sys.exit(f"instructions file not found: {source}")
    block = Block(source)
    print(f"instructions file: {source}")

    for path in TARGETS:
        if cmd == "remove":
            rest, current = (
                block.split(path.read_text()) if path.is_file() else ("", None)
            )
            if current is None:
                print(f"{'absent':<10} {path}")
            elif rest.strip():
                path.write_text(rest)
                print(f"{'removed':<10} {path}")
            else:
                path.unlink()
                print(f"{'deleted':<10} {path} (only our block was in it)")
            continue
        s = block.state(path)
        if cmd == "status":
            print(f"{s:<10} {path}")
        elif s == "no harness":
            print(f"{'skip':<10} {path} (harness not installed)")
        elif s == "current":
            print(f"{'ok':<10} {path}")
        else:
            rest, _ = block.split(path.read_text()) if path.is_file() else ("", None)
            path.write_text(rest + ("\n" if rest else "") + block.text())
            print(f"{'added' if s == 'absent' else 'updated':<10} {path}")


if __name__ == "__main__":
    main()

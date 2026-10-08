"""Harness readers; all source access is read only."""

import pathlib
import typing

from dima.agent_cli_mcp.models import Conversation, Harness, Source

from .antigravity import read_antigravity
from .claude import read_claude
from .codex import read_codex
from .opencode import read_opencode


def read_file(source: Source, path: pathlib.Path) -> list[Conversation]:
    match source.harness:
        case Harness.claude_code:
            return [read_claude(source, path)]
        case Harness.codex:
            return [read_codex(source, path)]
        case Harness.opencode:
            return read_opencode(source, path)
        case Harness.antigravity:
            return [read_antigravity(source, path)]
        case _:
            typing.assert_never(source.harness)

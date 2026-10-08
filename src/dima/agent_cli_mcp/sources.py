"""Explicit source discovery and source-file change detection."""

import hashlib
import json
import os
import pathlib
import stat
import typing

import pydantic

from .models import Harness, Model, Source


class SourceFile(Model):
    path: pathlib.Path
    fallback: pathlib.Path | None = None
    companions: list[pathlib.Path] = pydantic.Field(default_factory=list)

    @property
    def key(self) -> str:
        return str(self.path)

    @property
    def fingerprint(self) -> str:
        paths = [self.path, *self.companions]
        paths += [
            pathlib.Path(str(path) + "-wal") for path in paths if path.suffix == ".db"
        ]
        if self.fallback:
            paths.append(self.fallback)
        stats: list[tuple[str, int | None] | tuple[str, int, int, int]] = []
        for path in paths:
            try:
                info = path.stat()
                stats.append((str(path), info.st_ino, info.st_size, info.st_mtime_ns))
            except FileNotFoundError:
                stats.append((str(path), None))
        return hashlib.sha256(json.dumps(stats).encode()).hexdigest()


def default_sources(home: pathlib.Path | None = None) -> list[Source]:
    explicit_home = home is not None
    home = home or pathlib.Path.home()
    claude = (
        home / ".claude"
        if explicit_home
        else pathlib.Path(os.environ.get("CLAUDE_CONFIG_DIR", home / ".claude"))
    )
    codex = (
        home / ".codex"
        if explicit_home
        else pathlib.Path(os.environ.get("CODEX_HOME", home / ".codex"))
    )
    opencode = (
        home / ".local/share/opencode"
        if explicit_home
        else pathlib.Path(os.environ.get("XDG_DATA_HOME", home / ".local/share"))
        / "opencode"
    )
    return [
        Source(harness=Harness.claude_code, path=claude),
        Source(harness=Harness.codex, path=codex),
        Source(harness=Harness.opencode, path=opencode),
        *[
            Source(harness=Harness.antigravity, path=home / ".gemini" / name)
            for name in ["antigravity", "antigravity-ide", "antigravity-cli"]
        ],
    ]


def discover(source: Source) -> list[SourceFile]:
    root = source.path
    # scandir raises on missing/inaccessible roots; do not infer an empty corpus.
    with os.scandir(root):
        pass
    match source.harness:
        case Harness.claude_code:
            return [
                SourceFile(path=path) for path in _walk(root / "projects", ".jsonl")
            ]
        case Harness.codex:
            return [
                SourceFile(path=path)
                for directory in ["sessions", "archived_sessions"]
                for path in _walk(root / directory, ".jsonl")
            ]
        case Harness.opencode:
            paths = [
                root / name
                for name in ["opencode.db", "opencode-next.db"]
                if _is_file(root / name)
            ]
            return [SourceFile(path=paths[0], companions=paths[1:])] if paths else []
        case Harness.antigravity:
            files: dict[str, SourceFile] = {}
            for path in _walk(root / "conversations", (".db", ".pb")):
                if path.suffix == ".db" or path.stem not in files:
                    files[path.stem] = SourceFile(path=path)
            for path in _walk(root / "brain", ".jsonl"):
                if (
                    path.name != "transcript.jsonl"
                    or path.parent.name != "logs"
                    or path.parents[1].name != ".system_generated"
                ):
                    continue
                native = path.parents[2].name
                if native in files and files[native].path.suffix == ".db":
                    files[native].fallback = path
                else:
                    files[native] = SourceFile(path=path)
            return list(files.values())
        case _:
            typing.assert_never(source.harness)


def _walk(root: pathlib.Path, suffix: str | tuple[str, ...]) -> list[pathlib.Path]:
    try:
        info = root.stat()
    except FileNotFoundError:
        return []
    if not stat.S_ISDIR(info.st_mode):
        raise ValueError("Expected a harness source directory")

    def raise_error(error: OSError) -> typing.NoReturn:
        raise error

    paths: list[pathlib.Path] = []
    for directory, _, files in os.walk(root, onerror=raise_error):
        paths.extend(
            pathlib.Path(directory) / name for name in files if name.endswith(suffix)
        )
    return sorted(paths)


def _is_file(path: pathlib.Path) -> bool:
    try:
        info = path.stat()
    except FileNotFoundError:
        return False
    return stat.S_ISREG(info.st_mode)

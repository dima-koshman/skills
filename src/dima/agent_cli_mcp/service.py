"""Source synchronization and serialized access to the shared retrieval cache."""

import datetime
import hashlib
import json
import pathlib
import sqlite3
import threading
import time
import typing
from collections.abc import Callable
from typing import Self

from .adapters import read_file
from .adapters.common import optional_string, read_jsonl
from .models import (
    Conversation,
    Coverage,
    Harness,
    ListRequest,
    ListResult,
    ReadRequest,
    ReadResult,
    SearchRequest,
    SearchResult,
    Source,
)
from .sources import SourceFile, discover
from .store import Store


class Service:
    def __init__(
        self,
        *,
        index_path: pathlib.Path,
        sources: list[Source],
        refresh_seconds: float = 5,
    ):
        if any(
            index_path.resolve().is_relative_to(source.path.resolve())
            for source in sources
        ):
            raise ValueError("The index must be outside every harness source directory")
        self.store: Store = Store(index_path)
        self.store.source_ids = [source.source_id for source in sources]
        self.sources: list[Source] = sources
        self._refresh_seconds: float = refresh_seconds
        self._checked_at: float | None = None
        self._lock: threading.RLock = threading.RLock()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def close(self) -> None:
        with self._lock:
            self.store.close()

    def refresh(self) -> None:
        with self._lock:
            if (
                self._checked_at is not None
                and time.monotonic() - self._checked_at < self._refresh_seconds
            ):
                return
            for source in self.sources:
                self._refresh_source(source)
            self._checked_at = time.monotonic()

    def _refresh_source(self, source: Source) -> None:
        previous = next(
            (
                entry
                for entry in self.store.coverage()
                if entry.source_id == source.source_id
            ),
            None,
        )
        coverage = Coverage(
            source_id=source.source_id,
            harness=source.harness,
            path=str(source.path),
            status="ready",
            last_indexed_at=previous.last_indexed_at if previous else None,
        )
        try:
            files = discover(source)
        except (OSError, ValueError) as error:
            coverage.status = (
                "missing" if isinstance(error, FileNotFoundError) else "error"
            )
            coverage.limitations = [
                f"Source unavailable ({type(error).__name__}); cached chats retained"
            ]
            self.store.set_coverage(coverage)
            return
        known = self.store.files(source.source_id)
        titles, title_fingerprint, title_warnings = _codex_titles(source)
        coverage.limitations.extend(title_warnings)
        for file in files:
            try:
                fingerprint = file.fingerprint + title_fingerprint
                if known.get(file.key) != fingerprint:
                    conversations, warnings = _read_with_fallback(source, file)
                    for conversation in conversations:
                        if conversation.chat.native_session_id in titles:
                            conversation.chat.title = titles[
                                conversation.chat.native_session_id
                            ]
                            conversation.chat.title_source = "native"
                        warnings.extend(conversation.limitations)
                    self.store.replace_file(
                        source.source_id,
                        file.key,
                        fingerprint,
                        conversations,
                        sorted(set(warnings)),
                    )
                coverage.limitations.extend(
                    self.store.file_limitations(source.source_id, file.key)
                )
            except (OSError, ValueError, sqlite3.Error, TypeError, KeyError) as error:
                coverage.limitations.append(
                    f"Could not read {file.path.name} ({type(error).__name__}); cached chats retained"
                )
                if file.path.suffix == ".pb":
                    coverage.limitations.append(
                        "Legacy Antigravity .pb histories are unsupported"
                    )
        present = {file.key for file in files}
        for key in known.keys() - present:
            self.store.remove_file(source.source_id, key)
        coverage.limitations = sorted(set(coverage.limitations))
        coverage.status = "partial" if coverage.limitations else "ready"
        coverage.last_indexed_at = (
            datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z")
        )
        self.store.set_coverage(coverage)

    def list_chats(self, request: ListRequest) -> ListResult:
        return self._query(lambda: self.store.list_chats(request))

    def search_chats(self, request: SearchRequest) -> SearchResult:
        return self._query(lambda: self.store.search_chats(request))

    def read_chat(self, request: ReadRequest) -> ReadResult:
        return self._query(lambda: self.store.read_chat(request))

    def _query(self, run: Callable[[], "_ResultT"]) -> "_ResultT":
        with self._lock:
            self.refresh()
            # Other MCP processes can refresh the same index. Bind cursor
            # validation, results, and coverage to one SQLite read snapshot.
            with self.store.connection:
                _ = self.store.connection.execute("BEGIN")
                result = run()
                result.coverage = self.store.coverage()
                return result


_ResultT = typing.TypeVar("_ResultT", ListResult, SearchResult, ReadResult)


def _read_with_fallback(
    source: Source, file: SourceFile
) -> tuple[list[Conversation], list[str]]:
    if source.harness == Harness.opencode:
        conversations: dict[str, Conversation] = {}
        for path in [file.path, *file.companions]:
            for conversation in read_file(source, path):
                conversations[conversation.chat.native_session_id] = conversation
        return list(conversations.values()), []
    try:
        return read_file(source, file.path), []
    except (OSError, ValueError, sqlite3.Error):
        if file.fallback is None:
            raise
        return read_file(source, file.fallback), [
            "Antigravity SQLite unavailable; generated transcript used instead"
        ]


def _codex_titles(source: Source) -> tuple[dict[str, str], str, list[str]]:
    if source.harness != Harness.codex:
        return {}, "", []
    path = source.path / "session_index.jsonl"
    try:
        rows, warnings = read_jsonl(path)
        titles: dict[str, str] = {}
        for row in rows:
            native = optional_string(row.get("id"))
            title = optional_string(row.get("thread_name"))
            if native and title:
                titles[native] = title
        digest = hashlib.sha256(json.dumps(titles, sort_keys=True).encode()).hexdigest()
        return titles, digest, warnings
    except FileNotFoundError:
        return {}, "", []
    except (OSError, ValueError):
        return {}, "", ["Codex session title index unavailable"]

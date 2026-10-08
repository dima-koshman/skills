"""Transactional normalized conversation storage and FTS5 retrieval."""

import json
import pathlib
import re
import sqlite3
import typing
from collections.abc import Iterable, Sequence
from typing import Self

from .cursors import Cursors, RequestT
from .models import (
    Chat,
    ChatError,
    Conversation,
    Coverage,
    Filters,
    Hit,
    Item,
    ListRequest,
    Model,
    ListResult,
    ReadRequest,
    ReadResult,
    SearchRequest,
    SearchResult,
)

_SCHEMA = """
PRAGMA foreign_keys=ON;
PRAGMA journal_mode=WAL;
PRAGMA busy_timeout=5000;
CREATE TABLE IF NOT EXISTS metadata (revision INTEGER NOT NULL);
INSERT INTO metadata SELECT 0 WHERE NOT EXISTS (SELECT 1 FROM metadata);
CREATE TABLE IF NOT EXISTS sources (id TEXT PRIMARY KEY, data TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS source_files (
    source_id TEXT NOT NULL, file_key TEXT NOT NULL, fingerprint TEXT NOT NULL,
    limitations TEXT NOT NULL, PRIMARY KEY(source_id,file_key)
);
CREATE TABLE IF NOT EXISTS chats (
    id TEXT PRIMARY KEY, source_id TEXT NOT NULL, file_key TEXT NOT NULL,
    fingerprint TEXT NOT NULL, harness TEXT NOT NULL, directory TEXT,
    title TEXT NOT NULL, created_at TEXT, updated_at TEXT, parent_id TEXT,
    archived INTEGER, data TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS chats_source ON chats(source_id,file_key);
CREATE INDEX IF NOT EXISTS chats_directory ON chats(directory);
CREATE TABLE IF NOT EXISTS items (
    rowid INTEGER PRIMARY KEY, id TEXT UNIQUE NOT NULL,
    chat_id TEXT NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
    ordinal INTEGER NOT NULL, kind TEXT NOT NULL, text TEXT NOT NULL,
    data TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS items_chat ON items(chat_id,ordinal);
CREATE VIRTUAL TABLE IF NOT EXISTS items_fts USING fts5(
    text, content='items', content_rowid='rowid', tokenize='unicode61'
);
CREATE TRIGGER IF NOT EXISTS items_insert AFTER INSERT ON items BEGIN
    INSERT INTO items_fts(rowid,text) VALUES(new.rowid,new.text);
END;
CREATE TRIGGER IF NOT EXISTS items_delete AFTER DELETE ON items BEGIN
    INSERT INTO items_fts(items_fts,rowid,text) VALUES('delete',old.rowid,old.text);
END;
"""


class Store:
    """Own one SQLite connection; callers serialize access to this instance."""

    def __init__(self, path: pathlib.Path):
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        if not path.exists():
            path.touch(mode=0o600)
        self.connection: sqlite3.Connection = sqlite3.connect(
            path, check_same_thread=False
        )
        self.connection.row_factory = sqlite3.Row
        _ = self.connection.executescript(_SCHEMA)
        self._cursors: Cursors = Cursors()
        self.source_ids: list[str] | None = None

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def close(self) -> None:
        self.connection.close()

    @property
    def revision(self) -> int:
        return typing.cast(int, self._row("SELECT revision FROM metadata")[0])

    def put(
        self,
        chat: Chat,
        items: list[Item],
        *,
        source_id: str,
        file_key: str,
        fingerprint: str,
    ) -> None:
        with self.connection:
            self._put(
                chat,
                items,
                source_id=source_id,
                file_key=file_key,
                fingerprint=fingerprint,
            )
            _ = self.connection.execute(
                "INSERT OR REPLACE INTO source_files VALUES(?,?,?,?)",
                (source_id, file_key, fingerprint, "[]"),
            )
            _ = self.connection.execute("UPDATE metadata SET revision=revision+1")

    def _put(
        self,
        chat: Chat,
        items: list[Item],
        *,
        source_id: str,
        file_key: str,
        fingerprint: str,
    ) -> None:
        _ = self.connection.execute("DELETE FROM chats WHERE id=?", (chat.chat_id,))
        _ = self.connection.execute(
            "INSERT INTO chats VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                chat.chat_id,
                source_id,
                file_key,
                fingerprint,
                chat.harness,
                chat.directory,
                chat.title,
                chat.created_at,
                chat.updated_at,
                chat.parent_chat_id,
                chat.archived,
                chat.model_dump_json(),
            ),
        )
        _ = self.connection.executemany(
            "INSERT INTO items(id,chat_id,ordinal,kind,text,data) VALUES(?,?,?,?,?,?)",
            [
                (
                    item.item_id,
                    chat.chat_id,
                    i,
                    item.kind,
                    item.text,
                    item.model_dump_json(),
                )
                for i, item in enumerate(items)
            ],
        )

    def replace_file(
        self,
        source_id: str,
        file_key: str,
        fingerprint: str,
        conversations: list[Conversation],
        limitations: list[str],
    ) -> None:
        """Atomically publish a file; unchanged conversations retain their revision."""
        with self.connection:
            old = {
                _text(row, "id"): _text(row, "data")
                for row in self._rows(
                    "SELECT id,data FROM chats WHERE source_id=? AND file_key=?",
                    (source_id, file_key),
                )
            }
            present = {entry.chat.chat_id for entry in conversations}
            changed = False
            for conversation in conversations:
                chat, items = conversation.chat, conversation.items
                previous_items = (
                    [
                        _text(row, "data")
                        for row in self._rows(
                            "SELECT data FROM items WHERE chat_id=? ORDER BY ordinal",
                            (chat.chat_id,),
                        )
                    ]
                    if chat.chat_id in old
                    else []
                )
                if old.get(
                    chat.chat_id
                ) == chat.model_dump_json() and previous_items == [
                    item.model_dump_json() for item in items
                ]:
                    continue
                self._put(
                    chat,
                    items,
                    source_id=source_id,
                    file_key=file_key,
                    fingerprint=fingerprint,
                )
                changed = True
            for native in old.keys() - present:
                _ = self.connection.execute("DELETE FROM chats WHERE id=?", (native,))
                changed = True
            _ = self.connection.execute(
                "INSERT OR REPLACE INTO source_files VALUES(?,?,?,?)",
                (source_id, file_key, fingerprint, json.dumps(limitations)),
            )
            if changed:
                _ = self.connection.execute("UPDATE metadata SET revision=revision+1")

    def remove_file(self, source_id: str, file_key: str) -> None:
        with self.connection:
            count = self.connection.execute(
                "DELETE FROM chats WHERE source_id=? AND file_key=?",
                (source_id, file_key),
            ).rowcount
            _ = self.connection.execute(
                "DELETE FROM source_files WHERE source_id=? AND file_key=?",
                (source_id, file_key),
            )
            if count:
                _ = self.connection.execute("UPDATE metadata SET revision=revision+1")

    def files(self, source_id: str) -> dict[str, str]:
        return {
            _text(row, "file_key"): _text(row, "fingerprint")
            for row in self._rows(
                "SELECT file_key,fingerprint FROM source_files WHERE source_id=?",
                (source_id,),
            )
        }

    def file_limitations(self, source_id: str, file_key: str) -> list[str]:
        rows = self._rows(
            "SELECT limitations FROM source_files WHERE source_id=? AND file_key=?",
            (source_id, file_key),
        )
        return (
            typing.cast(list[str], json.loads(_text(rows[0], "limitations")))
            if rows
            else []
        )

    def set_coverage(self, coverage: Coverage) -> None:
        coverage.indexed_chats = typing.cast(
            int,
            self._row(
                "SELECT count(*) FROM chats WHERE source_id=?", (coverage.source_id,)
            )[0],
        )
        with self.connection:
            _ = self.connection.execute(
                "INSERT OR REPLACE INTO sources VALUES(?,?)",
                (coverage.source_id, coverage.model_dump_json()),
            )

    def coverage(self) -> list[Coverage]:
        return [
            Coverage.model_validate_json(_text(row, "data"))
            for row in self._rows("SELECT id,data FROM sources ORDER BY id")
            if self.source_ids is None or _text(row, "id") in self.source_ids
        ]

    def _rows(self, sql: str, parameters: Sequence[object] = ()) -> list[sqlite3.Row]:
        return typing.cast(
            list[sqlite3.Row], self.connection.execute(sql, parameters).fetchall()
        )

    def _row(self, sql: str, parameters: Sequence[object] = ()) -> sqlite3.Row:
        """Fetch a row the query always produces, such as an aggregate."""
        return self._rows(sql, parameters)[0]

    def _filters(self, request: Filters) -> tuple[str, list[object]]:
        where, args = _filters(request)
        if self.source_ids is not None:
            where += f" AND c.source_id IN ({_placeholders(self.source_ids)})"
            args.extend(self.source_ids)
        return where, args

    def _request(
        self, method: str, request: RequestT, cursor: str | None
    ) -> tuple[RequestT, dict[str, int]]:
        if cursor:
            return self._cursors.decode(cursor, method, self.revision, request)
        return request, {}

    def _cursor(self, method: str, request: Model, **position: int) -> str:
        return self._cursors.encode(method, self.revision, request, position)

    def list_chats(self, request: ListRequest) -> ListResult:
        request, position = self._request("list", request, request.cursor)
        where, args = self._filters(request)
        if request.title_contains is not None:
            where += " AND instr(lower(c.title),lower(?))>0"
            args.append(request.title_contains)
        sort = "updated_at" if request.sort == "updated_desc" else "created_at"
        offset = position.get("offset", 0)
        rows = self._rows(
            f"SELECT c.data FROM chats c WHERE {where} ORDER BY c.{sort} DESC,c.id LIMIT ? OFFSET ?",
            [*args, request.limit + 1, offset],
        )
        return ListResult(
            chats=[
                Chat.model_validate_json(_text(row, "data"))
                for row in rows[: request.limit]
            ],
            next_cursor=self._cursor("list", request, offset=offset + request.limit)
            if len(rows) > request.limit
            else None,
        )

    def search_chats(self, request: SearchRequest) -> SearchResult:
        request, position = self._request("search", request, request.cursor)
        expression = _expression(request.query, request.match)
        where, args = self._filters(request)
        if request.chat_ids is not None:
            where += f" AND c.id IN ({_placeholders(request.chat_ids)})"
            args.extend(request.chat_ids)
        where += f" AND i.kind IN ({_placeholders(request.content_types)})"
        args.extend(request.content_types)
        offset = position.get("offset", 0)
        rows = self._rows(
            f"""SELECT c.data AS chat,i.data AS item,i.text,
                snippet(items_fts,0,'','',' … ',48) AS excerpt
                FROM items_fts JOIN items i ON i.rowid=items_fts.rowid
                JOIN chats c ON c.id=i.chat_id
                WHERE items_fts MATCH ? AND {where}
                ORDER BY bm25(items_fts),i.id LIMIT ? OFFSET ?""",
            [expression, *args, request.limit + 1, offset],
        )
        hits: list[Hit] = []
        for row in rows[: request.limit]:
            chat = Chat.model_validate_json(_text(row, "chat"))
            item = Item.model_validate_json(_text(row, "item"))
            # FTS's ellipsis joins disjoint excerpts. Return one exact source span.
            excerpt = _text(row, "excerpt").split(" … ")[0]
            hits.append(
                Hit(
                    chat_id=chat.chat_id,
                    harness=chat.harness,
                    title=chat.title,
                    item_id=item.item_id,
                    kind=item.kind,
                    role=item.role,
                    timestamp=item.timestamp,
                    snippet=excerpt[:500],
                )
            )
        return SearchResult(
            hits=hits,
            next_cursor=self._cursor("search", request, offset=offset + request.limit)
            if len(rows) > request.limit
            else None,
        )

    def read_chat(self, request: ReadRequest) -> ReadResult:
        request, position = self._request("read", request, request.cursor)
        restriction = (
            f" AND source_id IN ({_placeholders(self.source_ids)})"
            if self.source_ids is not None
            else ""
        )
        rows = self._rows(
            f"SELECT data FROM chats WHERE id=?{restriction}",
            [request.chat_id, *(self.source_ids or [])],
        )
        if not rows:
            raise ChatError(
                "CHAT_NOT_FOUND", "No indexed conversation has this chat_id"
            )
        chat = Chat.model_validate_json(_text(rows[0], "data"))
        items = [
            Item.model_validate_json(_text(row, "data"))
            for row in self._rows(
                f"SELECT data FROM items WHERE chat_id=? AND kind IN ({_placeholders(request.content_types)}) ORDER BY ordinal",
                [request.chat_id, *request.content_types],
            )
        ]
        if position:
            start, end, offset = (
                position["start"],
                position["end"],
                position.get("offset", 0),
            )
        elif request.anchor_item_id:
            anchor = next(
                (
                    i
                    for i, item in enumerate(items)
                    if item.item_id == request.anchor_item_id
                ),
                None,
            )
            if anchor is None:
                raise ChatError(
                    "ITEM_NOT_FOUND",
                    "The anchor is absent from this conversation or excluded by content_types",
                )
            start, end, offset = (
                max(0, anchor - request.before),
                min(len(items), anchor + request.after + 1),
                0,
            )
        else:
            start, end, offset = max(0, len(items) - 20), len(items), 0
        output: list[Item] = []
        budget = request.max_chars
        current = start
        while current < end and budget:
            item = items[current]
            remaining = item.text[offset:]
            text = remaining[:budget]
            output.append(
                item.model_copy(
                    update={
                        "text": text,
                        "offset": offset,
                        "total_chars": len(item.text),
                    }
                )
            )
            budget -= len(text)
            if len(text) < len(remaining):
                offset += len(text)
                break
            current += 1
            offset = 0
        older = (
            self._cursor("read", request, start=max(0, start - 20), end=start)
            if start
            else None
        )
        if current < end:
            newer = self._cursor("read", request, start=current, end=end, offset=offset)
        elif end < len(items):
            newer = self._cursor(
                "read", request, start=end, end=min(len(items), end + 20)
            )
        else:
            newer = None
        return ReadResult(
            chat=chat, items=output, older_cursor=older, newer_cursor=newer
        )


def _placeholders(values: Iterable[object]) -> str:
    return ",".join("?" for _ in values)


def _text(row: sqlite3.Row, column: str) -> str:
    """Read a TEXT column of the index schema."""
    return typing.cast(str, row[column])


def _filters(request: Filters) -> tuple[str, list[object]]:
    clauses: list[str] = ["1=1"]
    args: list[object] = []
    if request.harnesses:
        clauses.append(f"c.harness IN ({_placeholders(request.harnesses)})")
        args.extend(request.harnesses)
    if not request.include_subagents:
        clauses.append("c.parent_id IS NULL")
    if not request.include_archived:
        clauses.append("coalesce(c.archived,0)=0")
    if request.directory:
        if request.directory_scope == "exact":
            clauses.append("c.directory=?")
            args.append(request.directory)
        else:
            prefix = request.directory.rstrip("/") + "/"
            clauses.append("(c.directory=? OR substr(c.directory,1,?)=?)")
            args.extend([request.directory, len(prefix), prefix])
    return " AND ".join(clauses), args


def _expression(query: str | None, match: str) -> str:
    if not query or not query.strip():
        raise ChatError("INVALID_QUERY", "Provide search words or quoted phrases")
    if query.count('"') % 2:
        raise ChatError("INVALID_QUERY", "Close the quoted phrase")
    parts = typing.cast(
        list[tuple[str, str]], re.findall(r'"([^"]*)"|([^\s"]+)', query)
    )
    terms = [phrase or word for phrase, word in parts]
    if not terms or any(not re.search(r"\w", term) for term in terms):
        raise ChatError("INVALID_QUERY", "Each search term must contain a word")
    return (" AND " if match == "all" else " OR ").join(
        '"' + term.replace('"', '""') + '"' for term in terms
    )

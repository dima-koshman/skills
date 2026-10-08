"""The public conversation tool contract and normalized source records."""

import datetime
import enum
import hashlib
import json
import pathlib
from typing import ClassVar, Literal, Self

import pydantic


class Harness(enum.StrEnum):
    claude_code = enum.auto()
    codex = enum.auto()
    opencode = enum.auto()
    antigravity = enum.auto()


class Kind(enum.StrEnum):
    message = enum.auto()
    tool_call = enum.auto()
    tool_result = enum.auto()
    summary = enum.auto()
    thinking = enum.auto()
    artifact = enum.auto()


class Model(pydantic.BaseModel):
    model_config: ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="forbid")


class Chat(Model):
    chat_id: str
    harness: Harness
    native_session_id: str
    title: str
    title_source: Literal["native", "first_message", "session_id"] = "native"
    directory: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    parent_chat_id: str | None = None
    forked_from_chat_id: str | None = None
    archived: bool | None = None


Role = Literal["user", "assistant", "tool", "system"]


class Item(Model):
    item_id: str
    kind: Kind
    role: Role
    text: str
    timestamp: str | None = None
    tool_name: str | None = None
    tool_call_id: str | None = None
    offset: int = 0
    total_chars: int | None = None


class Coverage(Model):
    source_id: str
    harness: Harness
    path: str
    status: Literal["ready", "partial", "missing", "error", "indexing"]
    indexed_chats: int = 0
    last_indexed_at: str | None = None
    limitations: list[str] = pydantic.Field(default_factory=list)


class Source(Model):
    harness: Harness
    path: pathlib.Path

    @property
    def source_id(self) -> str:
        return opaque_id("source", self.harness, str(self.path.resolve()))


class Filters(Model):
    harnesses: list[Harness] | None = None
    directory: str | None = None
    directory_scope: Literal["exact", "descendants"] = "exact"
    include_subagents: bool = False
    include_archived: bool = True
    cursor: str | None = pydantic.Field(default=None, max_length=16384)

    @pydantic.field_validator("directory")
    @classmethod
    def _absolute_directory(cls, value: str | None) -> str | None:
        if value is not None:
            path = pathlib.Path(value).expanduser()
            if not path.is_absolute():
                raise ValueError("directory must be an absolute path")
            return str(path.resolve())
        return value

    @pydantic.field_validator("harnesses")
    @classmethod
    def _nonempty_harnesses(cls, value: list[Harness] | None) -> list[Harness] | None:
        if value == []:
            raise ValueError("omit harnesses to select all sources")
        return value


class ListRequest(Filters):
    title_contains: str | None = None
    sort: Literal["updated_desc", "created_desc"] = "updated_desc"
    limit: int = pydantic.Field(default=20, ge=1, le=100)


class SearchRequest(Filters):
    query: str | None = pydantic.Field(default=None, max_length=4096)
    match: Literal["all", "any"] = "all"
    chat_ids: list[str] | None = None
    content_types: list[Kind] = pydantic.Field(
        default_factory=lambda: [Kind.message, Kind.summary], min_length=1
    )
    limit: int = pydantic.Field(default=10, ge=1, le=50)


class ReadRequest(Model):
    chat_id: str | None = None
    anchor_item_id: str | None = None
    before: int = pydantic.Field(default=5, ge=0, le=100)
    after: int = pydantic.Field(default=5, ge=0, le=100)
    content_types: list[Kind] = pydantic.Field(
        default_factory=lambda: [Kind.message, Kind.summary], min_length=1
    )
    max_chars: int = pydantic.Field(default=12000, ge=1, le=50000)
    cursor: str | None = pydantic.Field(default=None, max_length=16384)

    @pydantic.model_validator(mode="after")
    def _requires_chat(self) -> Self:
        if not self.chat_id and not self.cursor:
            raise ValueError("chat_id is required unless continuing with a cursor")
        return self


class Hit(Model):
    chat_id: str
    harness: Harness
    title: str
    item_id: str
    kind: Kind
    role: str
    timestamp: str | None
    snippet: str


class ListResult(Model):
    chats: list[Chat]
    next_cursor: str | None = None
    coverage: list[Coverage] = pydantic.Field(default_factory=list)


class SearchResult(Model):
    hits: list[Hit]
    next_cursor: str | None = None
    coverage: list[Coverage] = pydantic.Field(default_factory=list)


class ReadResult(Model):
    chat: Chat
    items: list[Item]
    older_cursor: str | None = None
    newer_cursor: str | None = None
    coverage: list[Coverage] = pydantic.Field(default_factory=list)


class Conversation(Model):
    chat: Chat
    items: list[Item]
    limitations: list[str] = pydantic.Field(default_factory=list)


class ChatError(ValueError):
    """An actionable retrieval error, safe to return through MCP."""

    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")


def opaque_id(namespace: str, *parts: str) -> str:
    digest = hashlib.sha256(json.dumps(parts, ensure_ascii=False).encode()).hexdigest()
    return f"{namespace}_{digest[:32]}"


def timestamp(value: object) -> str | None:
    """Normalize source timestamps; unavailable or invalid times stay null."""
    try:
        if isinstance(value, (int, float)):
            seconds = value / 1000 if value > 100_000_000_000 else value
            date = datetime.datetime.fromtimestamp(seconds, datetime.UTC)
        elif isinstance(value, str):
            date = datetime.datetime.fromisoformat(value)
            if date.tzinfo is None:
                date = date.replace(tzinfo=datetime.UTC)
        else:
            return None
        return date.astimezone(datetime.UTC).isoformat().replace("+00:00", "Z")
    except (ValueError, OverflowError, OSError, TypeError):
        return None

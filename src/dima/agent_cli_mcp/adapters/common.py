"""Shared normalization of original text and tool content blocks."""

import json
import pathlib
import sqlite3
import typing

from dima.agent_cli_mcp.models import (
    Chat,
    Conversation,
    Item,
    Kind,
    Role,
    Source,
    opaque_id,
    timestamp,
)

JsonObject = dict[str, object]


def read_jsonl(path: pathlib.Path) -> tuple[list[JsonObject], list[str]]:
    rows: list[JsonObject] = []
    limitations: list[str] = []
    with path.open("rb") as stream:
        for number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                row = typing.cast(object, json.loads(line))
                if not isinstance(row, dict):
                    raise TypeError("object required")
                rows.append(typing.cast(JsonObject, row))
            except (ValueError, UnicodeDecodeError, TypeError):
                if not line.endswith(b"\n"):
                    limitations.append(
                        f"Incomplete final JSONL record at line {number}"
                    )
                    break
                raise ValueError(f"Malformed JSONL record at line {number}") from None
    return rows, limitations


def read_database(path: pathlib.Path) -> sqlite3.Connection:
    connection = sqlite3.connect(
        f"{path.resolve().as_uri()}?mode=ro", uri=True, timeout=5
    )
    connection.row_factory = sqlite3.Row
    _ = connection.execute("PRAGMA query_only=ON")
    _ = connection.execute("BEGIN")
    return connection


def query(connection: sqlite3.Connection, sql: str) -> list[JsonObject]:
    """Run a read query on a `read_database` connection, one object per row."""
    rows = typing.cast(list[sqlite3.Row], connection.execute(sql).fetchall())
    return [{key: typing.cast(object, row[key]) for key in row.keys()} for row in rows]


def load_json(value: object) -> object:
    """Parse a JSON document stored in a source column."""
    if not isinstance(value, (str, bytes)):
        raise ValueError("Unsupported source record shape: expected JSON text")  # noqa: TRY004 -- malformed source data, not a caller type error
    return typing.cast(object, json.loads(value))


def mapping(value: object) -> JsonObject:
    if not isinstance(value, dict):
        raise ValueError("Unsupported source record shape: expected an object")  # noqa: TRY004 -- malformed source data, not a caller type error
    return typing.cast(JsonObject, value)


def as_object(value: object) -> JsonObject | None:
    """Return the value as an object when it is one, without rejecting other shapes."""
    return typing.cast(JsonObject, value) if isinstance(value, dict) else None


def string(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("Unsupported source record shape: expected a string")  # noqa: TRY004 -- malformed source data, not a caller type error
    return value


def optional_string(value: object) -> str | None:
    return None if value is None else string(value)


def make_chat(
    source: Source,
    native_id: str,
    *,
    directory: str | None = None,
    title: str | None = None,
    created: object = None,
    updated: object = None,
    parent: str | None = None,
    fork: str | None = None,
    archived: bool | None = None,
) -> Chat:
    return Chat(
        chat_id=opaque_id("chat", source.source_id, native_id),
        harness=source.harness,
        native_session_id=native_id,
        title=title or native_id,
        title_source="native" if title else "session_id",
        directory=(
            str(pathlib.Path(directory).expanduser().resolve()) if directory else None
        ),
        created_at=timestamp(created),
        updated_at=timestamp(updated),
        archived=archived,
        parent_chat_id=opaque_id("chat", source.source_id, parent) if parent else None,
        forked_from_chat_id=opaque_id("chat", source.source_id, fork) if fork else None,
    )


def finish(chat: Chat, items: list[Item], limitations: list[str]) -> Conversation:
    if chat.title_source == "session_id":
        first = next(
            (
                item.text
                for item in items
                if item.kind == Kind.message and item.role == "user" and item.text
            ),
            None,
        )
        if first:
            chat.title = first[:120].replace("\n", " ")
            chat.title_source = "first_message"
    return Conversation(chat=chat, items=items, limitations=sorted(set(limitations)))


def text_content(value: object) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(
            _block_text(block) for block in typing.cast(list[object], value)
        )
    return json.dumps(value, ensure_ascii=False)


def blocks(
    chat_id: str, native_id: str, content: object, role: str, time: object = None
) -> tuple[list[Item], list[str]]:
    if isinstance(content, str):
        content = [{"type": "text", "text": content}]
    if not isinstance(content, list):
        return [], ["Unsupported message content shape"]
    items: list[Item] = []
    limitations: list[str] = []
    for index, entry in enumerate(typing.cast(list[object], content)):
        block = as_object(entry)
        if block is None:
            limitations.append("Unsupported non-object content block")
            continue
        typ = block.get("type")
        kind: Kind
        text: object
        tool_name: str | None = None
        tool_call_id: str | None = None
        match typ:
            case "text" | "input_text" | "output_text":
                kind, text = Kind.message, block.get("text", "")
            case "thinking" | "reasoning":
                kind, text = Kind.thinking, block.get("thinking", block.get("text", ""))
                if not text and (
                    block.get("encrypted_content") or block.get("signature")
                ):
                    limitations.append("Encrypted reasoning has no readable text")
            case "tool_use" | "tool-call":
                kind = Kind.tool_call
                tool_name = optional_string(block.get("name", block.get("toolName")))
                tool_call_id = optional_string(block.get("id", block.get("toolCallId")))
                text = text_content(block.get("input", block.get("args", {})))
            case "tool_result" | "tool-result":
                kind = Kind.tool_result
                tool_call_id = optional_string(
                    block.get("tool_use_id", block.get("toolCallId"))
                )
                tool_name = optional_string(block.get("toolName"))
                text = text_content(block.get("content", block.get("result", "")))
            case "tool":
                state = mapping(block.get("state", {}))
                name = optional_string(block.get("tool"))
                call = optional_string(block.get("callID"))
                items.append(
                    Item(
                        item_id=opaque_id(
                            "item", chat_id, native_id, str(index), "call"
                        ),
                        kind=Kind.tool_call,
                        role="assistant",
                        text=text_content(state.get("input", {})),
                        timestamp=timestamp(time),
                        tool_name=name,
                        tool_call_id=call,
                    )
                )
                if state.get("status") not in {"completed", "error"}:
                    continue
                kind, text, tool_name, tool_call_id = (
                    Kind.tool_result,
                    text_content(state.get("output", state.get("error", ""))),
                    name,
                    call,
                )
            case "compaction":
                kind, text = (
                    Kind.summary,
                    block.get("text", "Compaction boundary (summary text unavailable)"),
                )
            case "image" | "input_image" | "file" | "patch":
                kind, text = Kind.artifact, f"[{typ} attachment]"
                limitations.append(
                    f"{typ} attachment represented by a marker; binary content is not indexed"
                )
            case "step-start" | "step-finish" | "snapshot" | "agent" | "retry":
                continue
            case _:
                limitations.append(f"Unsupported content block type: {str(typ)[:80]}")
                continue
        if text:
            items.append(
                Item(
                    item_id=opaque_id("item", chat_id, native_id, str(index)),
                    kind=kind,
                    role="tool" if kind == Kind.tool_result else _role(role),
                    text=text_content(text),
                    timestamp=timestamp(time),
                    tool_name=tool_name,
                    tool_call_id=tool_call_id,
                )
            )
    return items, limitations


def _block_text(block: object) -> str:
    entry = as_object(block)
    if entry is None:
        return text_content(block)
    return text_content(entry.get("text", entry.get("content", "")))


def _role(value: str) -> Role:
    match value:
        case "user" | "assistant" | "tool" | "system":
            return value
        case _:
            return "system"

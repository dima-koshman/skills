"""Codex rollout records; response items are canonical, events are not duplicated."""

import pathlib

import typing

from dima.agent_cli_mcp.models import (
    Conversation,
    Item,
    Kind,
    Source,
    opaque_id,
    timestamp,
)

from .common import (
    JsonObject,
    as_object,
    blocks,
    finish,
    make_chat,
    mapping,
    optional_string,
    read_jsonl,
    string,
    text_content,
)


def read_codex(source: Source, path: pathlib.Path) -> Conversation:
    rows, limitations = read_jsonl(path)
    meta = mapping(
        next(
            (
                row.get("payload", JsonObject())
                for row in rows
                if row.get("type") == "session_meta"
            ),
            JsonObject(),
        )
    )
    native = string(meta.get("id", path.stem))
    source_kind = as_object(meta.get("source", {}))
    parent = None
    if source_kind is not None and "subagent" in source_kind:
        subagent = as_object(source_kind["subagent"])
        if subagent is not None:
            spawn = as_object(subagent.get("thread_spawn", subagent))
            if spawn is not None:
                parent = optional_string(
                    spawn.get("parent_thread_id", meta.get("parent_thread_id"))
                )
    chat = make_chat(
        source,
        native,
        directory=optional_string(meta.get("cwd")),
        title=optional_string(meta.get("name")),
        created=meta.get("timestamp"),
        updated=next(
            (row.get("timestamp") for row in reversed(rows) if row.get("timestamp")),
            None,
        ),
        parent=parent,
        fork=optional_string(meta.get("forked_from_id")),
        archived="archived_sessions" in path.parts,
    )
    items: list[Item] = []
    for index, row in enumerate(rows):
        payload, time = as_object(row.get("payload", {})), row.get("timestamp")
        if payload is None:
            limitations.append("Unsupported Codex record payload shape")
            continue
        record_type = row.get("type")
        native_item = str(row.get("ordinal", index))
        if record_type == "compacted":
            text = optional_string(payload.get("message"))
            if text:
                items.append(
                    Item(
                        item_id=opaque_id("item", chat.chat_id, native_item),
                        kind=Kind.summary,
                        role="system",
                        text=text,
                        timestamp=timestamp(time),
                    )
                )
            continue
        if record_type != "response_item":
            continue
        typ = payload.get("type")
        if typ == "message":
            role = str(payload.get("role", "system"))
            added, warnings = blocks(
                chat.chat_id, native_item, payload.get("content", []), role, time
            )
            if role in {"system", "developer"}:
                for item in added:
                    item.kind = Kind.artifact
            items.extend(added)
            limitations.extend(warnings)
        elif typ in {
            "function_call",
            "custom_tool_call",
            "function_call_output",
            "custom_tool_call_output",
        }:
            call = typ in {"function_call", "custom_tool_call"}
            text = (
                payload.get("arguments", payload.get("input", ""))
                if call
                else payload.get("output", "")
            )
            items.append(
                Item(
                    item_id=opaque_id("item", chat.chat_id, native_item),
                    kind=Kind.tool_call if call else Kind.tool_result,
                    role="assistant" if call else "tool",
                    text=text_content(text),
                    timestamp=timestamp(time),
                    tool_name=optional_string(payload.get("name")),
                    tool_call_id=optional_string(payload.get("call_id")),
                )
            )
        elif typ == "reasoning":
            summary = payload.get("summary", [])
            entries = (
                typing.cast(list[object], summary) if isinstance(summary, list) else []
            )
            text = "\n".join(
                string(block.get("text", ""))
                for entry in entries
                if (block := as_object(entry)) is not None
            )
            if text:
                items.append(
                    Item(
                        item_id=opaque_id("item", chat.chat_id, native_item),
                        kind=Kind.thinking,
                        role="assistant",
                        text=text,
                        timestamp=timestamp(time),
                    )
                )
        elif typ == "web_search_call":
            items.append(
                Item(
                    item_id=opaque_id("item", chat.chat_id, native_item),
                    kind=Kind.tool_call,
                    role="assistant",
                    text=text_content(payload.get("action", {})),
                    timestamp=timestamp(time),
                    tool_name="web_search",
                    tool_call_id=optional_string(payload.get("id")),
                )
            )
        else:
            limitations.append(f"Unsupported Codex response item type: {str(typ)[:80]}")
    return finish(chat, items, limitations)

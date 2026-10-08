"""Known Antigravity SQLite steps and generated JSONL transcript fallback."""

import pathlib

import google.protobuf.message

from dima.agent_cli_mcp.models import (
    Conversation,
    Item,
    Kind,
    Role,
    Source,
    opaque_id,
    timestamp,
)

from .antigravity_proto import parse_step
from .common import finish, make_chat, query, read_database, read_jsonl, text_content


def read_antigravity(source: Source, path: pathlib.Path) -> Conversation:
    if path.suffix == ".pb":
        raise ValueError(
            "Legacy Antigravity .pb conversation format is unsupported; no decryption is attempted"
        )
    if path.suffix == ".jsonl":
        return _transcript(source, path)
    if path.suffix != ".db":
        raise ValueError("Antigravity conversation format is unsupported")
    chat = make_chat(source, path.stem)
    items: list[Item] = []
    limitations: list[str] = []
    connection = read_database(path)
    try:
        for row in query(
            connection,
            "SELECT idx,step_type,status,step_payload,step_format FROM steps ORDER BY idx",
        ):
            native = str(row["idx"])
            if row["step_format"] != 0:
                limitations.append(
                    f"Unsupported Antigravity step_format {row['step_format']}"
                )
                continue
            raw = row["step_payload"]
            if not isinstance(raw, bytes) or len(raw) > 64 * 1024 * 1024:
                raise ValueError("Invalid or oversized Antigravity step payload")
            try:
                step = parse_step(raw)
            except google.protobuf.message.DecodeError:
                raise ValueError("Invalid Antigravity protobuf step") from None
            if step.type != row["step_type"] or step.status != row["status"]:
                raise ValueError("Antigravity row and protobuf step disagree")
            if step.type == 14 and step.HasField("user"):
                items.append(
                    Item(
                        item_id=opaque_id("item", chat.chat_id, native),
                        kind=Kind.message,
                        role="user",
                        text=step.user.text,
                    )
                )
            elif step.type == 15 and step.HasField("planner"):
                if step.planner.text:
                    items.append(
                        Item(
                            item_id=opaque_id("item", chat.chat_id, native),
                            kind=Kind.message,
                            role="assistant",
                            text=step.planner.text,
                        )
                    )
                for i, call in enumerate(step.planner.calls):
                    items.append(
                        Item(
                            item_id=opaque_id("item", chat.chat_id, native, str(i)),
                            kind=Kind.tool_call,
                            role="assistant",
                            text=call.arguments,
                            tool_name=call.name,
                            tool_call_id=call.id,
                        )
                    )
            elif step.type == 132 and step.HasField("tool"):
                items.append(
                    Item(
                        item_id=opaque_id("item", chat.chat_id, native),
                        kind=Kind.tool_result,
                        role="tool",
                        text=step.tool.result.text,
                    )
                )
            else:
                limitations.append(f"Unsupported Antigravity step type {step.type}")
    finally:
        connection.close()
    return finish(chat, items, limitations)


def _transcript(source: Source, path: pathlib.Path) -> Conversation:
    rows, limitations = read_jsonl(path)
    chat = make_chat(source, path.parents[2].name)
    items: list[Item] = []
    known: dict[str, tuple[Kind, Role]] = {
        "USER_INPUT": (Kind.message, "user"),
        "PLANNER_RESPONSE": (Kind.message, "assistant"),
        "CONVERSATION_HISTORY": (Kind.summary, "system"),
        "TOOL_CALL": (Kind.tool_call, "assistant"),
        "TOOL_RESULT": (Kind.tool_result, "tool"),
        "THINKING": (Kind.thinking, "assistant"),
    }
    for index, row in enumerate(rows):
        typ = row.get("type")
        if not isinstance(typ, str) or typ not in known:
            limitations.append(
                f"Unsupported Antigravity transcript step type: {str(typ)[:80]}"
            )
            continue
        kind, role = known[typ]
        items.append(
            Item(
                item_id=opaque_id(
                    "item", chat.chat_id, str(row.get("step_index", index))
                ),
                kind=kind,
                role=role,
                text=text_content(row.get("content", "")),
                timestamp=timestamp(row.get("created_at")),
            )
        )
        if row.get("truncated_fields"):
            limitations.append(
                "Generated Antigravity transcript contains truncated fields"
            )
    times = [item.timestamp for item in items if item.timestamp]
    if times:
        chat.created_at, chat.updated_at = times[0], times[-1]
    return finish(chat, items, limitations)

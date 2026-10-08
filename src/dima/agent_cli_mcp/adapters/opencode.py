"""OpenCode legacy and v2 SQLite stores, read in one consistent transaction."""

import collections
import pathlib

from dima.agent_cli_mcp.models import Conversation, Item, Kind, Source

from .common import (
    JsonObject,
    blocks,
    finish,
    load_json,
    make_chat,
    mapping,
    optional_string,
    query,
    read_database,
    string,
)


def read_opencode(source: Source, path: pathlib.Path) -> list[Conversation]:
    connection = read_database(path)
    try:
        tables = {
            row["name"]
            for row in query(
                connection, "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        if not {"session", "session_v2"} & tables:
            raise ValueError("Unsupported OpenCode database schema")
        sessions: dict[str, tuple[JsonObject, bool]] = {}
        for table in ["session", "session_v2"]:
            if table in tables:
                for row in query(connection, f"SELECT * FROM {table}"):
                    sessions[string(row["id"])] = (row, table == "session_v2")
        legacy_messages: collections.defaultdict[object, list[JsonObject]] = (
            collections.defaultdict(list)
        )
        parts: collections.defaultdict[object, list[JsonObject]] = (
            collections.defaultdict(list)
        )
        modern_messages: collections.defaultdict[object, list[JsonObject]] = (
            collections.defaultdict(list)
        )
        if "message" in tables:
            for row in query(
                connection, "SELECT * FROM message ORDER BY time_created,id"
            ):
                legacy_messages[row["session_id"]].append(row)
        if "part" in tables:
            for row in query(connection, "SELECT * FROM part ORDER BY time_created,id"):
                parts[row["message_id"]].append(row)
        if "session_message" in tables:
            for row in query(
                connection, "SELECT * FROM session_message ORDER BY seq,id"
            ):
                modern_messages[row["session_id"]].append(row)
        conversations: list[Conversation] = []
        for native, (row, modern) in sessions.items():
            chat = make_chat(
                source,
                native,
                directory=optional_string(row.get("directory")),
                title=optional_string(row.get("title")),
                created=row.get("time_created"),
                updated=row.get("time_updated"),
                parent=optional_string(row.get("parent_id")),
                fork=optional_string(row.get("fork_session_id")),
                archived=bool(row.get("time_archived")),
            )
            items: list[Item] = []
            limitations: list[str] = []
            for message in (
                modern_messages[native] if modern else legacy_messages[native]
            ):
                data = mapping(load_json(message["data"]))
                typ = message.get("type", data.get("role", "system"))
                time = message.get("time_created")
                content_groups: list[tuple[object, object]]
                if modern:
                    if typ in {"agent-switched", "model-switched", "idle"}:
                        continue
                    if typ not in {
                        "user",
                        "assistant",
                        "system",
                        "synthetic",
                        "compaction",
                    }:
                        limitations.append(
                            f"Unsupported OpenCode v2 message type: {str(typ)[:80]}"
                        )
                        continue
                    content = data.get("content", data.get("text", ""))
                    content_groups = [(message["id"], content)]
                else:
                    content_groups = [
                        (part["id"], [load_json(part["data"])])
                        for part in parts[message["id"]]
                    ]
                role = (
                    typ
                    if isinstance(typ, str) and typ in {"user", "assistant"}
                    else "system"
                )
                added: list[Item] = []
                warnings: list[str] = []
                for native_item, content in content_groups:
                    normalized, block_warnings = blocks(
                        chat.chat_id, str(native_item), content, role, time
                    )
                    added.extend(normalized)
                    warnings.extend(block_warnings)
                if typ == "compaction" or data.get("summary") is True:
                    for item in added:
                        if item.kind == Kind.message:
                            item.kind = Kind.summary
                elif role == "system":
                    for item in added:
                        if item.kind == Kind.message:
                            item.kind = Kind.artifact
                items.extend(added)
                limitations.extend(warnings)
            conversations.append(finish(chat, items, limitations))
        return conversations
    finally:
        connection.close()

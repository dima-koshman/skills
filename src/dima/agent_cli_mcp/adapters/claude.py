"""Claude Code JSONL, including parent chains and separate subagent logs."""

import pathlib

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
    blocks,
    finish,
    make_chat,
    mapping,
    optional_string,
    read_jsonl,
    string,
)


def read_claude(source: Source, path: pathlib.Path) -> Conversation:
    rows, limitations = read_jsonl(path)
    subagent = path.parent.name == "subagents"
    native = (
        path.stem
        if subagent
        else next(
            (string(row["sessionId"]) for row in rows if row.get("sessionId")),
            path.stem,
        )
    )
    title = next(
        (
            optional_string(row.get("customTitle", row.get("aiTitle")))
            for row in reversed(rows)
            if row.get("customTitle") or row.get("aiTitle")
        ),
        None,
    )
    directory = next((string(row["cwd"]) for row in rows if row.get("cwd")), None)
    times = [row["timestamp"] for row in rows if row.get("timestamp")]
    chat = make_chat(
        source,
        native,
        title=title,
        directory=directory,
        created=times[0] if times else None,
        updated=times[-1] if times else None,
        parent=path.parents[1].name if subagent else None,
        archived=False,
    )
    selected = _chain(rows, limitations)
    latest = {row["uuid"]: i for i, row in enumerate(rows) if row.get("uuid")}
    items: list[Item] = []
    for index, row in enumerate(rows):
        typ = row.get("type")
        if row.get("uuid") and latest[row["uuid"]] != index:
            continue
        if selected is not None and row.get("uuid") and index not in selected:
            continue
        if typ in {"user", "assistant"}:
            message = mapping(row.get("message", {}))
            added, warnings = blocks(
                chat.chat_id,
                str(row.get("uuid", index)),
                message.get("content", []),
                str(message.get("role", typ)),
                row.get("timestamp"),
            )
            if row.get("isMeta"):
                for item in added:
                    if item.kind == Kind.message:
                        item.kind, item.role = Kind.artifact, "system"
            items.extend(added)
            limitations.extend(warnings)
        elif typ == "summary" and row.get("summary"):
            items.append(
                Item(
                    item_id=opaque_id("item", chat.chat_id, "summary", str(index)),
                    kind=Kind.summary,
                    role="system",
                    text=string(row["summary"]),
                    timestamp=timestamp(row.get("timestamp")),
                )
            )
    return finish(chat, items, limitations)


def _chain(rows: list[JsonObject], limitations: list[str]) -> set[int] | None:
    linked = [
        i
        for i, row in enumerate(rows)
        if row.get("uuid")
        and "parentUuid" in row
        and row.get("type") in {"user", "assistant"}
    ]
    if not linked:
        return None
    lookup = {row["uuid"]: i for i, row in enumerate(rows) if row.get("uuid")}
    current = rows[linked[-1]]["uuid"]
    selected: set[int] = set()
    seen: set[object] = set()
    while current:
        if current in seen:
            raise ValueError("Cyclic Claude parent chain")
        seen.add(current)
        if current not in lookup:
            limitations.append("Claude parent record is missing from the stored chain")
            break
        index = lookup[current]
        selected.add(index)
        current = rows[index].get("parentUuid")
    return selected

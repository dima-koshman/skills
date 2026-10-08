"""Refresh and MCP boundary tests against synthetic local source stores."""

import asyncio
import json
import pathlib
import shutil
import sqlite3
import sys
from collections.abc import Callable, Iterator

import fastmcp
import fastmcp.client.transports
import pytest

from dima.agent_cli_mcp import models
from dima.agent_cli_mcp.cursors import Cursors
from dima.agent_cli_mcp.server import create_server
from dima.agent_cli_mcp.service import Service
from dima.agent_cli_mcp.store import Store

_OpencodeDatabase = Callable[[pathlib.Path], sqlite3.Connection]


def _transcript(
    root: pathlib.Path, text: str = "needle in original chat", native: str = "native"
) -> pathlib.Path:
    path = root / f"sessions/{native}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        {
            "type": "session_meta",
            "payload": {
                "id": native,
                "cwd": "/repo",
                "timestamp": "2026-10-08T10:00:00Z",
            },
        },
        {
            "type": "response_item",
            "payload": {
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": text}],
            },
        },
    ]
    _ = path.write_text("".join(json.dumps(row) + "\n" for row in rows))
    return path


@pytest.fixture
def service(tmp_path: pathlib.Path) -> Iterator[tuple[Service, pathlib.Path]]:
    root = tmp_path / "codex"
    _ = _transcript(root)
    instance = Service(
        index_path=tmp_path / "index.db",
        sources=[models.Source(harness=models.Harness.codex, path=root)],
        refresh_seconds=0,
    )
    yield instance, root
    instance.close()


def test_first_query_indexes_existing_conversations(
    service: tuple[Service, pathlib.Path],
):
    instance, _ = service
    result = instance.search_chats(models.SearchRequest(query="needle"))
    assert result.hits[0].snippet == "needle in original chat"
    assert result.coverage[0].status == "ready"
    assert result.coverage[0].indexed_chats == 1


def test_changed_file_replaces_old_search_results(
    service: tuple[Service, pathlib.Path],
):
    instance, root = service
    _ = instance.list_chats(models.ListRequest())
    _ = _transcript(root, text="replacement content")
    assert instance.search_chats(models.SearchRequest(query="needle")).hits == []
    assert instance.search_chats(models.SearchRequest(query="replacement")).hits


def test_missing_source_preserves_cache_and_reports_incomplete_coverage(
    service: tuple[Service, pathlib.Path],
):
    instance, root = service
    _ = instance.list_chats(models.ListRequest())
    shutil.rmtree(root)
    result = instance.search_chats(models.SearchRequest(query="needle"))
    assert result.hits
    assert result.coverage[0].status == "missing"


def test_deleted_file_is_removed_after_successful_scan(
    service: tuple[Service, pathlib.Path],
):
    instance, root = service
    _ = instance.list_chats(models.ListRequest())
    (root / "sessions/native.jsonl").unlink()
    assert instance.list_chats(models.ListRequest()).chats == []


def test_malformed_source_preserves_previously_indexed_chat(
    service: tuple[Service, pathlib.Path],
):
    instance, root = service
    _ = instance.list_chats(models.ListRequest())
    _ = (root / "sessions/native.jsonl").write_text('{"broken":}\n')
    result = instance.search_chats(models.SearchRequest(query="needle"))
    assert result.hits
    assert result.coverage[0].status == "partial"


def test_unchanged_source_does_not_expire_cursor(service: tuple[Service, pathlib.Path]):
    instance, root = service
    _ = _transcript(root, native="second")
    first = instance.list_chats(models.ListRequest(limit=1))
    second = instance.list_chats(models.ListRequest(cursor=first.next_cursor))
    assert second.chats[0].chat_id != first.chats[0].chat_id


def test_query_keeps_one_snapshot_when_another_process_updates_index(
    service: tuple[Service, pathlib.Path], monkeypatch: pytest.MonkeyPatch
):
    instance, root = service
    _ = _transcript(root, native="second")
    first = instance.list_chats(models.ListRequest(limit=1))
    monkeypatch.setattr(instance, "_refresh_seconds", 3600)
    decode = Cursors.decode

    with Store(root.parent / "index.db") as other:

        def delete_after_cursor_validation(
            cursors: Cursors,
            token: str,
            method: str,
            revision: int,
            request: models.ListRequest,
        ) -> tuple[models.ListRequest, dict[str, int]]:
            result = decode(cursors, token, method, revision, request)
            # A second real SQLite connection commits between revision validation
            # and result retrieval; the request must keep its original snapshot.
            for key in other.files(instance.sources[0].source_id):
                other.remove_file(instance.sources[0].source_id, key)
            return result

        monkeypatch.setattr(Cursors, "decode", delete_after_cursor_validation)
        second = instance.list_chats(models.ListRequest(cursor=first.next_cursor))
        assert len(second.chats) == 1
        assert second.chats[0].chat_id != first.chats[0].chat_id
        assert instance.list_chats(models.ListRequest()).chats == []


def test_codex_session_index_supplies_native_titles(
    service: tuple[Service, pathlib.Path],
):
    instance, root = service
    _ = (root / "session_index.jsonl").write_text(
        json.dumps(
            {
                "id": "native",
                "thread_name": "Actual title",
                "updated_at": "2026-10-08T11:00:00Z",
            }
        )
        + "\n"
    )
    result = instance.list_chats(models.ListRequest())
    assert result.chats[0].title == "Actual title"
    _ = (root / "session_index.jsonl").write_text(
        json.dumps({"id": "native", "thread_name": "Renamed title"}) + "\n"
    )
    assert instance.list_chats(models.ListRequest()).chats[0].title == "Renamed title"


def test_failing_source_does_not_hide_other_sources(tmp_path: pathlib.Path):
    _ = _transcript(tmp_path / "codex")
    root = tmp_path / "antigravity"
    (root / "conversations").mkdir(parents=True)
    _ = (root / "conversations/legacy.pb").write_bytes(b"unsupported")
    with Service(
        index_path=tmp_path / "index.db",
        sources=[
            models.Source(harness=models.Harness.codex, path=tmp_path / "codex"),
            models.Source(harness=models.Harness.antigravity, path=root),
        ],
    ) as instance:
        result = instance.search_chats(models.SearchRequest(query="needle"))
        assert result.hits
        assert {entry.status for entry in result.coverage} == {"ready", "partial"}


def test_real_fastmcp_client_searches_then_reads_original_messages(
    service: tuple[Service, pathlib.Path],
):
    instance, _ = service

    async def run():
        async with fastmcp.Client(create_server(instance)) as client:
            tools = await client.list_tools()
            assert {tool.name for tool in tools} == {
                "list_chats",
                "search_chats",
                "read_chat",
            }
            result = await client.call_tool("search_chats", {"query": "needle"})
            hit = models.SearchResult.model_validate(result.structured_content).hits[0]
            read = models.ReadResult.model_validate(
                (
                    await client.call_tool(
                        "read_chat",
                        {"chat_id": hit.chat_id, "anchor_item_id": hit.item_id},
                    )
                ).structured_content
            )
            assert read.items[0].text == "needle in original chat"
            assert read.coverage[0].status == "ready"

    asyncio.run(run())


def test_fastmcp_cursor_only_arguments_continue_previous_request(
    service: tuple[Service, pathlib.Path],
):
    instance, root = service
    _ = _transcript(root, native="second")

    async def run():
        async with fastmcp.Client(create_server(instance)) as client:
            first = models.ListResult.model_validate(
                (await client.call_tool("list_chats", {"limit": 1})).structured_content
            )
            second = models.ListResult.model_validate(
                (
                    await client.call_tool("list_chats", {"cursor": first.next_cursor})
                ).structured_content
            )
            assert first.chats[0].chat_id != second.chats[0].chat_id

    asyncio.run(run())


def test_fastmcp_rejects_unknown_arguments(service: tuple[Service, pathlib.Path]):
    instance, _ = service

    async def run():
        async with fastmcp.Client(create_server(instance)) as client:
            result = await client.call_tool(
                "list_chats", {"surprise": True}, raise_on_error=False
            )
            assert result.is_error

    asyncio.run(run())


def test_stdio_entry_point_can_search_isolated_home(tmp_path: pathlib.Path):
    _ = _transcript(tmp_path / ".codex")

    # A real external MCP process: no user credentials or native model requests.
    async def run():
        async with fastmcp.Client(
            fastmcp.client.transports.StdioTransport(
                command=sys.executable,
                args=[
                    "-m",
                    "dima.agent_cli_mcp",
                    "--home",
                    str(tmp_path),
                    "--index",
                    str(tmp_path / "index.db"),
                ],
            )
        ) as client:
            result = await client.call_tool("search_chats", {"query": "needle"})
            hits = models.SearchResult.model_validate(result.structured_content).hits
            assert hits[0].harness == models.Harness.codex

    asyncio.run(run())


def test_partial_source_coverage_survives_server_restart(tmp_path: pathlib.Path):
    root = tmp_path / "codex"
    path = _transcript(root)
    with path.open("a") as stream:
        _ = stream.write('{"type":')
    source = models.Source(harness=models.Harness.codex, path=root)
    for _ in range(2):
        with Service(index_path=tmp_path / "index.db", sources=[source]) as instance:
            result = instance.list_chats(models.ListRequest())
            assert result.coverage[0].status == "partial"


def test_removed_source_configuration_excludes_previously_cached_chats(
    tmp_path: pathlib.Path,
):
    root = tmp_path / "codex"
    _ = _transcript(root)
    with Service(
        index_path=tmp_path / "index.db",
        sources=[models.Source(harness=models.Harness.codex, path=root)],
    ) as instance:
        chat = instance.list_chats(models.ListRequest()).chats[0]
    with Service(index_path=tmp_path / "index.db", sources=[]) as instance:
        assert instance.list_chats(models.ListRequest()).chats == []
        assert instance.search_chats(models.SearchRequest(query="needle")).hits == []
        with pytest.raises(models.ChatError, match="CHAT_NOT_FOUND"):
            _ = instance.read_chat(models.ReadRequest(chat_id=chat.chat_id))


def test_index_cannot_overwrite_harness_data(tmp_path: pathlib.Path):
    root = tmp_path / "opencode"
    root.mkdir()
    with pytest.raises(ValueError, match="outside"):
        _ = Service(
            index_path=root / "opencode.db",
            sources=[models.Source(harness=models.Harness.opencode, path=root)],
        )


def test_changed_opencode_wal_refreshes_cached_search(
    tmp_path: pathlib.Path, opencode_database: _OpencodeDatabase
):
    # Reuse the on-disk fixture constructor, not a mocked adapter.
    root = tmp_path / "opencode"
    root.mkdir()
    connection = opencode_database(root / "opencode.db")
    with Service(
        index_path=tmp_path / "index.db",
        sources=[models.Source(harness=models.Harness.opencode, path=root)],
        refresh_seconds=0,
    ) as instance:
        assert instance.search_chats(models.SearchRequest(query="first")).hits
        _ = connection.execute(
            "UPDATE part SET data=?",
            (json.dumps({"type": "text", "text": "WAL replacement"}),),
        )
        connection.commit()
        assert instance.search_chats(models.SearchRequest(query="first")).hits == []
        assert instance.search_chats(models.SearchRequest(query="replacement")).hits
    connection.close()


def test_overlapping_opencode_databases_keep_modern_session_on_legacy_update(
    tmp_path: pathlib.Path, opencode_database: _OpencodeDatabase
):
    root = tmp_path / "opencode"
    root.mkdir()
    legacy = opencode_database(root / "opencode.db")
    modern = opencode_database(root / "opencode-next.db")
    _ = modern.execute("UPDATE session SET title='Modern session'")
    modern.commit()
    with Service(
        index_path=tmp_path / "index.db",
        sources=[models.Source(harness=models.Harness.opencode, path=root)],
        refresh_seconds=0,
    ) as instance:
        assert (
            instance.list_chats(models.ListRequest()).chats[0].title == "Modern session"
        )
        _ = legacy.execute("UPDATE session SET title='Old store changed'")
        legacy.commit()
        assert (
            instance.list_chats(models.ListRequest()).chats[0].title == "Modern session"
        )
    legacy.close()
    modern.close()


def test_malformed_payload_does_not_abort_other_harnesses(tmp_path: pathlib.Path):
    _ = _transcript(tmp_path / "good")
    path = _transcript(tmp_path / "bad")
    _ = path.write_text(json.dumps({"type": "session_meta", "payload": []}) + "\n")
    with Service(
        index_path=tmp_path / "index.db",
        sources=[
            models.Source(harness=models.Harness.codex, path=tmp_path / "bad"),
            models.Source(harness=models.Harness.codex, path=tmp_path / "good"),
        ],
    ) as instance:
        result = instance.search_chats(models.SearchRequest(query="needle"))
        assert len(result.hits) == 1
        assert {source.status for source in result.coverage} == {"partial", "ready"}


def test_unreadable_child_directory_retains_cache_on_python314_semantics(
    service: tuple[Service, pathlib.Path], monkeypatch: pytest.MonkeyPatch
):
    instance, root = service
    _ = instance.list_chats(models.ListRequest())
    original_exists = pathlib.Path.exists

    def exists_suppressing_os_errors(path: pathlib.Path) -> bool:
        # Python 3.14 Path.exists suppresses OSError. Exercise real permissions
        # while reproducing that newer stdlib behavior on the project's 3.11.
        try:
            return original_exists(path)
        except OSError:
            return False

    monkeypatch.setattr(pathlib.Path, "exists", exists_suppressing_os_errors)
    root.chmod(0o400)
    try:
        result = instance.search_chats(models.SearchRequest(query="needle"))
        assert result.hits
        assert result.coverage[0].status == "error"
    finally:
        root.chmod(0o700)

"""Synthetic source fixtures exercise the actual on-disk harness formats."""

import json
import pathlib
import sqlite3
from collections.abc import Callable

import pytest

from dima.agent_cli_mcp.adapters import read_file
from dima.agent_cli_mcp.models import Conversation, Harness, Source


def test_claude_reads_latest_parent_chain_not_abandoned_branch(tmp_path: pathlib.Path):
    path = _jsonl(
        tmp_path / "projects" / "-repo" / "session.jsonl",
        [
            {
                "type": "user",
                "uuid": "u",
                "parentUuid": None,
                "sessionId": "session",
                "cwd": "/repo",
                "message": {"role": "user", "content": "question"},
            },
            {
                "type": "assistant",
                "uuid": "old",
                "parentUuid": "u",
                "message": {
                    "role": "assistant",
                    "content": [{"type": "text", "text": "abandoned answer"}],
                },
            },
            {
                "type": "assistant",
                "uuid": "new",
                "parentUuid": "u",
                "message": {
                    "role": "assistant",
                    "content": [{"type": "text", "text": "current answer"}],
                },
            },
            {
                "type": "custom-title",
                "customTitle": "Named session",
                "sessionId": "session",
            },
        ],
    )
    result = _read(Harness.claude_code, path, tmp_path)[0]
    assert [item.text for item in result.items] == ["question", "current answer"]
    assert result.chat.title == "Named session"
    assert result.chat.directory == "/repo"


def test_claude_preserves_tool_links_and_saved_thinking(tmp_path: pathlib.Path):
    path = _jsonl(
        tmp_path / "projects/p/session.jsonl",
        [
            {
                "type": "assistant",
                "uuid": "a",
                "message": {
                    "role": "assistant",
                    "content": [
                        {"type": "thinking", "thinking": "saved rationale"},
                        {
                            "type": "tool_use",
                            "id": "call",
                            "name": "Read",
                            "input": {"file_path": "/repo/a.py"},
                        },
                    ],
                },
            },
            {
                "type": "user",
                "uuid": "b",
                "message": {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": "call",
                            "content": "file body",
                        }
                    ],
                },
            },
        ],
    )
    result = _read(Harness.claude_code, path, tmp_path)[0]
    assert [item.kind for item in result.items] == [
        "thinking",
        "tool_call",
        "tool_result",
    ]
    assert result.items[1].tool_name == "Read"
    assert result.items[2].tool_call_id == "call"


def test_claude_subagent_has_its_own_identity_and_parent(tmp_path: pathlib.Path):
    path = _jsonl(
        tmp_path / "projects/p/session/subagents/agent-xyz.jsonl",
        [
            {
                "type": "user",
                "uuid": "a",
                "sessionId": "session",
                "message": {"role": "user", "content": "subtask"},
            },
        ],
    )
    result = _read(Harness.claude_code, path, tmp_path)[0]
    assert result.chat.native_session_id == "agent-xyz"
    assert result.chat.parent_chat_id is not None
    assert result.chat.chat_id != result.chat.parent_chat_id


def test_codex_avoids_duplicate_event_messages(tmp_path: pathlib.Path):
    path = _jsonl(
        tmp_path / "sessions/2026/10/08/rollout-test.jsonl",
        [
            {
                "type": "session_meta",
                "payload": {
                    "id": "native",
                    "cwd": "/repo",
                    "timestamp": "2026-10-08T10:00:00Z",
                },
            },
            {
                "type": "event_msg",
                "payload": {"type": "user_message", "message": "hello"},
            },
            {
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "hello"}],
                },
            },
            {
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "assistant",
                    "content": [{"type": "output_text", "text": "answer"}],
                },
            },
            {
                "type": "event_msg",
                "payload": {"type": "agent_message", "message": "answer"},
            },
        ],
    )
    result = _read(Harness.codex, path, tmp_path)[0]
    assert [item.text for item in result.items] == ["hello", "answer"]
    assert result.chat.native_session_id == "native"


def test_codex_retains_tool_results_and_compaction_summary(tmp_path: pathlib.Path):
    path = _jsonl(
        tmp_path / "archived_sessions/rollout-test.jsonl",
        [
            {
                "type": "session_meta",
                "payload": {"id": "native", "forked_from_id": "parent"},
            },
            {
                "type": "response_item",
                "payload": {
                    "type": "function_call",
                    "call_id": "call",
                    "name": "shell",
                    "arguments": '{"cmd":"pwd"}',
                },
            },
            {
                "type": "response_item",
                "payload": {
                    "type": "function_call_output",
                    "call_id": "call",
                    "output": "/repo",
                },
            },
            {"type": "compacted", "payload": {"message": "Previous context"}},
        ],
    )
    result = _read(Harness.codex, path, tmp_path)[0]
    assert result.chat.archived is True
    assert result.chat.forked_from_chat_id is not None
    assert [item.kind for item in result.items] == [
        "tool_call",
        "tool_result",
        "summary",
    ]


def test_partial_last_jsonl_record_reports_limitation(tmp_path: pathlib.Path):
    path = _jsonl(
        tmp_path / "sessions/a.jsonl",
        [
            {"type": "session_meta", "payload": {"id": "native"}},
            {
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "complete"}],
                },
            },
        ],
    )
    with path.open("a") as stream:
        _ = stream.write('{"type":')
    result = _read(Harness.codex, path, tmp_path)[0]
    assert [item.text for item in result.items] == ["complete"]
    assert result.limitations


def test_malformed_middle_record_is_an_error(tmp_path: pathlib.Path):
    path = tmp_path / "bad.jsonl"
    _ = path.write_text('{"type":}\n{}\n')
    with pytest.raises(ValueError, match="record"):
        _ = _read(Harness.codex, path, tmp_path)


def test_unknown_substantive_block_is_reported(tmp_path: pathlib.Path):
    path = _jsonl(
        tmp_path / "projects/p/a.jsonl",
        [
            {
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "content": [{"type": "future-content", "data": "not guessed"}],
                },
            },
        ],
    )
    assert _read(Harness.claude_code, path, tmp_path)[0].limitations


def test_opencode_reads_legacy_sqlite_messages(
    tmp_path: pathlib.Path,
    opencode_database: Callable[[pathlib.Path], sqlite3.Connection],
):
    path = tmp_path / "opencode.db"
    connection = opencode_database(path)
    result = _read(Harness.opencode, path, tmp_path)[0]
    assert result.chat.title == "Native title"
    assert result.items[0].text == "first"
    connection.close()


def test_opencode_reads_uncheckpointed_wal_content(
    tmp_path: pathlib.Path,
    opencode_database: Callable[[pathlib.Path], sqlite3.Connection],
):
    path = tmp_path / "opencode.db"
    connection = opencode_database(path)
    _ = connection.execute(
        "UPDATE part SET data=?",
        (json.dumps({"type": "text", "text": "new WAL content"}),),
    )
    connection.commit()
    assert _read(Harness.opencode, path, tmp_path)[0].items[0].text == "new WAL content"
    connection.close()


def test_opencode_prefers_v2_for_overlapping_sessions(
    tmp_path: pathlib.Path,
    opencode_database: Callable[[pathlib.Path], sqlite3.Connection],
):
    path = tmp_path / "opencode.db"
    connection = opencode_database(path)
    _ = connection.executescript("""
        CREATE TABLE session_v2 AS SELECT * FROM session;
        CREATE TABLE session_message(id TEXT,session_id TEXT,type TEXT,seq INTEGER,time_created INTEGER,time_updated INTEGER,data TEXT);
    """)
    _ = connection.execute(
        "INSERT INTO session_message VALUES(?,?,?,?,?,?,?)",
        ("v2", "s", "user", 0, 1, 1, json.dumps({"text": "modern content"})),
    )
    connection.commit()
    result = _read(Harness.opencode, path, tmp_path)
    assert len(result) == 1
    assert [item.text for item in result[0].items] == ["modern content"]
    connection.close()


def test_opencode_v2_reads_assistant_blocks(
    tmp_path: pathlib.Path,
    opencode_database: Callable[[pathlib.Path], sqlite3.Connection],
):
    path = tmp_path / "opencode.db"
    connection = opencode_database(path)
    _ = connection.executescript("""
        CREATE TABLE session_v2 AS SELECT * FROM session;
        CREATE TABLE session_message(id TEXT,session_id TEXT,type TEXT,seq INTEGER,time_created INTEGER,time_updated INTEGER,data TEXT);
    """)
    data = {
        "content": [
            {"type": "text", "text": "assistant answer"},
            {"type": "reasoning", "text": "saved thought"},
        ]
    }
    _ = connection.execute(
        "INSERT INTO session_message VALUES(?,?,?,?,?,?,?)",
        ("v2", "s", "assistant", 0, 1, 1, json.dumps(data)),
    )
    connection.commit()
    assert [item.kind for item in _read(Harness.opencode, path, tmp_path)[0].items] == [
        "message",
        "thinking",
    ]
    connection.close()


def test_antigravity_generated_transcript_is_readable(tmp_path: pathlib.Path):
    path = _jsonl(
        tmp_path / "brain/native/.system_generated/logs/transcript.jsonl",
        [
            {
                "step_index": 0,
                "type": "USER_INPUT",
                "status": "DONE",
                "created_at": "2026-10-08T10:00:00Z",
                "content": "question",
            },
            {
                "step_index": 1,
                "type": "PLANNER_RESPONSE",
                "status": "DONE",
                "content": "answer",
            },
        ],
    )
    result = _read(Harness.antigravity, path, tmp_path)[0]
    assert result.chat.native_session_id == "native"
    assert [item.text for item in result.items] == ["question", "answer"]


def test_antigravity_sqlite_known_protobuf_steps_are_decoded(tmp_path: pathlib.Path):
    # Independent literal protobuf fixtures: Step type/status and nested payloads.
    path = tmp_path / "conversations/native.db"
    path.parent.mkdir()
    connection = sqlite3.connect(path)
    _ = connection.executescript(
        "CREATE TABLE steps(idx INTEGER,step_type INTEGER,status INTEGER,step_payload BLOB,step_format INTEGER);"
    )
    _ = connection.execute(
        "INSERT INTO steps VALUES(0,14,3,?,0)",
        (bytes.fromhex("080e20039a010a12087175657374696f6e"),),
    )
    _ = connection.execute(
        "INSERT INTO steps VALUES(1,15,3,?,0)",
        (bytes.fromhex("080f2003a201080a06616e73776572"),),
    )
    connection.commit()
    result = _read(Harness.antigravity, path, tmp_path)[0]
    assert [item.text for item in result.items] == ["question", "answer"]
    connection.close()


def test_legacy_antigravity_pb_has_explicit_unsupported_error(tmp_path: pathlib.Path):
    path = tmp_path / "conversation.pb"
    _ = path.write_bytes(b"opaque binary")
    with pytest.raises(ValueError, match="unsupported"):
        _ = _read(Harness.antigravity, path, tmp_path)


def test_source_installations_do_not_collide(tmp_path: pathlib.Path):
    results: list[Conversation] = []
    for root in [tmp_path / "one", tmp_path / "two"]:
        path = _jsonl(
            root / "projects/p/same.jsonl",
            [
                {
                    "type": "user",
                    "sessionId": "same",
                    "message": {"role": "user", "content": "text"},
                }
            ],
        )
        results.append(_read(Harness.claude_code, path, root)[0])
    assert results[0].chat.chat_id != results[1].chat.chat_id


@pytest.mark.parametrize(
    "harness,record",
    [
        (Harness.codex, {"type": "session_meta", "payload": []}),
        (Harness.claude_code, {"type": "user", "message": []}),
    ],
)
def test_wrong_shaped_message_is_a_source_error(
    tmp_path: pathlib.Path, harness: Harness, record: dict[str, object]
):
    path = _jsonl(tmp_path / "bad.jsonl", [record])
    with pytest.raises(ValueError, match="shape"):
        _ = _read(harness, path, tmp_path)


def test_opencode_native_part_identity_survives_removal_of_earlier_part(
    tmp_path: pathlib.Path,
    opencode_database: Callable[[pathlib.Path], sqlite3.Connection],
):
    path = tmp_path / "opencode.db"
    connection = opencode_database(path)
    _ = connection.execute(
        "INSERT INTO part VALUES(?,?,?,?,?,?)",
        ("p2", "m", "s", json.dumps({"type": "text", "text": "second"}), 2, 2),
    )
    connection.commit()
    before = _read(Harness.opencode, path, tmp_path)[0].items
    _ = connection.execute("DELETE FROM part WHERE id='p'")
    connection.commit()
    after = _read(Harness.opencode, path, tmp_path)[0].items
    assert after[0].item_id == before[1].item_id
    assert after[0].text == "second"
    connection.close()


def test_codex_nested_subagent_source_preserves_parent(tmp_path: pathlib.Path):
    path = _jsonl(
        tmp_path / "sessions/child.jsonl",
        [
            {
                "type": "session_meta",
                "payload": {
                    "id": "child",
                    "source": {
                        "subagent": {"thread_spawn": {"parent_thread_id": "parent"}}
                    },
                },
            },
        ],
    )
    assert _read(Harness.codex, path, tmp_path)[0].chat.parent_chat_id is not None


def test_codex_web_search_activity_is_available_as_tool_call(tmp_path: pathlib.Path):
    path = _jsonl(
        tmp_path / "sessions/web.jsonl",
        [
            {"type": "session_meta", "payload": {"id": "native"}},
            {
                "type": "response_item",
                "payload": {
                    "type": "web_search_call",
                    "id": "call",
                    "action": {"type": "search", "query": "sqlite FTS5"},
                },
            },
        ],
    )
    result = _read(Harness.codex, path, tmp_path)[0]
    assert result.items[0].kind == "tool_call"
    assert result.items[0].tool_name == "web_search"
    assert "sqlite FTS5" in result.items[0].text


def test_claude_duplicate_native_uuid_is_read_once(tmp_path: pathlib.Path):
    path = _jsonl(
        tmp_path / "projects/p/native.jsonl",
        [
            {
                "type": "assistant",
                "uuid": "same",
                "message": {"role": "assistant", "content": "old partial"},
            },
            {
                "type": "assistant",
                "uuid": "same",
                "message": {"role": "assistant", "content": "complete answer"},
            },
        ],
    )
    assert [
        item.text for item in _read(Harness.claude_code, path, tmp_path)[0].items
    ] == ["complete answer"]


def _jsonl(path: pathlib.Path, rows: list[dict[str, object]]) -> pathlib.Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text("".join(json.dumps(row) + "\n" for row in rows))
    return path


def _read(
    harness: Harness, path: pathlib.Path, root: pathlib.Path
) -> list[Conversation]:
    return read_file(Source(harness=harness, path=root), path)

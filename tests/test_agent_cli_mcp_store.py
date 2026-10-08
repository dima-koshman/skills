"""Behavior tests for the rebuildable conversation index."""

import pathlib
import sqlite3
from collections.abc import Iterator

import pytest

from dima.agent_cli_mcp import models
from dima.agent_cli_mcp.store import Store


@pytest.fixture
def index(tmp_path: pathlib.Path) -> Iterator[Store]:
    index = Store(tmp_path / "index.db")
    for native, directory, updated, parent, archived in [
        ("a", "/repo", "2026-10-07T10:00:00Z", None, False),
        ("b", "/repo/child", "2026-10-08T10:00:00Z", None, True),
        ("c", "/repository", "2026-10-06T10:00:00Z", "a", False),
    ]:
        chat = models.Chat(
            chat_id=native,
            harness=models.Harness.codex,
            native_session_id=native,
            title=f"Chat {native}",
            title_source="native",
            directory=directory,
            created_at=updated,
            updated_at=updated,
            parent_chat_id=parent,
            archived=archived,
        )
        texts = ["The REFRESH token expired.", "Refresh alone.", "token alone."]
        items = [
            models.Item(
                item_id=f"{native}-{i}",
                kind=models.Kind.message,
                role="assistant",
                text=text,
            )
            for i, text in enumerate(texts)
        ]
        items.append(
            models.Item(
                item_id=f"{native}-tool",
                kind=models.Kind.tool_result,
                role="tool",
                text="secret tool output",
            )
        )
        index.put(chat, items, source_id="source", file_key=native, fingerprint="1")
    yield index
    index.close()


def test_phrase_search_returns_exact_passage_case_insensitively(index: Store):
    db = index
    result = db.search_chats(models.SearchRequest(query='"refresh token"'))
    assert {hit.item_id for hit in result.hits} == {"a-0", "b-0"}
    assert all(hit.snippet == "The REFRESH token expired." for hit in result.hits)


def test_all_terms_must_match_the_same_item(index: Store):
    db = index
    assert {
        hit.item_id
        for hit in db.search_chats(models.SearchRequest(query="refresh token")).hits
    } == {"a-0", "b-0"}


def test_any_terms_match_separate_items(index: Store):
    db = index
    assert (
        len(
            db.search_chats(
                models.SearchRequest(query="refresh token", match="any")
            ).hits
        )
        == 6
    )


def test_subagents_and_archives_have_independent_filters(index: Store):
    db = index
    result = db.list_chats(
        models.ListRequest(include_subagents=True, include_archived=False)
    )
    assert [chat.chat_id for chat in result.chats] == ["a", "c"]


def test_descendant_filter_observes_directory_boundaries(index: Store):
    db = index
    result = db.list_chats(
        models.ListRequest(
            directory="/repo", directory_scope="descendants", include_subagents=True
        )
    )
    assert [chat.chat_id for chat in result.chats] == ["b", "a"]


def test_directory_wildcards_are_literal(index: Store):
    db = index
    assert (
        db.list_chats(
            models.ListRequest(directory="/rep%", directory_scope="descendants")
        ).chats
        == []
    )


def test_tool_results_require_explicit_content_type(index: Store):
    db = index
    assert db.search_chats(models.SearchRequest(query="secret")).hits == []
    assert (
        len(
            db.search_chats(
                models.SearchRequest(
                    query="secret", content_types=[models.Kind.tool_result]
                )
            ).hits
        )
        == 2
    )


def test_cursor_alone_continues_list_without_duplicates(index: Store):
    db = index
    first = db.list_chats(models.ListRequest(limit=1))
    second = db.list_chats(models.ListRequest(cursor=first.next_cursor))
    assert [chat.chat_id for chat in first.chats + second.chats] == ["b", "a"]
    assert second.next_cursor is None


def test_search_cursor_alone_keeps_original_query(index: Store):
    db = index
    first = db.search_chats(models.SearchRequest(query="expired", limit=1))
    second = db.search_chats(models.SearchRequest(cursor=first.next_cursor))
    assert len({first.hits[0].item_id, second.hits[0].item_id}) == 2


def test_modified_index_expires_existing_cursor(index: Store):
    db = index
    first = db.list_chats(models.ListRequest(limit=1))
    db.remove_file("source", "a")
    with pytest.raises(models.ChatError, match="CURSOR_EXPIRED"):
        _ = db.list_chats(models.ListRequest(cursor=first.next_cursor))


def test_cursor_tampering_is_rejected(index: Store):
    db = index
    token = db.list_chats(models.ListRequest(limit=1)).next_cursor
    assert token is not None
    with pytest.raises(models.ChatError, match="INVALID_CURSOR"):
        _ = db.list_chats(models.ListRequest(cursor=token + "x"))


def test_cursor_cannot_be_reused_with_a_different_query(index: Store):
    db = index
    token = db.search_chats(models.SearchRequest(query="refresh", limit=1)).next_cursor
    with pytest.raises(models.ChatError, match="INVALID_CURSOR"):
        _ = db.search_chats(models.SearchRequest(query="token", cursor=token))


def test_replacement_removes_old_fts_hits(index: Store):
    db = index
    chat = db.list_chats(models.ListRequest(title_contains="Chat a")).chats[0]
    db.put(
        chat,
        [
            models.Item(
                item_id="a-new",
                kind=models.Kind.message,
                role="user",
                text="replacement",
            )
        ],
        source_id="source",
        file_key="a",
        fingerprint="2",
    )
    assert (
        db.search_chats(models.SearchRequest(query="expired", chat_ids=["a"])).hits
        == []
    )
    assert (
        db.search_chats(models.SearchRequest(query="replacement")).hits[0].item_id
        == "a-new"
    )


def test_read_returns_anchor_with_surrounding_messages(index: Store):
    db = index
    result = db.read_chat(
        models.ReadRequest(chat_id="a", anchor_item_id="a-1", before=1, after=1)
    )
    assert [item.item_id for item in result.items] == ["a-0", "a-1", "a-2"]


def test_large_item_can_be_read_completely_through_continuations(index: Store):
    db = index
    chat = db.list_chats(models.ListRequest(title_contains="Chat a")).chats[0]
    text = "abc🚀" * 100
    db.put(
        chat,
        [models.Item(item_id="long", kind=models.Kind.message, role="user", text=text)],
        source_id="source",
        file_key="a",
        fingerprint="2",
    )
    result = db.read_chat(models.ReadRequest(chat_id="a", max_chars=31))
    pieces = [result.items[0].text]
    while result.newer_cursor:
        result = db.read_chat(models.ReadRequest(cursor=result.newer_cursor))
        pieces.extend(item.text for item in result.items)
    assert "".join(pieces) == text
    assert all(len(piece) <= 31 for piece in pieces)


def test_default_read_starts_with_latest_twenty_items(index: Store):
    db = index
    chat = db.list_chats(models.ListRequest(title_contains="Chat a")).chats[0]
    db.put(
        chat,
        [
            models.Item(
                item_id=f"row-{i}", kind=models.Kind.message, role="user", text=str(i)
            )
            for i in range(25)
        ],
        source_id="source",
        file_key="a",
        fingerprint="2",
    )
    result = db.read_chat(models.ReadRequest(chat_id="a"))
    assert [item.text for item in result.items] == [str(i) for i in range(5, 25)]
    older = db.read_chat(models.ReadRequest(cursor=result.older_cursor))
    assert [item.text for item in older.items] == ["0", "1", "2", "3", "4"]


def test_missing_anchor_is_an_actionable_error(index: Store):
    db = index
    with pytest.raises(models.ChatError, match="ITEM_NOT_FOUND"):
        _ = db.read_chat(models.ReadRequest(chat_id="a", anchor_item_id="b-0"))


@pytest.mark.parametrize("query", ["", "   ", '"unfinished'])
def test_invalid_query_returns_actionable_error(index: Store, query: str):
    db = index
    with pytest.raises(models.ChatError, match="INVALID_QUERY"):
        _ = db.search_chats(models.SearchRequest(query=query))


def test_query_operators_are_literal_words(index: Store):
    db = index
    assert db.search_chats(models.SearchRequest(query="refresh OR token")).hits == []


def test_punctuation_in_query_does_not_escape_fts_expression(index: Store):
    db = index
    assert db.search_chats(models.SearchRequest(query="refresh-token")).hits


@pytest.mark.usefixtures("index")
def test_index_survives_restart(tmp_path: pathlib.Path):
    with Store(tmp_path / "index.db") as reopened:
        assert reopened.search_chats(models.SearchRequest(query="expired")).hits


def test_failed_file_replacement_rolls_back_all_conversations(index: Store):
    db = index
    chat = db.list_chats(models.ListRequest(title_contains="Chat a")).chats[0]
    duplicate = models.Item(
        item_id="duplicate", kind=models.Kind.message, role="user", text="new text"
    )
    with pytest.raises(sqlite3.IntegrityError):
        _ = db.replace_file(
            "source",
            "a",
            "2",
            [models.Conversation(chat=chat, items=[duplicate, duplicate])],
            [],
        )
    assert db.search_chats(models.SearchRequest(query="expired", chat_ids=["a"])).hits


def test_unchanged_conversation_does_not_invalidate_cursor(index: Store):
    db = index
    cursor = db.list_chats(models.ListRequest(limit=1)).next_cursor
    chat = db.list_chats(models.ListRequest(title_contains="Chat a")).chats[0]
    items = db.read_chat(
        models.ReadRequest(
            chat_id="a", content_types=[models.Kind.message, models.Kind.tool_result]
        )
    ).items
    items = [item.model_copy(update={"total_chars": None}) for item in items]
    db.replace_file(
        "source",
        "a",
        "different file stats",
        [models.Conversation(chat=chat, items=items)],
        [],
    )
    assert db.list_chats(models.ListRequest(cursor=cursor)).chats

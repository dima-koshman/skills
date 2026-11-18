"""Tests for okf_review_server: promoting drafts and leaving review comments from the reader."""

from __future__ import annotations

import http.client
import json
import pathlib
import sys
import textwrap
import threading

import pytest
import yaml

sys.path.insert(
    0, str(pathlib.Path(__file__).parent.parent / ".agents/skills/okf/scripts")
)

import okf_review_server

AT = "2026-11-18T10:00:00+04:00"

DRAFT = textwrap.dedent(
    """\
    ---
    type: Concept
    title: Shaping
    description: Narrowing a raw idea into a bounded, rough solution, written
      across two lines.
    status: draft
    generated:
      by: claude-code/claude-opus-5-5
      at: '2026-11-17T17:45:00+04:00'
    ---

    Body text.[^a]

    [^a]: A source.
    """
)


def _frontmatter(path: pathlib.Path) -> dict:
    return yaml.safe_load(path.read_text().split("---\n")[1])


@pytest.fixture
def bundle(tmp_path: pathlib.Path) -> pathlib.Path:
    root = tmp_path / "wiki"
    (root / "planning").mkdir(parents=True)
    (root / "planning/shaping.md").write_text(DRAFT)
    (root / "stable.md").write_text("---\ntype: Concept\ntitle: Stable\n---\n\nDone.\n")
    return root


def test_promote_removes_draft_status_and_records_the_reviewer(bundle):
    okf_review_server.promote(bundle, "planning/shaping.md", "human:dima", AT)

    frontmatter = _frontmatter(bundle / "planning/shaping.md")
    assert "status" not in frontmatter
    assert frontmatter["verified"] == [{"by": "human:dima", "at": AT}]


def test_promote_keeps_the_rest_of_the_file_byte_for_byte(bundle):
    okf_review_server.promote(bundle, "planning/shaping.md", "human:dima", AT)

    text = (bundle / "planning/shaping.md").read_text()
    without_new_lines = DRAFT.replace("status: draft\n", "")
    assert text.startswith(without_new_lines.split("---\n\n")[0])
    assert text.endswith("---\n\nBody text.[^a]\n\n[^a]: A source.\n")


def test_promote_appends_to_an_existing_verified_list(bundle):
    path = bundle / "planning/shaping.md"
    path.write_text(
        DRAFT.replace(
            "status: draft\n",
            "status: draft\nverified:\n- by: process:nightly\n  at: '2026-11-01T00:00:00Z'\n",
        )
    )

    okf_review_server.promote(bundle, "planning/shaping.md", "human:dima", AT)

    assert [event["by"] for event in _frontmatter(path)["verified"]] == [
        "process:nightly",
        "human:dima",
    ]


def test_promote_refuses_a_concept_that_is_not_a_draft(bundle):
    with pytest.raises(okf_review_server.ReviewError, match="not a draft"):
        okf_review_server.promote(bundle, "stable.md", "human:dima", AT)


def test_comment_appends_a_review_comment_and_keeps_the_draft(bundle):
    okf_review_server.add_comment(
        bundle, "planning/shaping.md", "human:dima", AT, "Cite the book for step 2."
    )
    okf_review_server.add_comment(
        bundle, "planning/shaping.md", "human:dima", AT, "Shorten the intro."
    )

    frontmatter = _frontmatter(bundle / "planning/shaping.md")
    assert frontmatter["status"] == "draft"
    assert [c["text"] for c in frontmatter["review_comments"]] == [
        "Cite the book for step 2.",
        "Shorten the intro.",
    ]
    assert frontmatter["review_comments"][0]["by"] == "human:dima"


def test_comment_refuses_empty_text(bundle):
    with pytest.raises(okf_review_server.ReviewError, match="empty"):
        okf_review_server.add_comment(bundle, "stable.md", "human:dima", AT, "  ")


@pytest.mark.parametrize(
    "concept_id", ["../outside.md", "index.md", "missing.md", "x.txt"]
)
def test_edits_refuse_anything_but_an_existing_concept_in_the_bundle(
    bundle, concept_id
):
    (bundle.parent / "outside.md").write_text(DRAFT)
    (bundle / "index.md").write_text("# Index\n")

    with pytest.raises(okf_review_server.ReviewError):
        okf_review_server.add_comment(bundle, concept_id, "human:dima", AT, "Hi.")


@pytest.fixture
def server(bundle):
    output = bundle.parent / "dev" / "site.html"
    review = okf_review_server.ReviewServer(
        bundle, output, reviewer="human:dima", host="127.0.0.1", port=0
    )
    thread = threading.Thread(target=review.httpd.serve_forever, daemon=True)
    thread.start()
    yield review
    review.httpd.shutdown()
    review.httpd.server_close()


def _request(review, method, path, body=None, headers=None):
    connection = http.client.HTTPConnection("127.0.0.1", review.port, timeout=10)
    payload = json.dumps(body) if body is not None else None
    all_headers = {"Host": f"127.0.0.1:{review.port}"}
    if payload is not None:
        all_headers["Content-Type"] = "application/json"
    all_headers.update(headers or {})
    connection.request(method, path, body=payload, headers=all_headers)
    response = connection.getresponse()
    return response.status, response.read()


def test_server_renders_the_site_on_start_and_answers_ping(server):
    status, body = _request(server, "GET", "/api/ping")

    assert status == 200
    assert json.loads(body)["reviewer"] == "human:dima"
    assert server.output_path.exists()
    assert (server.bundle_root / "index.md").exists()


def test_server_comment_edits_the_concept_and_rerenders(server):
    before = json.loads(_request(server, "GET", "/api/version")[1])["version"]

    status, _ = _request(
        server,
        "POST",
        "/api/comment",
        {"id": "planning/shaping.md", "text": "Add an example."},
    )

    assert status == 200
    assert "Add an example." in (server.bundle_root / "planning/shaping.md").read_text()
    assert "Add an example." in server.output_path.read_text()
    after = json.loads(_request(server, "GET", "/api/version")[1])["version"]
    assert after != before


def test_server_promote_reports_a_refused_edit_as_bad_request(server):
    status, body = _request(server, "POST", "/api/promote", {"id": "stable.md"})

    assert status == 400
    assert "not a draft" in json.loads(body)["error"]


def test_server_rejects_posts_from_another_origin(server):
    status, _ = _request(
        server,
        "POST",
        "/api/comment",
        {"id": "planning/shaping.md", "text": "Spam."},
        headers={"Origin": "https://evil.example"},
    )

    assert status == 403
    assert "Spam." not in (server.bundle_root / "planning/shaping.md").read_text()


def test_server_rejects_posts_that_are_not_json(server):
    status, _ = _request(
        server,
        "POST",
        "/api/comment",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert status == 415


def test_server_serves_the_page_and_bundle_files_but_nothing_else(server):
    (server.bundle_root.parent / "secret.txt").write_text("no")
    (server.bundle_root / "diagram.html").write_text("<p>ok</p>")

    root_status, _ = _request(server, "GET", "/")
    asset_status, asset = _request(server, "GET", "/wiki/diagram.html")
    secret_status, _ = _request(server, "GET", "/secret.txt")
    escape_status, _ = _request(server, "GET", "/wiki/../secret.txt")

    assert root_status == 302
    assert (asset_status, asset) == (200, b"<p>ok</p>")
    assert secret_status == 404
    assert escape_status == 404


def test_refresh_rerenders_only_after_a_concept_changes(server):
    assert server.refresh_if_changed() is False

    (server.bundle_root / "stable.md").write_text(
        "---\ntype: Concept\ntitle: Stable again\n---\n\nDone.\n"
    )

    assert server.refresh_if_changed() is True
    assert "Stable again" in server.output_path.read_text()
    assert server.refresh_if_changed() is False

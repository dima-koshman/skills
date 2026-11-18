"""Tests for okf_review: the inventory behind a bundle review pass."""

from __future__ import annotations

import datetime
import pathlib
import sys
import textwrap

sys.path.insert(
    0, str(pathlib.Path(__file__).parent.parent / ".agents/skills/okf/scripts")
)

import okf_review

NOW = datetime.datetime(2026, 11, 11, tzinfo=datetime.UTC)


def _write(root: pathlib.Path, relative: str, frontmatter: str, body: str = "") -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n"
        + textwrap.dedent(frontmatter).strip()
        + "\n---\n\n"
        + textwrap.dedent(body),
        encoding="utf-8",
    )


def test_lists_draft_concepts(tmp_path):
    _write(tmp_path, "a.md", "type: Concept\nstatus: draft")
    _write(tmp_path, "b.md", "type: Concept")

    report = okf_review.review(tmp_path, now=NOW)

    assert report.drafts == ["/a.md"]


def test_lists_concepts_past_stale_after(tmp_path):
    _write(tmp_path, "old.md", "type: Concept\nstale_after: '2026-11-01T00:00:00Z'")
    _write(tmp_path, "fresh.md", "type: Concept\nstale_after: '2027-01-01T00:00:00Z'")

    report = okf_review.review(tmp_path, now=NOW)

    assert report.stale == ["/old.md"]


def test_lists_concepts_without_verified_event(tmp_path):
    _write(
        tmp_path,
        "checked.md",
        "type: Concept\nverified:\n- by: human:ana\n  at: '2026-11-01T00:00:00Z'",
    )
    _write(tmp_path, "unchecked.md", "type: Concept")

    report = okf_review.review(tmp_path, now=NOW)

    assert report.unverified == ["/unchecked.md"]


def test_reports_body_link_to_missing_concept(tmp_path):
    _write(
        tmp_path, "a.md", "type: Concept", "See [b](/b.md) and [gone](/gone.md#part).\n"
    )
    _write(tmp_path, "b.md", "type: Concept")

    report = okf_review.review(tmp_path, now=NOW)

    assert report.broken_links == [("/a.md", "/gone.md")]


def test_reports_frontmatter_path_to_missing_concept(tmp_path):
    _write(tmp_path, "a.md", "type: Concept\nparent: /missing.md\nrelated:\n- /b.md")
    _write(tmp_path, "b.md", "type: Concept")

    report = okf_review.review(tmp_path, now=NOW)

    assert report.broken_links == [("/a.md", "/missing.md")]


def test_reports_source_id_that_nothing_cites(tmp_path):
    _write(
        tmp_path,
        "a.md",
        """
        type: Concept
        sources:
        - id: used
          resource: https://example.com/used
        - id: unused
          resource: https://example.com/unused
        """,
        "A claim.[^used]\n",
    )

    report = okf_review.review(tmp_path, now=NOW)

    assert report.uncited_sources == [("/a.md", "unused")]


def test_reports_footnote_without_matching_source(tmp_path):
    _write(
        tmp_path,
        "a.md",
        "type: Concept\nsources:\n- id: known\n  resource: https://example.com",
        "One.[^known] Two.[^unknown]\n",
    )

    report = okf_review.review(tmp_path, now=NOW)

    assert report.undefined_footnotes == [("/a.md", "unknown")]


def test_ignores_type_schema_documents(tmp_path):
    _write(tmp_path, "_types/Concept.md", "type: Type\nstatus: draft")

    report = okf_review.review(tmp_path, now=NOW)

    assert report.drafts == []
    assert report.unverified == []


def test_ignores_index_and_log_files(tmp_path):
    _write(tmp_path, "index.md", "okf_version: '0.2'", "[x](/nowhere.md)\n")
    (tmp_path / "log.md").write_text("# Log\n\n[y](/nowhere.md)\n", encoding="utf-8")

    report = okf_review.review(tmp_path, now=NOW)

    assert report.broken_links == []
    assert report.unverified == []


def test_lists_review_comments_left_on_concepts(tmp_path):
    _write(
        tmp_path,
        "a.md",
        "type: Concept\nreview_comments:\n- by: human:ana\n  at: '2026-11-10T00:00:00Z'\n  text: Add a source.",
    )
    _write(tmp_path, "b.md", "type: Concept")

    report = okf_review.review(tmp_path, now=NOW)

    assert report.review_comments == [("/a.md", "human:ana: Add a source.")]


def test_percent_encoded_links_to_existing_concepts_are_not_broken(tmp_path):
    _write(tmp_path, "Services/PII Masking (v2).md", "type: Concept")
    _write(
        tmp_path,
        "a.md",
        "type: Concept",
        "See [masking](/Services/PII%20Masking%20%28v2%29.md).\n",
    )

    report = okf_review.review(tmp_path, now=NOW)

    assert report.broken_links == []


def test_links_to_the_bundle_index_are_not_broken(tmp_path):
    (tmp_path / "index.md").write_text("# Index\n")
    _write(tmp_path, "a.md", "type: Concept", "Back to the [catalog](/index.md).\n")

    report = okf_review.review(tmp_path, now=NOW)

    assert report.broken_links == []

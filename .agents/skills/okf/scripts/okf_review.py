"""List what an OKF bundle's review pass should look at.

Usage:
    python okf_review.py [bundle-dir] [--list-unverified]

Reports, per concept:

* drafts: ``status: draft``, waiting for promotion or removal;
* stale: ``stale_after`` has passed;
* unverified: no ``verified`` event (count only, unless ``--list-unverified``);
* broken links: a bundle-relative ``/path.md`` in the body or the frontmatter
  that names no file in the bundle;
* uncited sources: a ``sources`` id that no ``[^id]`` footnote cites;
* undefined footnotes: a ``[^id]`` with neither a matching source nor a local
  ``[^id]:`` definition;
* review comments: ``review_comments`` a reviewer left (for example from
  ``okf_review_server.py``), waiting for an agent to address them.

It only lists. Judging duplicates, re-checking claims and deciding what to
promote or prune is the review pass's job (see SKILL.md).
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime
import pathlib
import re
import sys
import urllib.parse

from okf_index import _parse_frontmatter

_RESERVED_FILENAMES = frozenset({"index.md", "log.md"})
_FENCED_CODE = re.compile(r"^```.*?^```", re.MULTILINE | re.DOTALL)
_BODY_LINK = re.compile(r"\]\((/[^)\s#]+\.md)(?:#[^)]*)?\)")
_FOOTNOTE_DEFINITION = re.compile(r"^\[\^([^\]]+)\]:", re.MULTILINE)
_FOOTNOTE_REFERENCE = re.compile(r"\[\^([^\]]+)\](?!:)")


@dataclasses.dataclass
class Report:
    """What a review pass should look at. Concepts are bundle-relative paths."""

    drafts: list[str] = dataclasses.field(default_factory=list)
    stale: list[str] = dataclasses.field(default_factory=list)
    unverified: list[str] = dataclasses.field(default_factory=list)
    broken_links: list[tuple[str, str]] = dataclasses.field(default_factory=list)
    uncited_sources: list[tuple[str, str]] = dataclasses.field(default_factory=list)
    undefined_footnotes: list[tuple[str, str]] = dataclasses.field(default_factory=list)
    review_comments: list[tuple[str, str]] = dataclasses.field(default_factory=list)


def review(bundle_root: pathlib.Path, now: datetime.datetime) -> Report:
    """Inventory every concept document under ``bundle_root``."""
    bundle_root = bundle_root.resolve()
    all_documents = [
        path
        for path in sorted(bundle_root.rglob("*.md"))
        if path.name not in _RESERVED_FILENAMES
    ]
    # Reserved files (index.md, log.md) are valid link targets, even though they are not concepts.
    existing = {
        "/" + path.relative_to(bundle_root).as_posix()
        for path in bundle_root.rglob("*.md")
    }
    # `_types/` holds type schemas, not concepts; okf_site.py skips them too.
    documents = [
        path
        for path in all_documents
        if "_types" not in path.relative_to(bundle_root).parts[:-1]
    ]
    report = Report()

    for path in documents:
        frontmatter, error = _parse_frontmatter(path)
        if error is not None:
            continue
        concept = "/" + path.relative_to(bundle_root).as_posix()
        body = _FENCED_CODE.sub("", _body_of(path))

        if str(frontmatter.get("status") or "").strip() == "draft":
            report.drafts.append(concept)
        stale_after = _as_datetime(frontmatter.get("stale_after"))
        if stale_after is not None and stale_after < now:
            report.stale.append(concept)
        if not frontmatter.get("verified"):
            report.unverified.append(concept)
        for comment in frontmatter.get("review_comments") or []:
            if isinstance(comment, dict) and comment.get("text"):
                author = comment.get("by") or "unknown"
                report.review_comments.append((concept, f"{author}: {comment['text']}"))

        # Markdown link URLs percent-encode spaces and parentheses; frontmatter paths stay readable.
        targets = {urllib.parse.unquote(t) for t in _BODY_LINK.findall(body)} | set(
            _frontmatter_paths(frontmatter)
        )
        report.broken_links.extend(
            (concept, target) for target in sorted(targets - existing)
        )

        source_ids = {
            str(source["id"])
            for source in frontmatter.get("sources") or []
            if isinstance(source, dict) and source.get("id")
        }
        cited = set(_FOOTNOTE_REFERENCE.findall(body))
        defined_locally = set(_FOOTNOTE_DEFINITION.findall(body))
        report.uncited_sources.extend(
            (concept, sid) for sid in sorted(source_ids - cited)
        )
        report.undefined_footnotes.extend(
            (concept, label) for label in sorted(cited - source_ids - defined_locally)
        )

    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="List what an OKF review pass should look at."
    )
    parser.add_argument(
        "bundle", nargs="?", default=".", help="OKF bundle root (default: .)"
    )
    parser.add_argument(
        "--list-unverified",
        action="store_true",
        help="List every unverified concept instead of only counting them.",
    )
    args = parser.parse_args()

    bundle_root = pathlib.Path(args.bundle)
    if not bundle_root.is_dir():
        print(f"error: bundle path is not a directory: {bundle_root}", file=sys.stderr)
        return 2

    report = review(bundle_root, now=datetime.datetime.now(datetime.UTC))
    _print_section("Drafts", report.drafts)
    _print_section(
        "Review comments", [f"{c}: {text}" for c, text in report.review_comments]
    )
    _print_section("Past stale_after", report.stale)
    if args.list_unverified:
        _print_section("Unverified", report.unverified)
    else:
        print(
            f"## Unverified ({len(report.unverified)}) - pass --list-unverified to list\n"
        )
    _print_section("Broken links", [f"{c} -> {t}" for c, t in report.broken_links])
    _print_section("Concepts with uncited sources", _grouped(report.uncited_sources))
    _print_section(
        "Undefined footnotes", [f"{c}: [^{f}]" for c, f in report.undefined_footnotes]
    )
    return 0


def _body_of(path: pathlib.Path) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[index + 1 :])
    return ""


def _frontmatter_paths(value: object):
    """Yield every bundle-relative ``/....md`` string anywhere in the frontmatter."""
    if isinstance(value, str):
        if value.startswith("/") and value.endswith(".md"):
            yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _frontmatter_paths(item)
    elif isinstance(value, list):
        for item in value:
            yield from _frontmatter_paths(item)


def _as_datetime(value: object) -> datetime.datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime.datetime):
        moment = value
    elif isinstance(value, datetime.date):
        moment = datetime.datetime.combine(value, datetime.time())
    else:
        try:
            moment = datetime.datetime.fromisoformat(str(value))
        except ValueError:
            return None
    return moment if moment.tzinfo else moment.replace(tzinfo=datetime.UTC)


def _grouped(pairs: list[tuple[str, str]]) -> list[str]:
    by_concept: dict[str, list[str]] = {}
    for concept, item in pairs:
        by_concept.setdefault(concept, []).append(item)
    return [f"{concept}: {', '.join(items)}" for concept, items in by_concept.items()]


def _print_section(title: str, items: list[str]) -> None:
    print(f"## {title} ({len(items)})")
    for item in items:
        print(f"- {item}")
    print()


if __name__ == "__main__":
    sys.exit(main())

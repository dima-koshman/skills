"""Generate OKF ``index.md`` files from concept-document frontmatter.

Usage:
    python okf_index.py [bundle-dir] [--per-directory]

Reads every non-reserved ``.md`` file in the bundle, parses its YAML
frontmatter, and fully regenerates ``index.md`` as a progressive-disclosure
listing (OKF spec section 6). ``index.md`` is treated as a build artifact:
any existing file is overwritten, so the concept documents' frontmatter is
the single source of truth. Human-written prose belongs in the concept
files, not in ``index.md``.

By default a single catalog is written to ``<bundle>/index.md`` mirroring the
bundle's directory hierarchy: each directory becomes a heading whose level
reflects its depth (top-level dirs are ``#``, their subdirectories ``##``, and
so on), with that directory's concepts listed beneath it. Each concept's
``type`` is shown as an inline ``` `[Type]` ``` tag before its description,
since Markdown cannot color-code entries the way the HTML site does. With
``--per-directory`` an ``index.md`` is written into each directory that
contains concepts, listing that directory's own documents and its
subdirectories.

The bundle-root ``index.md`` is the only index that carries frontmatter; it
declares ``okf_version`` (spec section 11).
"""

from __future__ import annotations

import argparse
import dataclasses
import pathlib
import sys

import yaml

# Pinned to the OKF spec revision this script targets; see references/spec.md.
OKF_VERSION = "0.1"

_RESERVED_FILENAMES = frozenset({"index.md", "log.md"})


@dataclasses.dataclass(frozen=True)
class Concept:
    """A parsed OKF concept document.

    Attributes:
        path: Absolute path to the document on disk.
        directory: Absolute path to the document's parent directory.
        bundle_path: Bundle-relative POSIX path, e.g. ``/tables/orders.md``.
        type: The required ``type`` frontmatter field.
        title: Display name (frontmatter ``title`` or a filename fallback).
        description: One-line summary (frontmatter ``description`` or empty).
    """

    path: pathlib.Path
    directory: pathlib.Path
    bundle_path: str
    type: str
    title: str
    description: str


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate OKF index.md files from concept-document frontmatter.",
    )
    parser.add_argument(
        "bundle",
        nargs="?",
        default=".",
        help="Path to the OKF bundle root (default: current directory).",
    )
    parser.add_argument(
        "--per-directory",
        action="store_true",
        help="Regenerate an index.md in every directory that contains concepts, "
        "instead of a single catalog at the bundle root.",
    )
    args = parser.parse_args()

    bundle_root = pathlib.Path(args.bundle).resolve()
    if not bundle_root.is_dir():
        print(f"error: bundle path is not a directory: {bundle_root}", file=sys.stderr)
        return 2

    concepts, warnings = _collect_concepts(bundle_root)
    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)

    if not concepts:
        print("warning: no OKF concept documents found; nothing to index.", file=sys.stderr)
        return 0

    if args.per_directory:
        written = _write_per_directory_indexes(bundle_root, concepts)
    else:
        written = _write_root_catalog(bundle_root, concepts)

    for index_path in written:
        print(f"wrote {index_path.relative_to(bundle_root)}")

    return 0


def _collect_concepts(bundle_root: pathlib.Path) -> tuple[list[Concept], list[str]]:
    """Walk the bundle and parse every non-reserved ``.md`` file.

    Returns the parsed concepts and a list of human-readable warnings for
    files that could not be parsed or lacked a ``type`` field. Consistent
    with the spec's permissive model, unparseable files are skipped with a
    warning rather than aborting the run.
    """
    concepts: list[Concept] = []
    warnings: list[str] = []

    for path in sorted(bundle_root.rglob("*.md")):
        if path.name in _RESERVED_FILENAMES:
            continue

        frontmatter, error = _parse_frontmatter(path)
        relative = path.relative_to(bundle_root).as_posix()
        if error is not None:
            warnings.append(f"{relative}: {error}")
            continue

        concept_type = frontmatter.get("type")
        if not concept_type or not str(concept_type).strip():
            warnings.append(f"{relative}: missing required 'type' field; skipped.")
            continue

        title = frontmatter.get("title") or _title_from_filename(path)
        concepts.append(
            Concept(
                path=path,
                directory=path.parent,
                bundle_path="/" + relative,
                type=str(concept_type).strip(),
                title=str(title).strip(),
                description=str(frontmatter.get("description") or "").strip(),
            )
        )

    return concepts, warnings


def _parse_frontmatter(path: pathlib.Path) -> tuple[dict, str | None]:
    """Parse a document's YAML frontmatter block.

    Returns ``(frontmatter, None)`` on success or ``({}, error_message)`` if
    the file has no ``---`` delimited block or the YAML does not parse to a
    mapping.
    """
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, "no YAML frontmatter block."

    lines = text.splitlines()
    closing_index = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            closing_index = index
            break

    if closing_index is None:
        return {}, "frontmatter block is not closed with '---'."

    block = "\n".join(lines[1:closing_index])
    try:
        parsed = yaml.safe_load(block)
    except yaml.YAMLError as error:
        return {}, f"unparseable frontmatter YAML ({error})."

    if not isinstance(parsed, dict):
        return {}, "frontmatter did not parse to a mapping."

    return parsed, None


def _write_root_catalog(bundle_root: pathlib.Path, concepts: list[Concept]) -> list[pathlib.Path]:
    """Write a single ``index.md`` at the bundle root mirroring the hierarchy."""
    body = _render_hierarchy(bundle_root, concepts)
    content = _with_root_frontmatter(body)
    index_path = bundle_root / "index.md"
    index_path.write_text(content, encoding="utf-8")

    return [index_path]


def _write_per_directory_indexes(
    bundle_root: pathlib.Path, concepts: list[Concept]
) -> list[pathlib.Path]:
    """Write an ``index.md`` into every directory that contains concepts.

    Each index lists the directory's own concept documents (as a flat,
    type-tagged list using relative links) followed by links to immediate
    subdirectories that themselves contain concepts.
    """
    by_directory: dict[pathlib.Path, list[Concept]] = {}
    for concept in concepts:
        by_directory.setdefault(concept.directory, []).append(concept)

    directories_with_concepts = _directories_covering(bundle_root, by_directory.keys())
    written: list[pathlib.Path] = []

    for directory in sorted(directories_with_concepts):
        own = by_directory.get(directory, [])
        body = _render_concept_list(
            own,
            link_for=lambda concept, base=directory: concept.path.relative_to(base).as_posix(),
        )

        subdir_lines = _render_subdirectory_links(directory, directories_with_concepts)
        if subdir_lines:
            body = f"{body}\n\n# Subdirectories\n\n{subdir_lines}\n" if body.strip() else f"# Subdirectories\n\n{subdir_lines}\n"

        content = _with_root_frontmatter(body) if directory == bundle_root else body
        index_path = directory / "index.md"
        index_path.write_text(content, encoding="utf-8")
        written.append(index_path)

    return written


_MAX_HEADING_LEVEL = 6


def _render_hierarchy(bundle_root: pathlib.Path, concepts: list[Concept]) -> str:
    """Render concepts as a heading tree mirroring the directory structure.

    Each directory becomes a heading whose level equals its depth below the
    bundle root (top-level directories are ``#``, capped at ``######``), with
    that directory's concepts listed beneath it. Concepts living at the bundle
    root are listed first, without a heading. Directories are emitted in
    pre-order so a directory's own concepts sit directly above its
    subdirectories.
    """
    by_directory: dict[pathlib.Path, list[Concept]] = {}
    for concept in concepts:
        by_directory.setdefault(concept.directory, []).append(concept)

    covered = _directories_covering(bundle_root, by_directory.keys())
    blocks: list[str] = []

    root_list = _render_concept_list(
        by_directory.get(bundle_root, []),
        link_for=lambda concept: concept.bundle_path,
    )
    if root_list:
        blocks.append(root_list)

    subdirectories = sorted(
        (directory for directory in covered if directory != bundle_root),
        key=lambda directory: directory.relative_to(bundle_root).parts,
    )
    for directory in subdirectories:
        parts = directory.relative_to(bundle_root).parts
        level = min(len(parts), _MAX_HEADING_LEVEL)
        heading = f"{'#' * level} {parts[-1]}"
        entries = _render_concept_list(
            by_directory.get(directory, []),
            link_for=lambda concept: concept.bundle_path,
        )
        block = f"{heading}\n\n{entries}" if entries else heading
        blocks.append(block)

    return "\n\n".join(blocks)


def _render_concept_list(concepts, link_for) -> str:
    """Render concepts as a flat bullet list, sorted by title, type-tagged."""
    entries = sorted(concepts, key=lambda concept: concept.title.lower())

    return "\n".join(_render_concept_line(concept, link_for(concept)) for concept in entries)


def _render_concept_line(concept: Concept, link: str) -> str:
    """Render one bullet: link, an inline ``` `[Type]` ``` tag, and description."""
    tag = f" `[{concept.type}]`"
    suffix = f" - {concept.description}" if concept.description else ""

    return f"* [{concept.title}]({link}){tag}{suffix}"


def _render_subdirectory_links(directory, directories_with_concepts) -> str:
    """Render links to immediate subdirectories that contain concepts."""
    children = sorted(
        child
        for child in directories_with_concepts
        if child.parent == directory and child != directory
    )
    lines = [f"* [{child.name}/]({child.name}/)" for child in children]

    return "\n".join(lines)


def _directories_covering(bundle_root, directories) -> set[pathlib.Path]:
    """Return every directory that holds concepts, plus their ancestors.

    Ancestors up to and including the bundle root are included so that
    parent indexes can link down to subdirectories whose concepts live
    several levels deep.
    """
    covered: set[pathlib.Path] = set()
    for directory in directories:
        current = directory
        covered.add(current)
        while current != bundle_root and bundle_root in current.parents:
            current = current.parent
            covered.add(current)

    covered.add(bundle_root)

    return covered


def _with_root_frontmatter(body: str) -> str:
    """Prepend the bundle-root frontmatter declaring ``okf_version``."""
    frontmatter = f'---\nokf_version: "{OKF_VERSION}"\n---\n\n'

    return f"{frontmatter}{body.rstrip()}\n"


def _title_from_filename(path: pathlib.Path) -> str:
    """Derive a display title from a filename when frontmatter omits one."""
    return path.stem.replace("-", " ").replace("_", " ").strip().title()


if __name__ == "__main__":
    raise SystemExit(main())

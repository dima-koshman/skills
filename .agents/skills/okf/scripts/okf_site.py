"""Render an OKF bundle as a single self-contained HTML page.

Usage:
    python okf_site.py [bundle-dir] [-o OUTPUT]

Walks an OKF bundle, parses each concept's frontmatter and body, and writes one
self-contained ``okf-site.html`` with:

* a left navigation sidebar mirroring the bundle's directory structure, with a
  link to the bundle's ``log.md`` pinned at the bottom and non-Markdown assets
  opening in new tabs,
* a main reading area that renders the selected concept's markdown (via
  marked.js) with its in-bundle cross-links wired to navigate the bundle,
* a right pane showing unique inbound concept links by default, with a toggle
  for the Cytoscape.js graph (nodes = concepts colored by ``type``; edges =
  cross-links), and
* Back and Forward controls following browser history through reader pages.

The reader shows lifecycle ``status`` (draft and deprecated concepts are also
styled in the graph and tree) and ``sources`` with ``[^id]`` footnotes linked to
them. OKF v0.2 trust, freshness and authorship metadata is parsed and preserved
in the embedded data, but omitted from the visible concept pages.

Producer-defined frontmatter keys are shown as a Properties table, with optional
local `_types/` descriptions as hover help and secondary fields in collapsed details.
The `_types/` meta concepts themselves are omitted from the HTML reader. Any value
that is a path to another concept in the bundle (``/people/ana.md``, or a
list of such paths) becomes a link there and a *labeled* graph edge named after
the key, so typed relationships declared in frontmatter (``owner``,
``depends_on``, ...) appear in the graph next to the untyped body links.

The graph and reading libraries load from a CDN, so viewing the page needs
internet access; the Python side depends only on the standard library and
PyYAML. The output is a build artifact — regenerate it, do not hand-edit.
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime
import html
import json
import os
import pathlib
import posixpath
import re
import sys
import urllib.parse

import yaml

_RESERVED_FILENAMES = frozenset({"index.md", "log.md"})
_LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
_FOOTNOTE_DEFINITION = re.compile(r"^\[\^([^\]]+)\]:.*$", re.M)
_FOOTNOTE_REFERENCE = re.compile(r"\[\^([^\]]+)\]")

# Frontmatter keys defined by the OKF spec; every other key is producer-defined
# and rendered as a property.
_SPEC_KEYS = frozenset(
    {
        "type",
        "title",
        "description",
        "resource",
        "tags",
        "timestamp",
        "generated",
        "verified",
        "status",
        "stale_after",
        "sources",
        "usage_window",
    }
)

# Mid-tone, print-friendly hues that read well on a light background, assigned to
# concept types in first-seen order.
_TYPE_PALETTE = [
    "#3b82f6",
    "#ea7317",
    "#16a34a",
    "#dc2626",
    "#7c3aed",
    "#0891b2",
    "#ca8a04",
    "#9333ea",
    "#db2777",
    "#64748b",
    "#0d9488",
    "#b45309",
    "#4f46e5",
    "#be123c",
    "#65a30d",
    "#a16207",
]


@dataclasses.dataclass
class Concept:
    """A parsed OKF concept document, keyed by its bundle-relative id."""

    id: str  # bundle-relative POSIX path, e.g. "platform/mcp.md"
    type: str
    title: str
    description: str
    tags: list[str]
    resource: str
    body: str  # markdown body with in-bundle links rewritten to "#node:<id>"
    status: str = "stable"
    generated: dict | None = None
    verified: list[dict] = dataclasses.field(default_factory=list)
    trust: str = "unverified"
    stale_after: str = ""
    stale: bool = False
    sources: list[dict] = dataclasses.field(default_factory=list)
    properties: list[list[str]] = dataclasses.field(default_factory=list)
    links: list[dict] = dataclasses.field(
        default_factory=list
    )  # typed frontmatter edges


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render an OKF bundle as a single self-contained HTML page.",
    )
    parser.add_argument(
        "bundle",
        nargs="?",
        default=".",
        help="Path to the OKF bundle root (default: current directory).",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output HTML path (default: <bundle>/okf-site.html).",
    )
    args = parser.parse_args()

    bundle_root = pathlib.Path(args.bundle).resolve()
    if not bundle_root.is_dir():
        print(f"error: bundle path is not a directory: {bundle_root}", file=sys.stderr)
        return 2

    output_path = (
        pathlib.Path(args.output) if args.output else bundle_root / "okf-site.html"
    )
    render(bundle_root, output_path)

    return 0


def render(
    bundle_root: pathlib.Path,
    output_path: pathlib.Path,
    now: datetime.datetime | None = None,
) -> int:
    """Render the bundle at ``bundle_root`` into ``output_path``; return the concept count.

    ``now`` decides staleness (``stale_after``); it defaults to the current UTC time.
    """
    now = now or datetime.datetime.now(datetime.UTC)
    concepts, warnings = _collect_concepts(bundle_root, now)
    assets = _collect_assets(bundle_root, output_path)
    asset_hrefs = {asset["id"]: asset["href"] for asset in assets}
    for concept in concepts:
        concept.description = _rewrite_asset_links(
            concept.description, concept.id, asset_hrefs
        )
        concept.body = _rewrite_asset_links(concept.body, concept.id, asset_hrefs)
        concept.properties = [
            [key, _rewrite_asset_links(value, concept.id, asset_hrefs)]
            for key, value in concept.properties
        ]
        concept.resource = (
            _asset_href(concept.resource, concept.id, asset_hrefs) or concept.resource
        )
        for source in concept.sources:
            source["href"] = _asset_href(
                source["resource"], concept.id, asset_hrefs
            ) or source.get("href", "")
    type_schemas = _collect_type_schemas(bundle_root)
    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)

    if not concepts:
        print(
            "warning: no OKF concept documents found; nothing to render.",
            file=sys.stderr,
        )
        return 0

    edges = _build_edges(concepts)
    known_ids = {concept.id for concept in concepts}
    log_markdown = _read_log(bundle_root, known_ids)
    index_markdown = _read_index(bundle_root, known_ids)
    if log_markdown is not None:
        log_markdown = _rewrite_asset_links(log_markdown, "log.md", asset_hrefs)
    if index_markdown is not None:
        index_markdown = _rewrite_asset_links(index_markdown, "index.md", asset_hrefs)
    output_path.write_text(
        _render_html(
            bundle_root.name,
            concepts,
            edges,
            log_markdown,
            index_markdown,
            type_schemas,
            assets,
        ),
        encoding="utf-8",
    )

    print(f"wrote {output_path} ({len(concepts)} concepts, {len(edges)} links)")

    return len(concepts)


def _collect_assets(
    bundle_root: pathlib.Path, output_path: pathlib.Path
) -> list[dict[str, str]]:
    """List local supporting files without treating them as OKF concepts."""
    assets: list[dict[str, str]] = []
    output = output_path.resolve()
    for path in sorted(bundle_root.rglob("*")):
        if (
            not path.is_file()
            or path.is_symlink()
            or path.suffix.lower() == ".md"
            or path.resolve() == output
        ):
            continue
        relative = path.relative_to(bundle_root)
        if any(part.startswith(".") or part == "_types" for part in relative.parts):
            continue
        if relative.as_posix() == "okf-site.html":
            continue  # a prior rendering of this bundle, not a source asset
        href = os.path.relpath(path, output.parent).replace(os.sep, "/")
        assets.append(
            {
                "id": relative.as_posix(),
                "title": path.name,
                "kind": path.suffix.lstrip(".").upper() or "FILE",
                "href": urllib.parse.quote(href, safe="/"),
            }
        )
    return assets


def _asset_href(target: str, source_id: str, asset_hrefs: dict[str, str]) -> str | None:
    """Resolve a local path against the source concept without escaping the bundle."""
    if not target or "://" in target or target.startswith(("#", "mailto:")):
        return None
    raw_target = target.strip("<>")
    parsed = urllib.parse.urlsplit(raw_target)
    path = urllib.parse.unquote(parsed.path)
    source_dir = posixpath.dirname(source_id)
    resolved = posixpath.normpath(
        path.lstrip("/") if path.startswith("/") else posixpath.join(source_dir, path)
    )
    href = asset_hrefs.get(resolved)
    return href + raw_target[len(parsed.path) :] if href else None


def _rewrite_asset_links(
    markdown: str, source_id: str, asset_hrefs: dict[str, str]
) -> str:
    """Make bundle-local attachment links work when the site is rendered elsewhere."""

    def replace(match: re.Match[str]) -> str:
        href = _asset_href(match.group(1).strip(), source_id, asset_hrefs)
        return (
            match.group(0).replace(f"({match.group(1)})", f"({href})")
            if href
            else match.group(0)
        )

    return _LINK_PATTERN.sub(replace, markdown)


def _collect_concepts(
    bundle_root: pathlib.Path, now: datetime.datetime
) -> tuple[list[Concept], list[str]]:
    """Parse visible concept files, omitting `_types` meta documents."""
    warnings: list[str] = []
    parsed: list[tuple[str, dict, str]] = []

    for path in sorted(bundle_root.rglob("*.md")):
        if (
            path.name in _RESERVED_FILENAMES
            or "_types" in path.relative_to(bundle_root).parts[:-1]
        ):
            continue

        concept_id = path.relative_to(bundle_root).as_posix()
        frontmatter, body, error = _split_document(path)
        if error is not None:
            warnings.append(f"{concept_id}: {error}")
            continue

        concept_type = frontmatter.get("type")
        if not concept_type or not str(concept_type).strip():
            warnings.append(f"{concept_id}: missing required 'type' field; skipped.")
            continue

        parsed.append((concept_id, frontmatter, body))

    titles = {
        concept_id: str(frontmatter.get("title") or _title_from_id(concept_id)).strip()
        for concept_id, frontmatter, _ in parsed
    }
    known_ids = set(titles)

    return [_make_concept(item, titles, known_ids, now) for item in parsed], warnings


def _collect_type_schemas(bundle_root: pathlib.Path) -> dict[str, dict]:
    """Read local ``_types`` concepts as reader help, without making them graph nodes."""
    schemas: dict[str, dict] = {}
    for path in sorted(bundle_root.rglob("*.md")):
        if "_types" not in path.relative_to(bundle_root).parts[:-1]:
            continue
        frontmatter, body, error = _split_document(path)
        if error is not None or frontmatter.get("type") != "Concept Type":
            continue
        title = str(frontmatter.get("title") or "").strip()
        if not title:
            continue
        fields: dict[str, str] = {}
        for line in body.splitlines():
            match = re.match(r"^\|\s*`([^`]+)`\s*\|\s*[^|]*\|\s*(.*?)\s*\|\s*$", line)
            if match:
                fields[match.group(1)] = match.group(2)
        schema: dict[str, object] = {
            "description": str(frontmatter.get("description") or "").strip(),
            "fields": fields,
        }
        primary_fields = frontmatter.get("primary_fields")
        if isinstance(primary_fields, list):
            schema["primaryFields"] = [str(field) for field in primary_fields]
        schemas[title] = schema
    return schemas


def _make_concept(
    item: tuple[str, dict, str],
    titles: dict[str, str],
    known_ids: set[str],
    now: datetime.datetime,
) -> Concept:
    """Build a Concept, resolving v0.2 trust/lifecycle/provenance and typed links."""
    concept_id, frontmatter, body = item
    source_dir = posixpath.dirname(concept_id)
    tags = frontmatter.get("tags") or []
    verified = _verified_events(frontmatter.get("verified"))
    stale_after = _iso(frontmatter.get("stale_after"))
    properties, links = _properties_and_links(
        frontmatter, concept_id, titles, known_ids
    )

    return Concept(
        id=concept_id,
        type=str(frontmatter["type"]).strip(),
        title=titles[concept_id],
        description=_rewrite_internal_links(
            str(frontmatter.get("description") or "").strip(), concept_id, known_ids
        ),
        tags=[str(tag) for tag in tags] if isinstance(tags, list) else [],
        resource=str(frontmatter.get("resource") or "").strip(),
        body=_rewrite_internal_links(_link_footnotes(body), concept_id, known_ids),
        status=str(frontmatter.get("status") or "stable").strip(),
        generated=_generated(frontmatter),
        verified=verified,
        trust=_trust_tier(verified),
        stale_after=stale_after,
        stale=bool(stale_after) and _parse_instant(stale_after) <= now,
        sources=_sources(frontmatter.get("sources"), source_dir, known_ids),
        properties=properties,
        links=links,
    )


def _iso(value: object) -> str:
    """Normalize a YAML timestamp (parsed as datetime/date, or a string) to ISO 8601."""
    if isinstance(value, datetime.datetime):
        text = value.isoformat()
        return text.replace("+00:00", "Z")
    if isinstance(value, datetime.date):
        return value.isoformat()
    return str(value).strip() if value else ""


def _parse_instant(text: str) -> datetime.datetime:
    """Parse an ISO 8601 instant; a value without an offset is taken as UTC."""
    instant = datetime.datetime.fromisoformat(text.replace("Z", "+00:00"))
    return instant if instant.tzinfo else instant.replace(tzinfo=datetime.UTC)


def _generated(frontmatter: dict) -> dict | None:
    """Return ``generated`` as ``{by, at}``, falling back to a legacy v0.1 ``timestamp``."""
    generated = frontmatter.get("generated")
    if isinstance(generated, dict):
        return {"by": str(generated.get("by") or ""), "at": _iso(generated.get("at"))}
    if frontmatter.get("timestamp"):
        return {"by": "", "at": _iso(frontmatter["timestamp"])}
    return None


def _verified_events(value: object) -> list[dict]:
    """Normalize ``verified``: a bare mapping is a one-element list (spec section 5.2)."""
    events = (
        [value] if isinstance(value, dict) else value if isinstance(value, list) else []
    )
    return [
        {"by": str(event.get("by") or ""), "at": _iso(event.get("at"))}
        for event in events
        if isinstance(event, dict)
    ]


def _trust_tier(verified: list[dict]) -> str:
    """Derive the trust tier from verification events (spec section 5.3)."""
    if not verified:
        return "unverified"
    if any(event["by"].startswith("human:") for event in verified):
        return "human-reviewed"
    return "machine-confirmed"


def _sources(value: object, source_dir: str, known_ids: set[str]) -> list[dict]:
    """Normalize ``sources`` entries and give each a navigable ``href`` when possible."""
    sources: list[dict] = []
    for entry in value if isinstance(value, list) else []:
        if not isinstance(entry, dict) or not entry.get("resource"):
            continue
        normalized = {
            key: _iso(entry[key]) if key == "last_modified" else str(entry[key])
            for key in (
                "id",
                "resource",
                "title",
                "author",
                "usage_count",
                "last_modified",
            )
            if entry.get(key) not in (None, "")
        }
        resource = normalized["resource"]
        concept = _resolve_link(resource, source_dir)
        if concept in known_ids:
            normalized["href"] = f"#node:{urllib.parse.quote(concept, safe='/')}"
        elif "://" in resource:
            normalized["href"] = resource
        else:
            normalized["href"] = ""
        sources.append(normalized)
    return sources


def _properties_and_links(
    frontmatter: dict, concept_id: str, titles: dict[str, str], known_ids: set[str]
) -> tuple[list[list[str]], list[dict]]:
    """Render producer-defined keys as markdown, collecting typed links to concepts."""
    source_dir = posixpath.dirname(concept_id)
    properties: list[list[str]] = []
    links: list[dict] = []

    def cell(value: object, key: str) -> str:
        if isinstance(value, list):
            return ", ".join(cell(item, key) for item in value)
        if isinstance(value, dict):
            return "; ".join(f"{k}: {cell(v, key)}" for k, v in value.items())
        text = (
            _iso(value)
            if isinstance(value, (datetime.date, datetime.datetime))
            else str(value)
        )
        target = _resolve_link(text, source_dir) if text.strip() else None
        if target in known_ids:
            if target != concept_id:
                links.append({"source": concept_id, "target": target, "label": key})
            return f"[{titles[target]}](#node:{urllib.parse.quote(target, safe='/')})"
        return _rewrite_internal_links(text, concept_id, known_ids)

    for key, value in frontmatter.items():
        if key in _SPEC_KEYS or value in (None, "", []):
            continue
        properties.append([str(key), cell(value, str(key))])

    return properties, links


def _link_footnotes(body: str) -> str:
    """Drop ``[^id]:`` definitions and turn ``[^id]`` into links to the sources list."""
    body = _FOOTNOTE_DEFINITION.sub("", body).rstrip()
    return _FOOTNOTE_REFERENCE.sub(
        lambda match: (
            f'<sup class="fn"><a href="#src-{match.group(1)}">{match.group(1)}</a></sup>'
        ),
        body,
    )


def _split_document(path: pathlib.Path) -> tuple[dict, str, str | None]:
    """Split a document into ``(frontmatter, body, error)``."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, "", "no YAML frontmatter block."

    lines = text.splitlines()
    closing_index = next(
        (index for index in range(1, len(lines)) if lines[index].strip() == "---"),
        None,
    )
    if closing_index is None:
        return {}, "", "frontmatter block is not closed with '---'."

    try:
        parsed = yaml.safe_load("\n".join(lines[1:closing_index]))
    except yaml.YAMLError as error:
        return {}, "", f"unparseable frontmatter YAML ({error})."

    if not isinstance(parsed, dict):
        return {}, "", "frontmatter did not parse to a mapping."

    body = "\n".join(lines[closing_index + 1 :]).strip()

    return parsed, body, None


def _build_edges(concepts: list[Concept]) -> list[dict]:
    """Derive directed edges: typed ones from frontmatter, untyped ones from body links.

    A body link duplicating a typed frontmatter edge between the same pair is
    dropped, so each relationship is drawn once, with its label when it has one.
    """
    ids = {concept.id for concept in concepts}
    seen: set[tuple[str, str, str]] = set()
    typed_pairs: set[tuple[str, str]] = set()
    edges: list[dict] = []

    for concept in concepts:
        for link in concept.links:
            key = (link["source"], link["target"], link["label"])
            if link["target"] in ids and key not in seen:
                seen.add(key)
                typed_pairs.add((link["source"], link["target"]))
                edges.append(dict(link))

    for concept in concepts:
        source_links = "\n".join(
            [
                concept.body,
                concept.description,
                *(value for _, value in concept.properties),
                *(source.get("href", "") for source in concept.sources),
            ]
        )
        for target in re.findall(r"#node:([^)\s\"']+)", source_links):
            target = urllib.parse.unquote(target)
            key = (concept.id, target, "")
            pair = (concept.id, target)
            if (
                target in ids
                and target != concept.id
                and key not in seen
                and pair not in typed_pairs
            ):
                seen.add(key)
                edges.append({"source": concept.id, "target": target, "label": ""})

    return edges


def _read_log(bundle_root: pathlib.Path, known_ids: set[str]) -> str | None:
    """Return the bundle-root ``log.md`` markdown with in-bundle links rewritten."""
    log_path = bundle_root / "log.md"
    if not log_path.is_file():
        return None

    return _rewrite_internal_links(
        log_path.read_text(encoding="utf-8"), "log.md", known_ids
    )


def _read_index(bundle_root: pathlib.Path, known_ids: set[str]) -> str | None:
    """Return the bundle-root ``index.md`` body (frontmatter stripped, links rewritten)."""
    index_path = bundle_root / "index.md"
    if not index_path.is_file():
        return None

    _, body, error = _split_document(index_path)
    markdown = index_path.read_text(encoding="utf-8") if error is not None else body

    visible_lines: list[str] = []
    hidden_level: int | None = None
    for line in markdown.splitlines():
        heading = re.match(r"^(#{1,6})\s+", line)
        if (
            heading
            and hidden_level is not None
            and len(heading.group(1)) <= hidden_level
        ):
            hidden_level = None
        if heading and line[len(heading.group(1)) :].strip() == "_types":
            hidden_level = len(heading.group(1))
        if hidden_level is None:
            visible_lines.append(line)
    return _rewrite_internal_links("\n".join(visible_lines), "index.md", known_ids)


def _rewrite_internal_links(body: str, source_id: str, known_ids: set[str]) -> str:
    """Rewrite links that resolve to a concept in the bundle to ``#node:<id>``.

    Bundle-relative links (starting with ``/``) and relative links are resolved
    against the source document's directory; any that land on a known concept id
    are rewritten so the reader can intercept them for in-graph navigation.
    External and unresolved links are left untouched.
    """
    source_dir = posixpath.dirname(source_id)

    def replace(match: re.Match) -> str:
        target = match.group(1).strip()
        resolved = _resolve_link(target, source_dir)
        if resolved in known_ids:
            return match.group(0).replace(
                f"({target})", f"(#node:{urllib.parse.quote(resolved, safe='/')})"
            )

        return match.group(0)

    return _LINK_PATTERN.sub(replace, body)


def _resolve_link(target: str, source_dir: str) -> str | None:
    """Resolve a markdown link target to a bundle-relative concept id, or None."""
    link = urllib.parse.unquote(target.strip("<>").split("#", 1)[0].split("?", 1)[0])
    if not link.endswith(".md") or "://" in link:
        return None

    if link.startswith("/"):
        return posixpath.normpath(link.lstrip("/"))

    base = f"{source_dir}/" if source_dir else ""

    return posixpath.normpath(base + link)


def _render_html(
    bundle_name: str,
    concepts: list[Concept],
    edges: list[dict],
    log_markdown: str | None,
    index_markdown: str | None,
    type_schemas: dict[str, dict],
    assets: list[dict[str, str]],
) -> str:
    """Assemble the self-contained HTML document."""
    types = sorted({concept.type for concept in concepts})
    type_colors = {
        concept_type: _TYPE_PALETTE[index % len(_TYPE_PALETTE)]
        for index, concept_type in enumerate(types)
    }

    graph_data = {
        "title": bundle_name,
        "nodes": [
            {
                "id": concept.id,
                "title": concept.title,
                "type": concept.type,
                "description": concept.description,
                "tags": concept.tags,
                "resource": concept.resource,
                "body": concept.body,
                "color": type_colors[concept.type],
                "status": concept.status,
                "generated": concept.generated,
                "verified": concept.verified,
                "trust": concept.trust,
                "stale_after": concept.stale_after,
                "stale": concept.stale,
                "sources": concept.sources,
                "properties": concept.properties,
            }
            for concept in concepts
        ],
        "edges": edges,
        "files": assets,
        "types": [
            {"name": concept_type, "color": type_colors[concept_type]}
            for concept_type in types
        ],
        "typeSchemas": {
            name: type_schemas[name] for name in types if name in type_schemas
        },
        "log": log_markdown,
        "index": index_markdown,
    }

    payload = json.dumps(graph_data).replace("</", "<\\/")

    return _HTML_TEMPLATE.replace("__TITLE__", html.escape(bundle_name)).replace(
        "__DATA__", payload
    )


def _title_from_id(concept_id: str) -> str:
    """Derive a display title from a concept id when frontmatter omits one."""
    stem = posixpath.splitext(posixpath.basename(concept_id))[0]

    return stem.replace("-", " ").replace("_", " ").strip().title()


_HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__ — OKF knowledge graph</title>
<script src="https://cdn.jsdelivr.net/npm/cytoscape@3.30.2/dist/cytoscape.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/layout-base@2.0.1/layout-base.js"></script>
<script src="https://cdn.jsdelivr.net/npm/cose-base@2.2.0/cose-base.js"></script>
<script src="https://cdn.jsdelivr.net/npm/cytoscape-fcose@2.2.0/cytoscape-fcose.js"></script>
<script src="https://cdn.jsdelivr.net/npm/marked@12.0.0/marked.min.js"></script>
<style>
  :root {
    --bg:#ffffff; --sidebar:#f6f8fa; --ink:#1f2328; --muted:#656d76; --line:#d0d7de;
    --accent:#0969da; --hover:#eaeef2; --active:#ddf4ff; --code:#f6f8fa;
  }
  * { box-sizing: border-box; }
  html, body { margin:0; height:100%; color:var(--ink); background:var(--bg);
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif; font-size:14px; }
  .layout { display:flex; flex-direction:column; height:100vh; }
  header { display:flex; gap:14px; align-items:center; padding:9px 16px; border-bottom:1px solid var(--line); background:var(--sidebar); flex:0 0 auto; }
  header h1 { font-size:14px; margin:0; font-weight:600; white-space:nowrap; }
  header h1 span { color:var(--muted); font-weight:400; }
  .history-controls { display:flex; gap:4px; }
  .history-controls button { border:1px solid var(--line); border-radius:6px; background:var(--bg); color:var(--ink); cursor:pointer; padding:5px 9px; font:inherit; }
  .history-controls button:disabled { color:var(--muted); cursor:default; opacity:.55; }
  #mobile-actions { display:none; }
  .mobile-toggle { border:1px solid var(--line); border-radius:6px; padding:6px 9px; background:var(--bg); color:var(--ink); font:inherit; font-size:12px; cursor:pointer; }
  .mobile-toggle[aria-expanded="true"] { background:var(--active); border-color:var(--accent); }
  #search { margin-left:auto; flex:0 0 260px; padding:6px 10px; border-radius:6px; border:1px solid var(--line); background:var(--bg); color:var(--ink); font-size:13px; }
  .below { flex:1 1 auto; display:flex; min-height:0; }

  aside { flex:0 0 264px; display:flex; flex-direction:column; border-right:1px solid var(--line); background:var(--sidebar); min-height:0; }
  #nav { flex:1 1 auto; overflow-y:auto; padding:10px 8px; }
  #nav .nav-attention { animation:nav-attention 1.1s ease-in-out; }
  @keyframes nav-attention {
    0%, 40%, 80%, 100% { box-shadow:inset 0 0 0 0 transparent; }
    20%, 60% { background-color:#b6ddff; box-shadow:inset 0 0 0 2px var(--accent); }
  }
  @media (prefers-reduced-motion: reduce) {
    #nav .nav-attention { animation:none; outline:2px solid var(--accent); outline-offset:-2px; }
  }
  #nav ul { list-style:none; margin:0; padding:0; }
  #nav .dir > .label { display:flex; align-items:center; gap:5px; font-size:11px; font-weight:600; letter-spacing:.04em; color:var(--muted); padding:6px 8px 4px; cursor:pointer; user-select:none; border-radius:6px; }
  #nav .dir > .label:hover { background:var(--hover); color:var(--ink); }
  #nav .dir > .label.active { background:var(--active); color:var(--ink); }
  #nav .dir > .label .caret, #nav .dir > .label .caret-toggle { display:inline-block; width:10px; transition:transform .15s; }
  #nav .dir:not(.collapsed) > .label .caret, #nav .dir:not(.collapsed) > .label .caret-toggle { transform:rotate(90deg); }
  #nav .dir > .label .caret-toggle { border:0; background:none; color:inherit; padding:0; cursor:pointer; font:inherit; }
  #nav .dir > .label .overview-link { padding:0; color:inherit; font-size:inherit; font-weight:inherit; letter-spacing:inherit; }
  #nav .dir > .label .overview-link.active { background:transparent; }
  #nav .dir > .label .count { font-weight:400; color:var(--muted); text-transform:none; letter-spacing:0; }
  #nav .dir.collapsed > ul { display:none; }
  #nav .dir ul { margin-left:12px; border-left:1px solid var(--line); }
  #nav a { display:flex; align-items:center; gap:8px; padding:5px 8px; border-radius:6px; color:var(--ink); text-decoration:none; font-size:13px; line-height:1.3; }
  #nav a:hover { background:var(--hover); }
  #nav a.active { background:var(--active); font-weight:600; }
  #nav a.typematch:not(.active) { background:#fff3bf; }
  #nav a .dot { width:8px; height:8px; border-radius:50%; flex:0 0 auto; }
  #nav a.hidden { display:none; }
  #nav a.homelink { font-weight:600; margin-bottom:6px; }
  #nav a.asset-link { color:var(--muted); }
  #nav a.asset-link .file-kind { font-size:10px; margin-left:auto; }
  #loglink { flex:0 0 auto; border-top:1px solid var(--line); padding:8px; }
  #loglink a { display:flex; align-items:center; gap:8px; padding:7px 10px; border-radius:6px; color:var(--muted); text-decoration:none; font-size:13px; }
  #loglink a:hover { background:var(--hover); color:var(--ink); }
  #loglink a.active { background:var(--active); color:var(--ink); font-weight:600; }

  main { flex:1 1 auto; display:flex; flex-direction:row; min-width:0; min-height:0; }
  #doc { flex:1 1 auto; overflow-y:auto; padding:26px 36px; min-width:0; }
  #doc > * { max-width:820px; }
  main.graph-only #doc { display:none; }
  #graph-wrap { flex:0 0 42%; border-left:1px solid var(--line); display:flex; flex-direction:column; position:relative; min-height:0; min-width:0; background:var(--bg); }
  main.graph-only #graph-wrap { flex:1 1 auto; border-left:none; }
  .pane-switch { flex:0 0 auto; display:flex; gap:4px; padding:8px 12px; border-bottom:1px solid var(--line); }
  .pane-switch button { border:1px solid var(--line); border-radius:6px; background:var(--bg); color:var(--muted); padding:5px 10px; font:inherit; font-size:12px; cursor:pointer; }
  .pane-switch button[aria-selected="true"] { background:var(--active); border-color:var(--accent); color:var(--ink); font-weight:600; }
  #graph-area { flex:1 1 auto; display:flex; flex-direction:column; min-height:0; }
  #graph-wrap[data-view="backlinks"] #graph-area { visibility:hidden; pointer-events:none; }
  #backlinks { display:none; position:absolute; inset:48px 0 0; overflow-y:auto; padding:18px 16px; background:var(--sidebar); }
  #graph-wrap[data-view="backlinks"] #backlinks { display:block; }
  #backlinks h2 { font-size:12px; text-transform:uppercase; letter-spacing:.05em; color:var(--muted); margin:0 0 12px; }
  #backlinks p { color:var(--muted); font-size:13px; line-height:1.5; }
  #backlinks .backlink-group { margin:0 0 12px; padding:12px; border:1px solid var(--line); border-radius:12px;
    background:var(--bg); box-shadow:0 3px 10px #1f23280d; }
  #backlinks h3 { display:flex; align-items:center; gap:8px; margin:0 0 7px; }
  #backlinks .group-count { color:var(--muted); font-size:11px; font-weight:500; }
  #backlinks ul { list-style:none; padding:0; margin:0; }
  #backlinks li { margin:0; }
  #backlinks a { display:block; padding:7px 9px; color:var(--ink); text-decoration:none; border-radius:6px; }
  #backlinks a:hover, #backlinks a:focus-visible { background:var(--hover); }
  #legend { flex:0 0 auto; display:flex; flex-wrap:wrap; align-items:center; gap:2px 6px; padding:8px 12px; border-bottom:1px solid var(--line); }
  #legend .legend-title { font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:.04em; color:var(--muted); margin-right:4px; }
  #legend .legend-item { display:inline-flex; align-items:center; gap:5px; cursor:pointer; border:0; background:none; font:inherit; font-size:11.5px; color:var(--muted); padding:2px 6px; border-radius:5px; }
  #legend .legend-item:hover { background:var(--hover); color:var(--ink); }
  #legend .legend-item.active { background:var(--active); color:var(--ink); font-weight:600; }
  #legend .sw { width:10px; height:10px; border-radius:3px; flex:0 0 auto; }
  #legend .relayout { margin-left:auto; border:1px solid var(--line); background:var(--bg); color:var(--muted); font:inherit; font-size:11.5px; padding:2px 8px; border-radius:5px; cursor:pointer; }
  #legend .relayout:hover { background:var(--hover); color:var(--ink); }
  #graph-container { flex:1 1 auto; position:relative; min-height:0; }
  #graph { position:absolute; inset:0; }
  #graph-caption { position:absolute; top:8px; left:12px; font-size:11px; color:var(--muted); pointer-events:none; }
  #node-menu { position:absolute; z-index:5; min-width:220px; padding:4px; border:1px solid var(--line);
    border-radius:8px; background:var(--bg); box-shadow:0 8px 24px #1f232833; }
  #node-menu[hidden] { display:none; }
  #node-menu button { display:block; width:100%; border:0; border-radius:5px; background:none; color:var(--ink);
    font:inherit; font-size:12px; text-align:left; padding:8px 10px; cursor:pointer; }
  #node-menu button:hover, #node-menu button:focus-visible { background:var(--hover); }
  #node-menu button:disabled { color:var(--muted); cursor:default; }
  #node-menu button[hidden] { display:none; }

  #doc h1 { font-size:24px; margin:0 0 2px; }
  #doc h2 { font-size:17px; margin:1.5em 0 .4em; padding-bottom:5px; border-bottom:1px solid var(--line); }
  #doc .prose h1 { font-size:17px; font-weight:600; margin:1.6em 0 .4em; padding-bottom:5px; border-bottom:1px solid var(--line); }
  #doc .meta { display:flex; align-items:center; gap:10px; margin:8px 0 16px; font-size:12.5px; }
  #doc .badge, #backlinks .badge { flex:0 0 auto; display:inline-block; padding:2px 9px; border-radius:11px; font-size:11px; color:#fff; font-weight:600; }
  #doc .resource { flex:0 1 auto; min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  #doc .meta-right { flex:0 0 auto; margin-left:auto; display:flex; align-items:center; gap:8px; }
  #doc .tags-inline { display:flex; gap:5px; }
  #doc .tags-inline code { color:var(--muted); font-size:11px; }
  #doc .summary { margin:0 0 18px; color:var(--muted); font-size:14px; line-height:1.5; }
  #doc a { color:var(--accent); text-decoration:none; }
  #doc a:hover { text-decoration:underline; }
  #doc a.xref { border-bottom:1px dotted var(--accent); }
  #doc a.flash { background:#fff3bf; box-shadow:0 0 0 3px #fff3bf; border-radius:3px; transition:background .3s, box-shadow .3s; }
  #doc table { border-collapse:collapse; font-size:13px; margin:12px 0; }
  #doc th, #doc td { border:1px solid var(--line); padding:6px 10px; text-align:left; }
  #doc th { background:var(--sidebar); }
  #doc th[title] { text-decoration:underline dotted; text-underline-offset:3px; cursor:help; }
  #doc .prop-details { margin:4px 0 16px; }
  #doc .prop-details summary { color:var(--muted); cursor:pointer; font-size:12px; }
  #doc code { font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:85%; background:var(--code); padding:.15em .4em; border-radius:5px; }
  #doc pre { background:var(--code); padding:13px; border-radius:8px; overflow-x:auto; }
  #doc pre code { background:none; padding:0; }
  #doc .lifecycle { display:flex; flex-wrap:wrap; gap:6px; margin:-6px 0 12px; }
  #doc .pill { display:inline-block; padding:1px 8px; border-radius:10px; font-size:11px; font-weight:600; border:1px solid var(--line); color:var(--muted); background:var(--bg); }
  #doc .pill.status-draft { color:#9a6700; border-color:#d4a72c; background:#fff8c5; }
  #doc .pill.status-deprecated { color:#82071e; border-color:#ff8182; background:#ffebe9; }
  #doc table.props { margin:4px 0 18px; }
  #doc table.props th { white-space:nowrap; font-weight:600; width:1%; }
  #doc .sources h1 { font-size:17px; font-weight:600; margin:1.6em 0 .4em; padding-bottom:5px; border-bottom:1px solid var(--line); }
  #doc .sources li { margin:3px 0; }
  #doc ul.dirlist { list-style:none; padding-left:0; }
  #doc ul.dirlist li { margin:4px 0; }
  #doc ul.dirlist .dot { display:inline-block; width:8px; height:8px; border-radius:50%; margin-right:6px; }
  #doc .sources li:target, #doc .sources li.flash { background:#fff3bf; }
  #doc sup.fn a { text-decoration:none; font-size:10px; padding:0 2px; }
  #nav a.deprecated span:last-child { text-decoration:line-through; color:var(--muted); }
  #nav a.draft span:last-child { font-style:italic; }

  @media (max-width: 860px) {
    .layout { height:100vh; height:100dvh; }
    header { flex-wrap:wrap; gap:8px; padding:8px 10px; }
    header h1 { flex:1 1 auto; overflow:hidden; text-overflow:ellipsis; }
    #mobile-actions { display:flex; gap:6px; }
    #search { order:3; flex:1 0 100%; width:100%; margin-left:0; }
    .below { position:relative; }
    aside { display:none; position:absolute; inset:0; z-index:10; width:100%; background:var(--sidebar); border-right:0; }
    body.nav-open aside { display:flex; }
    main { width:100%; }
    #doc { padding:20px 16px 32px; }
    #doc > * { max-width:none; }
    #doc .meta { align-items:flex-start; flex-wrap:wrap; }
    #doc .resource { flex-basis:100%; }
    #doc .meta-right { margin-left:0; }
    #doc table { display:block; max-width:100%; overflow-x:auto; }
    #graph-wrap { display:none; flex:1 1 auto; border-left:0; }
    main.mobile-graph #doc, main.graph-only #doc { display:none; }
    main.mobile-graph #graph-wrap, main.graph-only #graph-wrap { display:flex; }
  }
</style>
</head>
<body>
<div class="layout">
  <header>
    <h1>__TITLE__ <span>· OKF</span></h1>
    <div class="history-controls" aria-label="Navigation history">
      <button id="nav-back" type="button" title="Back" aria-label="Back" disabled>←</button>
      <button id="nav-forward" type="button" title="Forward" aria-label="Forward" disabled>→</button>
    </div>
    <div id="mobile-actions">
      <button id="nav-toggle" class="mobile-toggle" type="button" aria-controls="nav" aria-expanded="false">Contents</button>
      <button id="graph-toggle" class="mobile-toggle" type="button" aria-controls="graph-wrap" aria-expanded="false">Links</button>
    </div>
    <input id="search" type="search" placeholder="Search concepts…" autocomplete="off">
  </header>
  <div class="below">
    <aside>
      <nav id="nav"></nav>
      <div id="loglink"></div>
    </aside>
    <main id="main" class="graph-only">
      <div id="doc"></div>
      <div id="graph-wrap" data-view="backlinks">
        <div class="pane-switch" role="tablist" aria-label="Right pane">
          <button type="button" role="tab" data-view="backlinks" aria-selected="true">Backlinks</button>
          <button type="button" role="tab" data-view="graph" aria-selected="false">Graph</button>
        </div>
        <div id="backlinks" aria-live="polite"></div>
        <div id="graph-area">
          <div id="legend"></div>
          <div id="graph-container">
            <div id="graph"></div>
            <div id="graph-caption"></div>
            <div id="node-menu" role="menu" aria-label="Node actions" hidden>
              <button type="button" role="menuitem" data-action="focus">Center and show connections</button>
              <button type="button" role="menuitem" data-action="toggle">Collapse into parent directory</button>
              <button type="button" role="menuitem" data-action="collapse-parent" hidden>Collapse into parent directory</button>
              <button type="button" role="menuitem" data-action="collapse-all" hidden>Collapse all</button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</div>
<script>
const DATA = __DATA__;
const byId = Object.fromEntries(DATA.nodes.map(n => [n.id, n]));
const main = document.getElementById('main');
const doc = document.getElementById('doc');
const caption = document.getElementById('graph-caption');
const graphContainer = document.getElementById('graph-container');
const nodeMenu = document.getElementById('node-menu');
const navToggle = document.getElementById('nav-toggle');
const graphToggle = document.getElementById('graph-toggle');
const graphWrap = document.getElementById('graph-wrap');
const backlinks = document.getElementById('backlinks');
const backButton = document.getElementById('nav-back');
const forwardButton = document.getElementById('nav-forward');

document.querySelectorAll('.pane-switch button').forEach(button => button.addEventListener('click', () => {
  graphWrap.dataset.view = button.dataset.view;
  document.querySelectorAll('.pane-switch button').forEach(tab =>
    tab.setAttribute('aria-selected', String(tab === button)));
  if (button.dataset.view === 'graph') relayout();
}));

function closeMobilePanels() {
  document.body.classList.remove('nav-open');
  main.classList.remove('mobile-graph');
  navToggle.setAttribute('aria-expanded', 'false');
  graphToggle.setAttribute('aria-expanded', 'false');
}

navToggle.addEventListener('click', () => {
  const willOpen = !document.body.classList.contains('nav-open');
  closeMobilePanels();
  document.body.classList.toggle('nav-open', willOpen);
  navToggle.setAttribute('aria-expanded', String(willOpen));
});

graphToggle.addEventListener('click', () => {
  const willOpen = !main.classList.contains('mobile-graph');
  closeMobilePanels();
  main.classList.toggle('mobile-graph', willOpen);
  graphToggle.setAttribute('aria-expanded', String(willOpen));
  if (willOpen) relayout();
});

/* ---------- directory state (shared by the sidebar tree and the graph) ---------- */
// Every directory starts collapsed. A collapsed directory is drawn as one "directory node"
// standing in for everything below it; edges to its concepts are rerouted to it. The same
// `expanded` set drives the sidebar tree, so the two views are always in sync.
const DIR_PREFIX = 'dir:';
const expanded = new Set();
const dirs = {};   // path -> { path, name, parent, concepts: [all ids below], types: Set }
DATA.nodes.forEach(n => {
  const parts = n.id.split('/');
  for (let i = 1; i < parts.length; i++) {
    const path = parts.slice(0, i).join('/');
    const d = dirs[path] || (dirs[path] = { path, name: parts[i - 1], parent: parts.slice(0, i - 1).join('/') || null,
                                            concepts: [], types: new Set(), files: 0 });
    d.concepts.push(n.id);
    d.types.add(n.type);
  }
});
DATA.files.forEach(file => {
  const parts = file.id.split('/');
  for (let i = 1; i < parts.length; i++) {
    const path = parts.slice(0, i).join('/');
    dirs[path] ||= { path, name: parts[i - 1], parent: parts.slice(0, i - 1).join('/') || null,
                     concepts: [], types: new Set(), files: 0 };
    dirs[path].files++;
  }
});
Object.values(dirs).forEach(d => { d.overviewId = byId[d.path + '.md'] ? d.path + '.md' : null; });
const isDirId = id => id.startsWith(DIR_PREFIX);
const dirOf = id => isDirId(id) ? id.slice(DIR_PREFIX.length) : id;
function directoryForNode(id) {
  if (isDirId(id)) return dirOf(id);
  const path = id.endsWith('.md') ? id.slice(0, -3) : '';
  return dirs[path] && dirs[path].overviewId === id ? path : null;
}
function ancestorsOf(path) {          // ['a', 'a/b'] for a concept 'a/b/c.md' or a directory 'a/b/c'
  const parts = path.split('/');
  const out = [];
  for (let i = 1; i < parts.length; i++) out.push(parts.slice(0, i).join('/'));
  return out;
}
function parentDirOf(conceptId) { const a = ancestorsOf(conceptId); return a.length ? a[a.length - 1] : null; }
// The graph node currently standing for a concept: itself, or its topmost collapsed ancestor.
function representative(conceptId) {
  for (const d of ancestorsOf(conceptId)) if (!expanded.has(d)) return dirs[d].overviewId || DIR_PREFIX + d;
  return conceptId;
}
function dirLabel(path) {
  return dirs[path].name;
}

/* ---------- graph ---------- */
const cy = cytoscape({
  container: document.getElementById('graph'),
  elements: [],
  style: [
    { selector: 'node', style: {
        'background-color': 'data(color)', 'label': 'data(label)', 'color': '#1f2328',
        'font-size': '8px', 'text-wrap': 'wrap', 'text-max-width': '80px',
        'text-valign': 'bottom', 'text-margin-y': 3, 'width': 15, 'height': 15,
        'border-width': 1.5, 'border-color': '#ffffff' } },
    { selector: 'edge', style: {
        'width': 1, 'line-color': '#c8d1da', 'target-arrow-color': '#c8d1da',
        'target-arrow-shape': 'triangle', 'curve-style': 'bezier', 'arrow-scale': .7 } },
    { selector: 'edge.typed', style: { 'line-color': '#8c959f', 'target-arrow-color': '#8c959f' } },
    { selector: 'edge.near.typed', style: {
        'label': 'data(label)', 'font-size': '7px', 'color': '#57606a', 'text-rotation': 'autorotate',
        'text-background-color': '#ffffff', 'text-background-opacity': 1, 'text-background-padding': '1px' } },
    { selector: 'node.status-deprecated', style: { 'opacity': .45, 'border-style': 'dashed', 'border-color': '#82071e' } },
    { selector: 'node.status-draft', style: { 'border-style': 'dashed', 'border-color': '#9a6700' } },
    { selector: 'node.dir', style: {
        'shape': 'round-rectangle', 'background-color': '#eaeef2', 'border-color': '#57606a', 'border-width': 2,
        'width': 'data(size)', 'height': 'data(size)', 'font-size': '10px', 'font-weight': 'bold', 'color': '#24292f' } },
    { selector: 'edge.agg', style: { 'width': 'data(weight)' } },
    { selector: 'node.sel', style: { 'border-color': '#0969da', 'border-width': 3, 'font-size': '10px', 'font-weight': 'bold', 'width': 20, 'height': 20 } },
    { selector: 'node.dir.sel', style: { 'width': 'data(size)', 'height': 'data(size)' } },
    { selector: 'node.overview', style: { 'shape': 'round-rectangle', 'width': 'data(size)', 'height': 'data(size)',
        'font-size': '10px', 'font-weight': 'bold' } },
    { selector: 'node.overview.sel', style: { 'width': 'data(size)', 'height': 'data(size)' } },
    { selector: '.faded', style: { 'opacity': .12 } },
    { selector: 'node.hidden', style: { 'display': 'none' } },
  ],
  wheelSensitivity: 0.2,
  maxZoom: 2.5,   // small bundles would otherwise zoom a single node to fill the pane
});

// Full layouts use fcose (spectral start + few force iterations, much faster than cose on
// hundreds of nodes); cose is the fallback when the fcose scripts did not load.
const HAS_FCOSE = typeof cytoscapeFcose !== 'undefined';
function graphLayout() {
  return HAS_FCOSE
    ? { name: 'fcose', quality: 'default', randomize: true, animate: false, nodeDimensionsIncludeLabels: true,
        idealEdgeLength: 110, nodeRepulsion: 9000, nodeSeparation: 90, packComponents: true, padding: 40 }
    : { name: 'cose', animate: false, nodeDimensionsIncludeLabels: true, randomize: true,
        idealEdgeLength: 150, nodeRepulsion: 22000, nodeOverlap: 60,
        gravity: 0.2, componentSpacing: 160, numIter: 1500, padding: 40 };
}

// Full re-layout of everything visible (initial view and the "Re-layout" button), then the
// overlap pass so labels never sit on top of each other.
function runLayout(done) {
  const layout = cy.layout(graphLayout());
  layout.one('layoutstop', () => requestAnimationFrame(() => { separateOverlaps(true); if (done) done(); }));
  layout.run();
}

// Expand/collapse never re-lays out the whole graph: only the newly shown nodes are placed,
// in a disc around the directory node they came out of, laid out among themselves (fcose on
// the small subset) and scaled to fit; then the overlap pass nudges neighbours apart. Existing
// nodes keep their positions, so the cost depends on what changed, not on the graph size.
function placeNewNodes(groups) {
  groups.forEach(({ anchor, nodes }) => {
    if (nodes.length === 1) { nodes[0].position(anchor); return; }
    const eles = nodes.union(nodes.edgesWith(nodes));
    eles.layout({ ...graphLayout(), fit: false, packComponents: false, padding: 0 }).run();
    const bb = nodes.boundingBox({ includeLabels: false });
    const radius = 45 * Math.sqrt(nodes.length) + 30;
    const scale = (2 * radius) / Math.max(bb.w, bb.h, 1);
    const cx = (bb.x1 + bb.x2) / 2, cyy = (bb.y1 + bb.y2) / 2;
    nodes.positions(n => ({ x: anchor.x + (n.position('x') - cx) * scale, y: anchor.y + (n.position('y') - cyy) * scale }));
  });
}

// A same-named overview serves as the directory node without losing its concept identity.
function graphNodeForRepresentative(id) {
  if (isDirId(id)) {
    const path = dirOf(id);
    return { data: { id, label: dirLabel(path), isDir: true, color: '#57606a',
                     size: Math.round(24 + 6 * Math.sqrt(dirs[path].concepts.length)) }, classes: 'dir' };
  }
  const n = byId[id];
  const path = directoryForNode(id);
  if (path) return { data: { id, label: n.title, color: n.color,
                            size: Math.round(24 + 6 * Math.sqrt(dirs[path].concepts.length)) },
                     classes: 'overview status-' + n.status };
  return { data: { id, label: n.title, color: n.color }, classes: 'status-' + n.status };
}

// Rebuild the visible graph from `expanded`: concept nodes for expanded directories,
// one node per topmost collapsed directory, and edges rerouted to whatever
// node currently represents each endpoint (parallel edges merged, with a count).
function syncGraph(done) {
  const old = {};
  cy.nodes().forEach(n => { old[n.id()] = { ...n.position() }; });
  const wanted = new Map();
  DATA.nodes.forEach(n => {
    const r = representative(n.id);
    if (wanted.has(r)) return;
    wanted.set(r, graphNodeForRepresentative(r));
  });
  const agg = new Map();
  DATA.edges.forEach(e => {
    const s = representative(e.source), t = representative(e.target);
    if (s === t) return;
    const key = s + '->' + t;
    const a = agg.get(key) || { s, t, edges: [], labels: new Set() };
    a.edges.push(e);
    if (e.label) a.labels.add(e.label);
    agg.set(key, a);
  });

  cy.batch(() => {
    cy.edges().remove();
    cy.nodes().filter(n => !wanted.has(n.id())).remove();
    const fresh = [];
    wanted.forEach((el, id) => {
      if (cy.getElementById(id).nonempty()) return;
      const anchor = newNodeAnchor(id, old);
      fresh.push(anchor ? { ...el, position: { ...anchor.pos }, data: { ...el.data, anchorKey: anchor.key } } : el);
    });
    cy.add(fresh);
    cy.add([...agg.values()].map(a => ({
      data: { id: 'e:' + a.s + '->' + a.t, source: a.s, target: a.t,
              label: [...a.labels].join(', ') + (a.edges.length > 1 ? ' ×' + a.edges.length : ''),
              weight: Math.min(1 + Math.log2(a.edges.length), 5), links: a.edges },
      classes: [a.labels.size ? 'typed' : '', a.edges.length > 1 ? 'agg' : ''].join(' '),
    })));
  });
  paintTreeState();
  const finish = () => { if (done) done(); else clearHighlight(); };
  if (!Object.keys(old).length) { runLayout(finish); return; }
  const groups = new Map();
  cy.nodes().filter(n => n.data('anchorKey')).forEach(n => {
    const key = n.data('anchorKey');
    const g = groups.get(key) || { anchor: { ...n.position() }, nodes: cy.collection() };
    g.nodes = g.nodes.union(n);
    groups.set(key, g);
    n.removeData('anchorKey');
  });
  placeNewNodes([...groups.values()]);
  separateOverlaps(false);
  finish();
}

// Where a newly shown node belongs: around the directory node it was folded into (when
// expanding), or at the centroid of the nodes it now replaces (when collapsing). Nodes with
// the same anchor key are laid out together.
function newNodeAnchor(id, old) {
  if (isDirId(id)) {
    const path = dirOf(id);
    const pts = Object.keys(old).filter(o => (isDirId(o) ? dirOf(o) : o).startsWith(path + '/')).map(o => old[o]);
    if (!pts.length) return null;
    return { key: 'collapse:' + path,
             pos: { x: pts.reduce((a, p) => a + p.x, 0) / pts.length, y: pts.reduce((a, p) => a + p.y, 0) / pts.length } };
  }
  for (const d of ancestorsOf(id).reverse()) {
    const p = old[dirs[d].overviewId || DIR_PREFIX + d];
    if (p) return { key: 'expand:' + d, pos: p };
  }
  return null;
}

// Change the expanded state, then bring the tree and the graph back in sync.
function setExpanded(paths, open, done) {
  let changed = false;
  paths.forEach(p => {
    if (!dirs[p]) return;
    if (open && !expanded.has(p)) { expanded.add(p); changed = true; }
    if (!open && expanded.has(p)) { expanded.delete(p); changed = true; }
  });
  if (changed) syncGraph(done); else if (done) done();
}
function expandDir(path, done) { setExpanded([...ancestorsOf(path + '/x'), path], true, done); }
function collapseDir(path, done) { setExpanded([path], false, done); }
function collapseAllDirs(done) { stopViewportMotion(); setExpanded([...expanded], false, done); }
function revealConcept(id, done) { setExpanded(ancestorsOf(id), true, done); }

function separateOverlaps(fitAll, iterations = 60, pad = 10) {
  // Measure each label-inclusive box once, then push overlapping pairs apart on plain arrays.
  // Candidate pairs come from a uniform grid whose cell is at least the largest box, so two
  // boxes can only overlap if they sit in the same or neighbouring cells: ~O(n) per round
  // instead of comparing every pair.
  const nodes = cy.nodes();
  const n = nodes.length;
  const x = new Float64Array(n), y = new Float64Array(n);
  const hw = new Float64Array(n), hh = new Float64Array(n), ox = new Float64Array(n), oy = new Float64Array(n);
  let cell = 1;
  nodes.forEach((node, i) => {
    const p = node.position(), bb = node.boundingBox({ includeLabels: true });
    x[i] = p.x; y[i] = p.y;
    hw[i] = (bb.x2 - bb.x1) / 2; hh[i] = (bb.y2 - bb.y1) / 2;
    ox[i] = (bb.x1 + bb.x2) / 2 - p.x; oy[i] = (bb.y1 + bb.y2) / 2 - p.y;   // label sits below the node
    cell = Math.max(cell, 2 * hw[i] + pad, 2 * hh[i] + pad);
  });
  for (let it = 0; it < iterations; it++) {
    const grid = new Map();
    const gx = new Int32Array(n), gy = new Int32Array(n);
    for (let i = 0; i < n; i++) {
      gx[i] = Math.floor((x[i] + ox[i]) / cell); gy[i] = Math.floor((y[i] + oy[i]) / cell);
      const key = gx[i] + ',' + gy[i];
      const bucket = grid.get(key);
      if (bucket) bucket.push(i); else grid.set(key, [i]);
    }
    let moved = false;
    for (let i = 0; i < n; i++) {
      for (let cx = gx[i] - 1; cx <= gx[i] + 1; cx++) {
        for (let cyy = gy[i] - 1; cyy <= gy[i] + 1; cyy++) {
          const bucket = grid.get(cx + ',' + cyy);
          if (!bucket) continue;
          for (const j of bucket) {
            if (j <= i) continue;
            let dx = (x[i] + ox[i]) - (x[j] + ox[j]);
            let dy = (y[i] + oy[i]) - (y[j] + oy[j]);
            const overlapX = hw[i] + hw[j] + pad - Math.abs(dx);
            const overlapY = hh[i] + hh[j] + pad - Math.abs(dy);
            if (overlapX > 0 && overlapY > 0) {
              const dist = Math.hypot(dx, dy) || 0.01;
              const push = Math.min(overlapX, overlapY) / 2;
              dx /= dist; dy /= dist;
              x[i] += dx * push; y[i] += dy * push;
              x[j] -= dx * push; y[j] -= dy * push;
              moved = true;
            }
          }
        }
      }
    }
    if (!moved) break;
  }
  cy.batch(() => nodes.forEach((node, i) => node.position({ x: x[i], y: y[i] })));
  if (fitAll) cy.fit(undefined, 30);
}

// Clicks: the single-click action waits DOUBLE_CLICK_MS and is cancelled when a second click
// on the same target arrives, so a double-click never first runs the single-click action
// (e.g. zooming to the node). 150 ms keeps clicks responsive; slower double-clicks may
// register as two single clicks.
const DOUBLE_CLICK_MS = 150;
let pendingClick = null;
let lastGraphDouble = null;
function handleGraphDoubleClick(target) {
  const id = target === cy ? null : target.id();
  const now = Date.now();
  if (lastGraphDouble && lastGraphDouble.id === id && now - lastGraphDouble.at < DOUBLE_CLICK_MS * 2) return;
  lastGraphDouble = { id, at: now };
  onDoubleClick(target);
}
cy.on('tap', ev => {
  hideNodeMenu();
  const target = ev.target;
  const targetId = target === cy ? null : target.id();
  if (pendingClick && pendingClick.id === targetId) {
    clearTimeout(pendingClick.timer);
    pendingClick = null;
    handleGraphDoubleClick(target);
    return;
  }
  if (pendingClick) { clearTimeout(pendingClick.timer); pendingClick.run(); }   // a click elsewhere settles the previous one
  const run = () => onSingleClick(target);
  pendingClick = { id: targetId, run, timer: setTimeout(() => { pendingClick = null; run(); }, DOUBLE_CLICK_MS) };
});
// Cytoscape also recognises slower double taps. Keep the 150 ms single-click delay,
// but let its native event finish the double action when our tap window has elapsed.
cy.on('dbltap', ev => {
  const target = ev.target;
  const targetId = target === cy ? null : target.id();
  if (pendingClick) {
    clearTimeout(pendingClick.timer);
    if (pendingClick.id !== targetId) pendingClick.run();
    pendingClick = null;
  }
  handleGraphDoubleClick(target);
});

function onSingleClick(target) {
  if (target === cy) { clearHighlight(); return; }                 // empty space: deselect, keep the doc open
  if (target.isEdge()) { openEdgeLink(target); return; }           // open the source doc at the link behind the edge
  focusConnections(target.id());
}

// A directory can toggle its own children or fold into its parent. Graph double-clicks
// use the latter for nested directories; the sidebar and menu can still toggle children.
function toggleDirectory(path, attention = true) {
  if (expanded.has(path)) collapseDir(path, () => openDir(path, attention));
  else expandDir(path, () => openDir(path, attention));
}

function collapseNodeIntoParent(id, attention = true) {
  const directory = directoryForNode(id);
  const parent = parentDirOf(directory || id);
  if (parent) collapseDir(parent, () => openDir(parent, attention));
  return !!parent;
}

function onNodeDoubleClick(id, attention = true) {
  const directory = directoryForNode(id);
  if (!collapseNodeIntoParent(id, attention) && directory) toggleDirectory(directory, attention);
}

// Empty graph space or an edge resets the zoom to fit everything.
function onDoubleClick(target) {
  stopViewportMotion();
  if (target === cy || target.isEdge()) {
    cy.animate({ fit: { eles: cy.elements(), padding: 30 } }, { duration: 300 });
    return;
  }
  onNodeDoubleClick(target.id());
}

// Reveal the actual concepts behind links to collapsed directory nodes. For a
// selected directory, only links visible outside that directory are followed.
function connectedDirectories(id) {
  const paths = new Set();
  DATA.edges.forEach(edge => {
    const source = representative(edge.source), target = representative(edge.target);
    if (source === target) return;
    const other = source === id ? edge.target : target === id ? edge.source : null;
    if (other) ancestorsOf(other).forEach(path => paths.add(path));
  });
  return [...paths];
}

function focusConnections(id) {
  const keepMobileGraph = window.matchMedia('(max-width: 860px)').matches &&
    (main.classList.contains('graph-only') || main.classList.contains('mobile-graph'));
  setExpanded(connectedDirectories(id), true, () => {
    if (isDirId(id)) openDir(dirOf(id));
    else openConcept(id);
    if (keepMobileGraph) {
      main.classList.add('mobile-graph');
      graphToggle.setAttribute('aria-expanded', 'true');
    }
  });
}

let menuNodeId = null;
function hideNodeMenu() {
  nodeMenu.hidden = true;
  menuNodeId = null;
}

function showNodeMenu(id, position) {
  menuNodeId = id;
  nodeMenu.querySelector('[data-action="focus"]').hidden = false;
  nodeMenu.querySelector('[data-action="collapse-all"]').hidden = true;
  const toggle = nodeMenu.querySelector('[data-action="toggle"]');
  toggle.hidden = false;
  const collapseParent = nodeMenu.querySelector('[data-action="collapse-parent"]');
  const directory = directoryForNode(id);
  toggle.textContent = directory ? (expanded.has(directory) ? 'Collapse directory' : 'Expand directory') : 'Collapse into parent directory';
  toggle.disabled = !directory && !parentDirOf(id);
  collapseParent.hidden = !directory || !parentDirOf(directory);
  nodeMenu.hidden = false;
  nodeMenu.style.left = Math.max(0, Math.min(position.x, graphContainer.clientWidth - nodeMenu.offsetWidth - 4)) + 'px';
  nodeMenu.style.top = Math.max(0, Math.min(position.y, graphContainer.clientHeight - nodeMenu.offsetHeight - 4)) + 'px';
  nodeMenu.querySelector('[data-action="focus"]').focus();
}

function showGraphMenu(position) {
  menuNodeId = null;
  nodeMenu.querySelectorAll('button[data-action]').forEach(button => {
    button.hidden = button.dataset.action !== 'collapse-all';
  });
  nodeMenu.hidden = false;
  nodeMenu.style.left = Math.max(0, Math.min(position.x, graphContainer.clientWidth - nodeMenu.offsetWidth - 4)) + 'px';
  nodeMenu.style.top = Math.max(0, Math.min(position.y, graphContainer.clientHeight - nodeMenu.offsetHeight - 4)) + 'px';
  nodeMenu.querySelector('[data-action="collapse-all"]').focus();
}

function onNodeMenuAction(action, id) {
  if (action === 'collapse-all') collapseAllDirs(() => { clearHighlight(); relayout(); });
  else if (action === 'focus') focusConnections(id);
  else if (action === 'toggle') {
    const directory = directoryForNode(id);
    if (directory) toggleDirectory(directory);
    else {
      const node = cy.getElementById(id);
      if (node.nonempty()) onDoubleClick(node);
    }
  } else if (action === 'collapse-parent' && directoryForNode(id)) collapseNodeIntoParent(id);
}

nodeMenu.addEventListener('click', ev => {
  const button = ev.target.closest('button[data-action]');
  if (!button || (!menuNodeId && button.dataset.action !== 'collapse-all')) return;
  const id = menuNodeId;
  hideNodeMenu();
  onNodeMenuAction(button.dataset.action, id);
});
cy.on('cxttap', 'node', ev => {
  if (pendingClick) { clearTimeout(pendingClick.timer); pendingClick = null; }
  if (ev.originalEvent) ev.originalEvent.preventDefault();
  showNodeMenu(ev.target.id(), ev.renderedPosition);
});
cy.on('cxttap', ev => {
  if (ev.target !== cy) return;
  if (pendingClick) { clearTimeout(pendingClick.timer); pendingClick = null; }
  if (ev.originalEvent) ev.originalEvent.preventDefault();
  showGraphMenu(ev.renderedPosition);
});
cy.on('dragpan scrollzoom pinchzoom', hideNodeMenu);
document.getElementById('graph').addEventListener('contextmenu', ev => ev.preventDefault());
document.addEventListener('pointerdown', ev => { if (!nodeMenu.contains(ev.target)) hideNodeMenu(); });
document.addEventListener('keydown', ev => { if (ev.key === 'Escape') hideNodeMenu(); });

let activeType = null;

// Reflect the active type (if any) onto the legend chips and the nav tree.
function paintTypeState() {
  document.querySelectorAll('#legend .legend-item').forEach(el =>
    el.classList.toggle('active', el.dataset.type === activeType));
  document.querySelectorAll('#nav a[data-id]').forEach(a =>
    a.classList.toggle('typematch', !!activeType && byId[a.dataset.id].type === activeType));
}

function highlight(id) {
  const node = cy.getElementById(id);
  activeType = null;
  cy.elements().addClass('faded');
  cy.nodes().removeClass('sel');
  const near = node.closedNeighborhood();
  near.removeClass('faded');
  cy.edges().removeClass('near');
  node.connectedEdges().addClass('near');
  node.addClass('sel');
  paintTypeState();
  caption.textContent = node.data('label') + ' — ' + node.connectedEdges().length + ' links';
}

// A merged overview represents its own type and the types of its hidden children.
function nodeMatchesType(id, type) {
  if (isDirId(id)) return dirs[dirOf(id)].types.has(type);
  const path = directoryForNode(id);
  return byId[id].type === type || !!path && dirs[path].types.has(type);
}

// Highlight every concept of one type across the graph and the nav tree.
function highlightType(type) {
  activeType = type;
  cy.nodes().removeClass('sel');
  cy.elements().addClass('faded');
  const matching = cy.nodes().filter(n => nodeMatchesType(n.id(), type));
  matching.removeClass('faded');
  paintTypeState();
  caption.textContent = type + ' — ' + matching.length + ' concepts';
}

function graphCounts() {
  let concepts = 0, directories = 0;
  cy.nodes().forEach(node => {
    const id = node.id();
    if (!isDirId(id)) concepts++;
    const path = directoryForNode(id);
    if (path && (isDirId(id) || !expanded.has(path))) directories++;
  });
  return { concepts, directories };
}

function clearHighlight() {
  activeType = null;
  cy.edges().removeClass('near');
  cy.elements().removeClass('faded');
  cy.nodes().removeClass('sel');
  paintTypeState();
  const counts = graphCounts();
  caption.textContent = counts.concepts + ' concepts · ' + counts.directories + ' collapsed directories · ' +
    cy.edges().length + ' links  (double-click: expand / collapse)';
}

function relayout() {
  // Only resize/refit on view changes — never re-run the force layout, which
  // would reshuffle node positions and make the graph jump on every click.
  requestAnimationFrame(() => { cy.resize(); cy.fit(undefined, 30); });
}

let pendingFocusFrame = null;
function stopViewportMotion() {
  if (pendingFocusFrame !== null) {
    cancelAnimationFrame(pendingFocusFrame);
    pendingFocusFrame = null;
  }
  cy.stop(true);
}

function focusOn(id) {
  // Zoom and recenter to the selected node plus its immediate links, instead of
  // refitting the entire graph. Only the newest requested viewport move should run.
  stopViewportMotion();
  const node = cy.getElementById(id);
  pendingFocusFrame = requestAnimationFrame(() => {
    pendingFocusFrame = null;
    cy.resize();
    if (node.nonempty()) cy.animate({ fit: { eles: node.closedNeighborhood(), padding: 60 } }, { duration: 300 });
    else cy.fit(undefined, 30);
  });
}

/* ---------- reader ---------- */
// Wire a rendered markdown container: in-bundle links navigate the graph,
// external links open in a new tab.
function wireDocLinks(container) {
  container.querySelectorAll('a[href^="#node:"]').forEach(a => {
    const target = decodeURIComponent(a.getAttribute('href').slice(6));
    a.classList.add('xref');
    a.addEventListener('click', ev => { ev.preventDefault(); openConcept(target); });
  });
  container.querySelectorAll('a[href^="http"]').forEach(a => { a.target = '_blank'; a.rel = 'noopener'; });
  container.querySelectorAll('a[href]').forEach(a => {
    const path = a.getAttribute('href').split(/[?#]/, 1)[0];
    if (DATA.files.some(file => file.href === path)) { a.target = '_blank'; a.rel = 'noopener'; }
  });
  container.querySelectorAll('a[href^="#src-"]').forEach(a => {
    a.addEventListener('click', ev => {
      ev.preventDefault();
      const li = doc.querySelector('#' + cssEscape(a.getAttribute('href').slice(1)));
      if (!li) return;
      li.scrollIntoView({ behavior: 'smooth', block: 'center' });
      li.classList.add('flash');
      setTimeout(() => li.classList.remove('flash'), 1600);
    });
  });
}

function inboundConcepts(id) {
  const sources = new Set(DATA.edges.filter(edge => edge.target === id).map(edge => edge.source));
  return [...sources].filter(source => source !== id && byId[source]).map(source => byId[source])
    .sort((a, b) => a.title.localeCompare(b.title) || a.id.localeCompare(b.id));
}

function updateBacklinks(id) {
  if (!id || !byId[id]) {
    backlinks.innerHTML = '<h2>Backlinks</h2><p>Select a concept to see which other concepts reference it.</p>';
    return;
  }
  const inbound = inboundConcepts(id);
  const groups = new Map();
  inbound.forEach(n => {
    if (!groups.has(n.type)) groups.set(n.type, []);
    groups.get(n.type).push(n);
  });
  backlinks.innerHTML = `<h2>Backlinks · ${inbound.length}</h2>` + (inbound.length
    ? [...groups.entries()].sort(([a], [b]) => a.localeCompare(b)).map(([type, members]) =>
        `<section class="backlink-group"><h3><span class="badge" style="background:${members[0].color}">` +
        `${escapeHtml(type)}</span><span class="group-count">${members.length}</span></h3><ul>` +
        members.map(n => `<li><a href="#${encodeURIComponent(n.id)}" data-backlink="${escapeAttr(n.id)}">` +
          `${escapeHtml(n.title)}</a></li>`).join('') + '</ul></section>').join('')
    : '<p>No other concepts link to this one.</p>');
  backlinks.querySelectorAll('a[data-backlink]').forEach(a => a.addEventListener('click', ev => {
    ev.preventDefault();
    openConcept(a.dataset.backlink);
  }));
}

const navigationEntries = [];
let navigationIndex = -1;
const navigationStorageKey = 'okf-navigation:' + location.pathname;
function persistNavigation() {
  try { sessionStorage.setItem(navigationStorageKey, JSON.stringify(navigationEntries)); } catch (_) { /* file URL storage may be disabled */ }
}
try {
  const saved = JSON.parse(sessionStorage.getItem(navigationStorageKey));
  const state = history.state;
  if (Array.isArray(saved) && Number.isInteger(state?.okfIndex) &&
      saved[state.okfIndex] === state.okfId) {
    navigationEntries.push(...saved);
    navigationIndex = state.okfIndex;
  }
} catch (_) { /* history still works within this page load */ }
function updateHistoryButtons() {
  backButton.disabled = navigationIndex <= 0;
  forwardButton.disabled = navigationIndex < 0 || navigationIndex >= navigationEntries.length - 1;
}
function recordNavigation(id) {
  if (navigationIndex >= 0 && navigationEntries[navigationIndex] === id) {
    updateHistoryButtons();
    return;
  }
  const url = id ? '#' + encodeURIComponent(id) : location.pathname;
  if (navigationIndex < 0) {
    navigationEntries.push(id);
    navigationIndex = 0;
    history.replaceState({ okfIndex: 0, okfId: id }, '', url);
  } else {
    navigationEntries.splice(navigationIndex + 1);
    navigationEntries.push(id);
    navigationIndex++;
    history.pushState({ okfIndex: navigationIndex, okfId: id }, '', url);
  }
  persistNavigation();
  updateHistoryButtons();
}
backButton.addEventListener('click', () => history.back());
forwardButton.addEventListener('click', () => history.forward());
window.addEventListener('popstate', ev => {
  const index = ev.state && ev.state.okfIndex;
  if (!Number.isInteger(index) || index < 0) return;
  const id = Object.prototype.hasOwnProperty.call(ev.state, 'okfId')
    ? ev.state.okfId : navigationEntries[index];
  if (id === undefined) return;
  navigationEntries[index] = id;
  navigationIndex = index;
  persistNavigation();
  updateHistoryButtons();
  if (id === 'index') openIndex();
  else if (id === 'log') openLog();
  else if (byId[id]) openConcept(id);
  else if (isDirId(id) && dirs[dirOf(id)]) openDir(dirOf(id));
  else showGraphOnly();
});

/* ---------- OKF v0.2 metadata ---------- */
function lifecycleHtml(n) {
  if (!n.status || n.status === 'stable') return '';
  return `<div class="lifecycle"><span class="pill status-${escapeAttr(n.status)}">${escapeHtml(n.status)}</span></div>`;
}

function propertiesHtml(n) {
  if (!n.properties || !n.properties.length) return '';
  const schema = DATA.typeSchemas[n.type] || {};
  const fields = schema.fields || {};
  const rowHtml = ([key, value]) => {
    const help = fields[key] ? ` title="${escapeAttr(fields[key])}"` : '';
    return `<tr><th${help}>${escapeHtml(key)}</th><td>${marked.parseInline(value)}</td></tr>`;
  };
  const table = rows => rows.length ? `<table class="props">${rows.map(rowHtml).join('')}</table>` : '';
  if (!schema.primaryFields) return table(n.properties);
  const primary = new Set(schema.primaryFields);
  const prominent = n.properties.filter(([key]) => primary.has(key));
  const technical = n.properties.filter(([key]) => !primary.has(key));
  return table(prominent) + (technical.length
    ? `<details class="prop-details"><summary>Technical details (${technical.length})</summary>${table(technical)}</details>`
    : '');
}

function sourcesHtml(n) {
  if (!n.sources || !n.sources.length) return '';
  const items = n.sources.map(src => {
    const label = escapeHtml(src.title || src.resource);
    const link = src.href ? `<a href="${escapeAttr(src.href)}">${label}</a>` : label;
    const extra = [src.author, src.last_modified].filter(Boolean).map(escapeHtml).join(' · ');
    const id = src.id ? ` id="src-${escapeAttr(src.id)}"` : '';
    const tag = src.id ? `<code>${escapeHtml(src.id)}</code> ` : '';
    return `<li${id}>${tag}${link}${extra ? ' — ' + extra : ''}</li>`;
  }).join('');
  return `<div class="sources"><h1>Sources</h1><ul>${items}</ul></div>`;
}

function renderDoc(markdown) {
  doc.innerHTML = marked.parse(markdown);
  wireDocLinks(doc);
  doc.scrollTop = 0;
}

function openConcept(id, attention = true) {
  const n = byId[id];
  if (!n) return;
  if (representative(id) !== id) { revealConcept(id, () => openConcept(id, attention)); return; }
  closeMobilePanels();
  main.classList.remove('graph-only');
  const resourceHtml = n.resource
    ? `<span class="resource">🔗 <a href="${escapeAttr(n.resource)}" title="${escapeAttr(n.resource)}" target="_blank" rel="noopener">${escapeHtml(n.resource)}</a></span>` : '';
  const tagsHtml = (n.tags && n.tags.length)
    ? `<span class="tags-inline">${n.tags.map(t => `<code>${escapeHtml(t)}</code>`).join('')}</span>` : '';
  const summaryHtml = n.description ? `<p class="summary">${marked.parseInline(n.description)}</p>` : '';
  const typeHelp = (DATA.typeSchemas[n.type] || {}).description;
  const typeTitle = typeHelp ? ` title="${escapeAttr(typeHelp)}"` : '';
  doc.innerHTML =
    `<h1>${escapeHtml(n.title)}</h1>` +
    `<div class="meta">` +
      resourceHtml +
      `<span class="meta-right">${tagsHtml}` +
        `<span class="badge" style="background:${n.color}"${typeTitle}>${escapeHtml(n.type)}</span>` +
      `</span>` +
    `</div>` + lifecycleHtml(n) + summaryHtml + propertiesHtml(n);
  wireDocLinks(doc);
  const bodyHtml = document.createElement('div');
  bodyHtml.className = 'prose';
  bodyHtml.innerHTML = marked.parse(n.body) + sourcesHtml(n);
  doc.appendChild(bodyHtml);
  wireDocLinks(bodyHtml);
  doc.scrollTop = 0;
  setActiveNav(id, attention);
  recordNavigation(id);
  updateBacklinks(id);
  highlight(id);
  if (graphWrap.dataset.view === 'graph') focusOn(id);
}

function openIndex() {
  // The bundle-root index.md is the landing page: catalog in the reader, every directory collapsed.
  closeMobilePanels();
  main.classList.remove('graph-only');
  const body = document.createElement('div');
  body.className = 'prose';
  body.innerHTML = DATA.index ? marked.parse(DATA.index) : '';
  doc.innerHTML = '';
  doc.appendChild(body);
  wireDocLinks(body);
  doc.scrollTop = 0;
  setActiveNav('index');
  recordNavigation('index');
  updateBacklinks(null);
  collapseAllDirs(() => { clearHighlight(); relayout(); });
}

function openDir(path, attention = true) {
  // Reader view for a directory: its concepts and subdirectories; the graph keeps its state.
  const d = dirs[path];
  if (!d) return;
  if (d.overviewId) { openConcept(d.overviewId, attention); return; }
  closeMobilePanels();
  main.classList.remove('graph-only');
  const direct = d.concepts.filter(id => parentDirOf(id) === path).map(id => byId[id])
    .sort((a, b) => a.title.localeCompare(b.title));
  const files = DATA.files.filter(file => parentDirOf(file.id) === path)
    .sort((a, b) => a.title.localeCompare(b.title));
  const subdirs = Object.values(dirs).filter(x => x.parent === path).sort((a, b) => a.path.localeCompare(b.path));
  const state = expanded.has(path) ? 'expanded — double-click a concept node to collapse' : 'collapsed — double-click its node to expand';
  doc.innerHTML = `<h1>${escapeHtml(dirLabel(path))}</h1><p class="summary">Directory <code>${escapeHtml(path)}/</code> · ${state}</p>` +
    (subdirs.length ? '<h2>Directories</h2><ul class="dirlist">' + subdirs.map(x =>
      `<li><a href="#" data-dir="${escapeAttr(x.path)}">📁 ${escapeHtml(dirLabel(x.path))}</a></li>`).join('') + '</ul>' : '') +
    (direct.length ? '<h2>Concepts</h2><ul class="dirlist">' + direct.map(n =>
      `<li><span class="dot" style="background:${n.color}"></span><a href="#node:${escapeAttr(n.id)}">${escapeHtml(n.title)}</a>` +
      (n.description ? ` — <span style="color:var(--muted)">${marked.parseInline(n.description)}</span>` : '') + '</li>').join('') + '</ul>' : '') +
    (files.length ? '<h2>Files</h2><ul class="dirlist">' + files.map(file =>
      `<li><a href="${escapeAttr(file.href)}" target="_blank" rel="noopener">${escapeHtml(file.title)}</a> <small>${escapeHtml(file.kind)}</small></li>`).join('') + '</ul>' : '');
  wireDocLinks(doc);
  doc.querySelectorAll('a[data-dir]').forEach(a => a.addEventListener('click', ev => {
    ev.preventDefault();
    const sub = a.dataset.dir;
    expandDir(path, () => openDir(sub));
  }));
  doc.scrollTop = 0;
  setActiveNav(DIR_PREFIX + path, attention);
  recordNavigation(DIR_PREFIX + path);
  updateBacklinks(null);
  const node = cy.getElementById(DIR_PREFIX + path);
  if (node.nonempty()) { highlight(node.id()); if (graphWrap.dataset.view === 'graph') focusOn(node.id()); return; }
  // Expanded: frame what the directory now shows (its concepts and collapsed subdirectories).
  clearHighlight();
  const inside = cy.nodes().filter(x => (isDirId(x.id()) ? dirOf(x.id()) : x.id()).startsWith(path + '/'));
  requestAnimationFrame(() => {
    cy.resize();
    if (inside.nonempty()) cy.animate({ fit: { eles: inside, padding: 50 } }, { duration: 300 });
  });
}

function openEdgeLink(edge) {
  // Open the edge's source concept and scroll to / flash the link that produced
  // this edge (a body link, or the Properties row for a typed frontmatter edge).
  // Merged edges touching a directory node open that directory's overview instead.
  const source = edge.data('source'), target = edge.data('target');
  if (isDirId(source)) { openDir(dirOf(source)); return; }
  openConcept(source);
  const targets = (edge.data('links') || []).map(l => l.target);
  const link = [...doc.querySelectorAll('a[href^="#node:"]')].find(a => {
    const id = decodeURIComponent(a.getAttribute('href').slice(6));
    return targets.includes(id) || id === target;
  });
  if (link) {
    link.scrollIntoView({ behavior: 'smooth', block: 'center' });
    link.classList.add('flash');
    setTimeout(() => link.classList.remove('flash'), 1600);
  }
}

function openLog() {
  if (!DATA.log) return;
  closeMobilePanels();
  main.classList.remove('graph-only');
  renderDoc(DATA.log);
  setActiveNav('log');
  clearHighlight();
  recordNavigation('log');
  updateBacklinks(null);
  relayout();
}

function showGraphOnly() {
  main.classList.add('graph-only');
  graphWrap.dataset.view = 'graph';
  document.querySelectorAll('.pane-switch button').forEach(tab =>
    tab.setAttribute('aria-selected', String(tab.dataset.view === 'graph')));
  setActiveNav(null);
  clearHighlight();
  recordNavigation(null);
  updateBacklinks(null);
  relayout();
}

/* ---------- sidebar tree ---------- */
function buildTree(nodes, assets = DATA.files) {
  const root = { dirs: {}, files: [], assets: [] };
  nodes.forEach(n => {
    const parts = n.id.split('/');
    let cur = root;
    for (let i = 0; i < parts.length - 1; i++) {
      cur.dirs[parts[i]] = cur.dirs[parts[i]] || { dirs: {}, files: [], assets: [] };
      cur = cur.dirs[parts[i]];
    }
    const path = n.id.slice(0, -3);
    if (dirs[path]) {
      const name = parts[parts.length - 1].slice(0, -3);
      cur.dirs[name] = cur.dirs[name] || { dirs: {}, files: [], assets: [] };
      cur.dirs[name].overview = n;
    } else cur.files.push(n);
  });
  assets.forEach(file => {
    const parts = file.id.split('/');
    let cur = root;
    for (let i = 0; i < parts.length - 1; i++) {
      cur.dirs[parts[i]] = cur.dirs[parts[i]] || { dirs: {}, files: [], assets: [] };
      cur = cur.dirs[parts[i]];
    }
    cur.assets.push(file);
  });
  return root;
}

// Sidebar links use the graph's click window so a double-click can cancel navigation.
let pendingNavClick = null;
function onNavConceptClick(ev, id) {
  ev.preventDefault();
  if (pendingNavClick) {
    clearTimeout(pendingNavClick.timer);
    if (pendingNavClick.id !== id) pendingNavClick.run();
  }
  const directory = directoryForNode(id);
  const toggleSelected = !!directory && ev.currentTarget.classList.contains('active');
  const run = () => {
    if (toggleSelected) {
      if (expanded.has(directory)) collapseDir(directory, () => openDir(directory, false));
      else expandDir(directory, () => openDir(directory, false));
    } else if (directory) expandDir(directory, () => openConcept(id, false));
    else openConcept(id, false);
  };
  pendingNavClick = { id, run, timer: setTimeout(() => { pendingNavClick = null; run(); }, DOUBLE_CLICK_MS) };
}

function onNavConceptDoubleClick(ev, id) {
  ev.preventDefault();
  ev.stopPropagation();
  if (pendingNavClick) {
    clearTimeout(pendingNavClick.timer);
    if (pendingNavClick.id !== id) pendingNavClick.run();
    pendingNavClick = null;
  }
  const directory = directoryForNode(id);
  if (directory) toggleDirectory(directory, false);
  else onNodeDoubleClick(id, false);
}

function renderTree(tree, prefix = '') {
  const ul = document.createElement('ul');
  // Standalone concepts first; same-named overviews live in their directory entry.
  tree.files.sort((a, b) => a.title.localeCompare(b.title)).forEach(n => {
    const li = document.createElement('li');
    const a = document.createElement('a');
    a.href = '#' + encodeURIComponent(n.id);
    a.dataset.id = n.id;
    if (n.status && n.status !== 'stable') a.classList.add(n.status);
    a.innerHTML = `<span class="dot" style="background:${n.color}"></span><span>${escapeHtml(n.title)}</span>`;
    a.addEventListener('click', ev => onNavConceptClick(ev, n.id));
    a.addEventListener('dblclick', ev => onNavConceptDoubleClick(ev, n.id));
    li.appendChild(a);
    ul.appendChild(li);
  });
  tree.assets.sort((a, b) => a.title.localeCompare(b.title)).forEach(file => {
    const li = document.createElement('li');
    const a = document.createElement('a');
    a.className = 'asset-link';
    a.dataset.fileId = file.id;
    a.href = file.href;
    a.target = '_blank';
    a.rel = 'noopener';
    a.innerHTML = `<span>📄</span><span>${escapeHtml(file.title)}</span><span class="file-kind">${escapeHtml(file.kind)}</span>`;
    li.appendChild(a);
    ul.appendChild(li);
  });
  // Underscore-prefixed directories (e.g. _types) hold meta concepts: list them last.
  Object.keys(tree.dirs).sort((a, b) => (a[0] === '_') - (b[0] === '_') || a.localeCompare(b)).forEach(name => {
    const path = prefix ? prefix + '/' + name : name;
    const li = document.createElement('li');
    li.className = 'dir collapsed';
    li.dataset.dir = path;
    const label = document.createElement('div');
    label.className = 'label';
    const toggle = () => {
      if (expanded.has(path)) collapseDir(path, () => openDir(path, false)); else expandDir(path, () => openDir(path, false));
    };
    if (tree.dirs[name].overview) {
      const overview = tree.dirs[name].overview;
      const caret = document.createElement('button');
      caret.className = 'caret-toggle';
      caret.type = 'button';
      caret.setAttribute('aria-label', 'Expand or collapse ' + overview.title);
      caret.setAttribute('aria-expanded', 'false');
      caret.textContent = '▸';
      caret.addEventListener('click', ev => { ev.stopPropagation(); if (ev.detail < 2) toggle(); });
      caret.addEventListener('dblclick', ev => { ev.preventDefault(); ev.stopPropagation(); });
      const link = document.createElement('a');
      link.className = 'overview-link';
      link.href = '#' + encodeURIComponent(overview.id);
      link.dataset.id = overview.id;
      if (overview.status && overview.status !== 'stable') link.classList.add(overview.status);
      link.innerHTML = `<span class="dot" style="background:${overview.color}"></span><span>${escapeHtml(overview.title)}</span>`;
      link.addEventListener('click', ev => { ev.stopPropagation(); onNavConceptClick(ev, overview.id); });
      const count = document.createElement('span');
      count.className = 'count';
      count.textContent = dirs[path].concepts.length + dirs[path].files;
      label.appendChild(caret);
      label.appendChild(link);
      label.appendChild(count);
      label.addEventListener('click', ev => onNavConceptClick(ev, overview.id));
      label.addEventListener('dblclick', ev => onNavConceptDoubleClick(ev, overview.id));
    } else {
      label.title = 'Click to expand or collapse (also in the graph)';
      label.innerHTML = `<span class="caret">▸</span><span>${escapeHtml(dirLabel(path))}</span>` +
        `<span class="count">${dirs[path].concepts.length + dirs[path].files}</span>`;
      label.addEventListener('click', toggle);
    }
    li.appendChild(label);
    li.appendChild(renderTree(tree.dirs[name], path));
    ul.appendChild(li);
  });
  return ul;
}

// Reflect `expanded` onto the sidebar tree.
function paintTreeState() {
  document.querySelectorAll('#nav li.dir').forEach(li => {
    const open = expanded.has(li.dataset.dir);
    li.classList.toggle('collapsed', !open);
    const caret = li.firstElementChild.querySelector('.caret-toggle');
    if (caret) caret.setAttribute('aria-expanded', String(open));
  });
}

function setActiveNav(id, attention = true) {
  document.querySelectorAll('#nav a, #loglink a, #nav .dir > .label').forEach(a => a.classList.remove('active'));
  document.querySelectorAll('#nav .nav-attention').forEach(row => row.classList.remove('nav-attention'));
  const reveal = row => {
    row.scrollIntoView({block:'nearest'});
    if (attention) {
      void row.offsetWidth; // restart the pulse when the same entry is selected again
      row.classList.add('nav-attention');
    }
  };
  if (id && isDirId(id)) {
    const li = document.querySelector(`#nav li.dir[data-dir="${cssEscape(dirOf(id))}"]`);
    if (li) {
      const label = li.firstElementChild;
      label.classList.add('active');
      reveal(label);
    }
    return;
  }
  if (id === 'log') { const l = document.querySelector('#loglink a'); l && l.classList.add('active'); return; }
  if (id === 'index') { const h = document.querySelector('#nav a.homelink'); h && h.classList.add('active'); return; }
  if (!id) return;
  const a = document.querySelector(`#nav a[data-id="${cssEscape(id)}"]`);
  if (a) {
    a.classList.add('active');
    const row = a.classList.contains('overview-link') ? a.parentElement : a;
    if (row !== a) row.classList.add('active');
    reveal(row);
  }
}

const nav = document.getElementById('nav');
if (DATA.index) {
  const home = document.createElement('a');
  home.href = '#index';
  home.className = 'homelink';
  home.innerHTML = '🏠 <span>Index</span>';
  home.addEventListener('click', ev => { ev.preventDefault(); openIndex(); });
  nav.appendChild(home);
}
nav.appendChild(renderTree(buildTree(DATA.nodes, DATA.files)));
if (DATA.log) {
  const link = document.createElement('a');
  link.href = '#log';
  link.innerHTML = '📓 <span>Change log</span>';
  link.addEventListener('click', ev => { ev.preventDefault(); openLog(); });
  document.getElementById('loglink').appendChild(link);
}

/* ---------- search ---------- */
function searchNavMatch(id, hits) {
  if (hits.includes(id)) return true;
  const path = directoryForNode(id);
  return !!path && hits.some(hit => hit.startsWith(path + '/'));
}

document.getElementById('search').addEventListener('input', ev => {
  if (window.matchMedia('(max-width: 860px)').matches) {
    closeMobilePanels();
    document.body.classList.add('nav-open');
    navToggle.setAttribute('aria-expanded', 'true');
  }
  const q = ev.target.value.trim().toLowerCase();
  const hits = [];
  DATA.nodes.forEach(n => {
    const props = (n.properties || []).map(p => p.join(' ')).join(' ');
    const hay = (n.title + ' ' + n.description + ' ' + n.type + ' ' + n.tags.join(' ') + ' ' + n.status + ' ' + props).toLowerCase();
    const hit = !q || hay.includes(q);
    if (q && hit) hits.push(n.id);
  });
  DATA.nodes.forEach(n => {
    const navA = document.querySelector(`#nav a[data-id="${cssEscape(n.id)}"]`);
    if (navA) navA.classList.toggle('hidden', !!q && !searchNavMatch(n.id, hits));
  });
  const fileHits = DATA.files.filter(file => (file.title + ' ' + file.id + ' ' + file.kind).toLowerCase().includes(q));
  DATA.files.forEach(file => {
    const navA = document.querySelector(`#nav a[data-file-id="${cssEscape(file.id)}"]`);
    if (navA) navA.classList.toggle('hidden', !!q && !fileHits.includes(file));
  });
  clearTimeout(searchTimer);
  if (q.length < 2) return;
  // Open the directories holding matches (tree and graph together), then fade the rest.
  searchTimer = setTimeout(() => {
    setExpanded([...new Set([...hits, ...fileHits.map(file => file.id)].flatMap(id => ancestorsOf(id)))], true, () => {
      cy.nodes().forEach(node => node.toggleClass('faded', !hits.includes(node.id())));
      cy.edges().addClass('faded');
      caption.textContent = (hits.length + fileHits.length) + ' matches for “' + q + '”';
    });
  }, 300);
});
let searchTimer = null;

/* ---------- legend ---------- */
function buildLegend() {
  const legend = document.getElementById('legend');
  const relayoutButton = document.createElement('button');
  relayoutButton.className = 'relayout';
  relayoutButton.title = 'Lay out the whole visible graph again';
  relayoutButton.textContent = '↻ Re-layout';
  relayoutButton.addEventListener('click', () => runLayout(() => clearHighlight()));
  const title = document.createElement('span');
  title.className = 'legend-title';
  title.textContent = 'Types';
  legend.appendChild(title);
  DATA.types.forEach(t => {
    const item = document.createElement('button');
    item.className = 'legend-item';
    item.dataset.type = t.name;
    item.innerHTML = `<span class="sw" style="background:${t.color}"></span>${escapeHtml(t.name)}`;
    item.addEventListener('click', () => {
      if (activeType === t.name) clearHighlight(); else highlightType(t.name);
    });
    legend.appendChild(item);
  });
  legend.appendChild(relayoutButton);
}

/* ---------- helpers ---------- */
function escapeHtml(s) { return String(s).replace(/[&<>]/g, c => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;' }[c])); }
function escapeAttr(s) { return escapeHtml(s).replace(/"/g, '&quot;'); }
function cssEscape(s) { return (window.CSS && CSS.escape) ? CSS.escape(s) : s.replace(/["\\]/g, '\\$&'); }

/* ---------- initial state ---------- */
buildLegend();
syncGraph(() => {
  clearHighlight();
  const start = decodeURIComponent(location.hash.slice(1));
  if (start === 'log') openLog();
  else if (byId[start]) openConcept(start);
  else if (isDirId(start) && dirs[dirOf(start)]) expandDir(dirOf(start), () => openDir(dirOf(start)));
  else if (DATA.index) openIndex();
  else showGraphOnly();
});
</script>
</body>
</html>
"""


if __name__ == "__main__":
    raise SystemExit(main())

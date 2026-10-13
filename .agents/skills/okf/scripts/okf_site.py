"""Render an OKF bundle as a single self-contained HTML page.

Usage:
    python okf_site.py [bundle-dir] [-o OUTPUT]

Walks an OKF bundle, parses each concept's frontmatter and body, and writes one
self-contained ``okf-site.html`` with:

* a left navigation sidebar mirroring the bundle's directory structure, with a
  link to the bundle's ``log.md`` pinned at the bottom,
* a main reading area that renders the selected concept's markdown (via
  marked.js) with its in-bundle cross-links wired to navigate the bundle, and
* an interactive knowledge graph below the reader (nodes = concepts colored by
  ``type``, edges = cross-links) built with Cytoscape.js. On first load the graph
  fills the main area; selecting a concept highlights its node and immediate
  links while dimming the rest.

OKF v0.2 metadata is surfaced in the reader: lifecycle ``status`` (draft and
deprecated concepts are also styled in the graph and tree), the trust tier derived
from ``verified`` (unverified / machine-confirmed / human-reviewed), staleness from
``stale_after``, authorship from ``generated`` (falling back to a legacy
``timestamp``), and ``sources`` with ``[^id]`` footnotes linked to them.

Producer-defined frontmatter keys are shown as a Properties table. Any of their
values that is a path to another concept in the bundle (``/people/ana.md``, or a
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
import pathlib
import posixpath
import re
import sys

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
    output_path.write_text(
        _render_html(bundle_root.name, concepts, edges, log_markdown, index_markdown),
        encoding="utf-8",
    )

    print(f"wrote {output_path} ({len(concepts)} concepts, {len(edges)} links)")

    return len(concepts)


def _collect_concepts(
    bundle_root: pathlib.Path, now: datetime.datetime
) -> tuple[list[Concept], list[str]]:
    """Parse every non-reserved ``.md`` file into a Concept, collecting warnings."""
    warnings: list[str] = []
    parsed: list[tuple[str, dict, str]] = []

    for path in sorted(bundle_root.rglob("*.md")):
        if path.name in _RESERVED_FILENAMES:
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
        description=str(frontmatter.get("description") or "").strip(),
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
            normalized["href"] = f"#node:{concept}"
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
            return f"[{titles[target]}](#node:{target})"
        return text

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
        for target in re.findall(r"#node:([^)\s\"']+)", concept.body):
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

    return _rewrite_internal_links(markdown, "index.md", known_ids)


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
            return match.group(0).replace(f"({target})", f"(#node:{resolved})")

        return match.group(0)

    return _LINK_PATTERN.sub(replace, body)


def _resolve_link(target: str, source_dir: str) -> str | None:
    """Resolve a markdown link target to a bundle-relative concept id, or None."""
    link = target.split("#", 1)[0].split("?", 1)[0]
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
        "types": [
            {"name": concept_type, "color": type_colors[concept_type]}
            for concept_type in types
        ],
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
  #mobile-actions { display:none; }
  .mobile-toggle { border:1px solid var(--line); border-radius:6px; padding:6px 9px; background:var(--bg); color:var(--ink); font:inherit; font-size:12px; cursor:pointer; }
  .mobile-toggle[aria-expanded="true"] { background:var(--active); border-color:var(--accent); }
  #search { margin-left:auto; flex:0 0 260px; padding:6px 10px; border-radius:6px; border:1px solid var(--line); background:var(--bg); color:var(--ink); font-size:13px; }
  .below { flex:1 1 auto; display:flex; min-height:0; }

  aside { flex:0 0 264px; display:flex; flex-direction:column; border-right:1px solid var(--line); background:var(--sidebar); min-height:0; }
  #nav { flex:1 1 auto; overflow-y:auto; padding:10px 8px; }
  #nav ul { list-style:none; margin:0; padding:0; }
  #nav .dir > .label { display:flex; align-items:center; gap:5px; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:.04em; color:var(--muted); padding:8px 8px 3px; }
  #nav .dir ul { margin-left:12px; border-left:1px solid var(--line); }
  #nav a { display:flex; align-items:center; gap:8px; padding:5px 8px; border-radius:6px; color:var(--ink); text-decoration:none; font-size:13px; line-height:1.3; }
  #nav a:hover { background:var(--hover); }
  #nav a.active { background:var(--active); font-weight:600; }
  #nav a.typematch:not(.active) { background:#fff3bf; }
  #nav a .dot { width:8px; height:8px; border-radius:50%; flex:0 0 auto; }
  #nav a.hidden { display:none; }
  #nav a.homelink { font-weight:600; margin-bottom:6px; }
  #loglink { flex:0 0 auto; border-top:1px solid var(--line); padding:8px; }
  #loglink a { display:flex; align-items:center; gap:8px; padding:7px 10px; border-radius:6px; color:var(--muted); text-decoration:none; font-size:13px; }
  #loglink a:hover { background:var(--hover); color:var(--ink); }
  #loglink a.active { background:var(--active); color:var(--ink); font-weight:600; }

  main { flex:1 1 auto; display:flex; flex-direction:row; min-width:0; min-height:0; }
  #doc { flex:1 1 auto; overflow-y:auto; padding:26px 36px; min-width:0; }
  #doc > * { max-width:820px; }
  main.graph-only #doc { display:none; }
  #graph-wrap { flex:0 0 42%; border-left:1px solid var(--line); display:flex; flex-direction:column; min-height:0; min-width:0; background:var(--bg); }
  main.graph-only #graph-wrap { flex:1 1 auto; border-left:none; }
  #legend { flex:0 0 auto; display:flex; flex-wrap:wrap; align-items:center; gap:2px 6px; padding:8px 12px; border-bottom:1px solid var(--line); }
  #legend .legend-title { font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:.04em; color:var(--muted); margin-right:4px; }
  #legend .legend-item { display:inline-flex; align-items:center; gap:5px; cursor:pointer; border:0; background:none; font:inherit; font-size:11.5px; color:var(--muted); padding:2px 6px; border-radius:5px; }
  #legend .legend-item:hover { background:var(--hover); color:var(--ink); }
  #legend .legend-item.active { background:var(--active); color:var(--ink); font-weight:600; }
  #legend .sw { width:10px; height:10px; border-radius:3px; flex:0 0 auto; }
  #graph-container { flex:1 1 auto; position:relative; min-height:0; }
  #graph { position:absolute; inset:0; }
  #graph-caption { position:absolute; top:8px; left:12px; font-size:11px; color:var(--muted); pointer-events:none; }

  #doc h1 { font-size:24px; margin:0 0 2px; }
  #doc h2 { font-size:17px; margin:1.5em 0 .4em; padding-bottom:5px; border-bottom:1px solid var(--line); }
  #doc .prose h1 { font-size:17px; font-weight:600; margin:1.6em 0 .4em; padding-bottom:5px; border-bottom:1px solid var(--line); }
  #doc .meta { display:flex; align-items:center; gap:10px; margin:8px 0 16px; font-size:12.5px; }
  #doc .badge { flex:0 0 auto; display:inline-block; padding:2px 9px; border-radius:11px; font-size:11px; color:#fff; font-weight:600; }
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
  #doc code { font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:85%; background:var(--code); padding:.15em .4em; border-radius:5px; }
  #doc pre { background:var(--code); padding:13px; border-radius:8px; overflow-x:auto; }
  #doc pre code { background:none; padding:0; }
  #doc .lifecycle { display:flex; flex-wrap:wrap; gap:6px; margin:-6px 0 12px; }
  #doc .pill { display:inline-block; padding:1px 8px; border-radius:10px; font-size:11px; font-weight:600; border:1px solid var(--line); color:var(--muted); background:var(--bg); }
  #doc .pill.status-draft { color:#9a6700; border-color:#d4a72c; background:#fff8c5; }
  #doc .pill.status-deprecated { color:#82071e; border-color:#ff8182; background:#ffebe9; }
  #doc .pill.trust-unverified { color:var(--muted); }
  #doc .pill.trust-machine-confirmed { color:#0550ae; border-color:#80ccff; background:#ddf4ff; }
  #doc .pill.trust-human-reviewed { color:#116329; border-color:#4ac26b; background:#dafbe1; }
  #doc .pill.stale { color:#82071e; border-color:#ff8182; background:#ffebe9; }
  #doc .provenance { color:var(--muted); font-size:12px; margin:0 0 14px; }
  #doc table.props { margin:4px 0 18px; }
  #doc table.props th { white-space:nowrap; font-weight:600; width:1%; }
  #doc .sources h1 { font-size:17px; font-weight:600; margin:1.6em 0 .4em; padding-bottom:5px; border-bottom:1px solid var(--line); }
  #doc .sources li { margin:3px 0; }
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
    <div id="mobile-actions">
      <button id="nav-toggle" class="mobile-toggle" type="button" aria-controls="nav" aria-expanded="false">Contents</button>
      <button id="graph-toggle" class="mobile-toggle" type="button" aria-controls="graph-wrap" aria-expanded="false">Graph</button>
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
      <div id="graph-wrap">
        <div id="legend"></div>
        <div id="graph-container">
          <div id="graph"></div>
          <div id="graph-caption"></div>
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
const navToggle = document.getElementById('nav-toggle');
const graphToggle = document.getElementById('graph-toggle');

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

/* ---------- graph ---------- */
const cy = cytoscape({
  container: document.getElementById('graph'),
  elements: [
    ...DATA.nodes.map(n => ({ data: { id: n.id, label: n.title, color: n.color }, classes: 'status-' + n.status })),
    ...DATA.edges.map((e, i) => ({ data: { id: 'e' + i, source: e.source, target: e.target, label: e.label || '' },
                                   classes: e.label ? 'typed' : '' })),
  ],
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
    { selector: 'node.sel', style: { 'border-color': '#0969da', 'border-width': 3, 'font-size': '10px', 'font-weight': 'bold', 'width': 20, 'height': 20 } },
    { selector: '.faded', style: { 'opacity': .12 } },
    { selector: 'node.hidden', style: { 'display': 'none' } },
  ],
  wheelSensitivity: 0.2,
  maxZoom: 2.5,   // small bundles would otherwise zoom a single node to fill the pane
});

function graphLayout() {
  return { name: 'cose', animate: false, nodeDimensionsIncludeLabels: true,
           idealEdgeLength: 150, nodeRepulsion: 22000, nodeOverlap: 60,
           gravity: 0.2, componentSpacing: 160, numIter: 1500, padding: 40 };
}

// Run the force layout, then a deterministic pass that pushes any still-
// overlapping nodes apart using their label-inclusive bounding boxes, so labels
// never sit on top of each other regardless of the force layout's result.
function runLayout() {
  const layout = cy.layout(graphLayout());
  layout.one('layoutstop', () => requestAnimationFrame(() => separateOverlaps()));
  layout.run();
}

function separateOverlaps(iterations = 80, pad = 10) {
  const nodes = cy.nodes();
  for (let it = 0; it < iterations; it++) {
    let moved = false;
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const a = nodes[i], b = nodes[j];
        const ba = a.boundingBox({ includeLabels: true });
        const bb = b.boundingBox({ includeLabels: true });
        const overlapX = Math.min(ba.x2, bb.x2) - Math.max(ba.x1, bb.x1) + pad;
        const overlapY = Math.min(ba.y2, bb.y2) - Math.max(ba.y1, bb.y1) + pad;
        if (overlapX > 0 && overlapY > 0) {
          let dx = (ba.x1 + ba.x2) / 2 - (bb.x1 + bb.x2) / 2;
          let dy = (ba.y1 + ba.y2) / 2 - (bb.y1 + bb.y2) / 2;
          const dist = Math.hypot(dx, dy) || 0.01;
          const push = Math.min(overlapX, overlapY) / 2;
          dx /= dist; dy /= dist;
          a.position({ x: a.position('x') + dx * push, y: a.position('y') + dy * push });
          b.position({ x: b.position('x') - dx * push, y: b.position('y') - dy * push });
          moved = true;
        }
      }
    }
    if (!moved) break;
  }
  cy.fit(undefined, 30);
}

cy.on('tap', 'node', ev => {
  // Clicking the already-selected node toggles the selection off.
  if (ev.target.hasClass('sel')) clearHighlight(); else openConcept(ev.target.id());
});
cy.on('tap', 'edge', ev => openEdgeLink(ev.target));           // open the source doc at the link that made this edge
cy.on('tap', ev => { if (ev.target === cy) clearHighlight(); });    // click empty space = deselect node, keep the doc open
document.getElementById('graph').addEventListener('dblclick', () => {  // double-click anywhere = reset zoom to fit all
  cy.animate({ fit: { eles: cy.elements(), padding: 30 } }, { duration: 300 });
});

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

// Highlight every concept of one type across the graph and the nav tree.
function highlightType(type) {
  activeType = type;
  cy.nodes().removeClass('sel');
  cy.elements().addClass('faded');
  const matching = cy.nodes().filter(n => byId[n.id()].type === type);
  matching.removeClass('faded');
  paintTypeState();
  caption.textContent = type + ' — ' + matching.length + ' concepts';
}

function clearHighlight() {
  activeType = null;
  cy.edges().removeClass('near');
  cy.elements().removeClass('faded');
  cy.nodes().removeClass('sel');
  paintTypeState();
  caption.textContent = cy.nodes().length + ' concepts · ' + cy.edges().length + ' links';
}

function relayout() {
  // Only resize/refit on view changes — never re-run the force layout, which
  // would reshuffle node positions and make the graph jump on every click.
  requestAnimationFrame(() => { cy.resize(); cy.fit(undefined, 30); });
}

function focusOn(id) {
  // Zoom and recenter to the selected node plus its immediate links, instead of
  // refitting the entire graph.
  const node = cy.getElementById(id);
  requestAnimationFrame(() => {
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

/* ---------- OKF v0.2 metadata ---------- */
function lifecycleHtml(n) {
  const pills = [];
  if (n.status && n.status !== 'stable') pills.push(`<span class="pill status-${escapeAttr(n.status)}">${escapeHtml(n.status)}</span>`);
  pills.push(`<span class="pill trust-${escapeAttr(n.trust)}" title="Trust tier derived from 'verified'">${escapeHtml(n.trust)}</span>`);
  if (n.stale) pills.push(`<span class="pill stale" title="stale_after has passed">stale since ${escapeHtml(n.stale_after)}</span>`);
  else if (n.stale_after) pills.push(`<span class="pill" title="stale_after">fresh until ${escapeHtml(n.stale_after)}</span>`);
  return `<div class="lifecycle">${pills.join('')}</div>`;
}

function provenanceHtml(n) {
  const parts = [];
  if (n.generated) parts.push('Generated' + (n.generated.by ? ' by ' + escapeHtml(n.generated.by) : '') + (n.generated.at ? ' at ' + escapeHtml(n.generated.at) : ''));
  if (n.verified && n.verified.length) parts.push('Verified by ' + n.verified.map(v => escapeHtml(v.by) + (v.at ? ' (' + escapeHtml(v.at) + ')' : '')).join(', '));
  return parts.length ? `<p class="provenance">${parts.join(' · ')}</p>` : '';
}

function propertiesHtml(n) {
  if (!n.properties || !n.properties.length) return '';
  const rows = n.properties.map(([key, value]) =>
    `<tr><th>${escapeHtml(key)}</th><td>${marked.parseInline(value)}</td></tr>`).join('');
  return `<table class="props">${rows}</table>`;
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

function openConcept(id) {
  const n = byId[id];
  if (!n) return;
  closeMobilePanels();
  main.classList.remove('graph-only');
  const resourceHtml = n.resource
    ? `<span class="resource">🔗 <a href="${escapeAttr(n.resource)}" title="${escapeAttr(n.resource)}" target="_blank" rel="noopener">${escapeHtml(n.resource)}</a></span>` : '';
  const tagsHtml = (n.tags && n.tags.length)
    ? `<span class="tags-inline">${n.tags.map(t => `<code>${escapeHtml(t)}</code>`).join('')}</span>` : '';
  const summaryHtml = n.description ? `<p class="summary">${escapeHtml(n.description)}</p>` : '';
  doc.innerHTML =
    `<h1>${escapeHtml(n.title)}</h1>` +
    `<div class="meta">` +
      resourceHtml +
      `<span class="meta-right">${tagsHtml}` +
        `<span class="badge" style="background:${n.color}">${escapeHtml(n.type)}</span>` +
      `</span>` +
    `</div>` + lifecycleHtml(n) + summaryHtml + provenanceHtml(n) + propertiesHtml(n);
  wireDocLinks(doc);
  const bodyHtml = document.createElement('div');
  bodyHtml.className = 'prose';
  bodyHtml.innerHTML = marked.parse(n.body) + sourcesHtml(n);
  doc.appendChild(bodyHtml);
  wireDocLinks(bodyHtml);
  doc.scrollTop = 0;
  setActiveNav(id);
  history.replaceState(null, '', '#' + encodeURIComponent(id));
  highlight(id);
  focusOn(id);
}

function openIndex() {
  // The bundle-root index.md is the landing page: catalog in the reader, whole graph.
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
  clearHighlight();
  history.replaceState(null, '', '#index');
  relayout();
}

function openEdgeLink(edge) {
  // Open the edge's source concept and scroll to / flash the link that produced
  // this edge (a body link, or the Properties row for a typed frontmatter edge).
  const source = edge.data('source'), target = edge.data('target');
  openConcept(source);
  const link = doc.querySelector(`a[href="#node:${target}"]`);
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
  history.replaceState(null, '', '#log');
  relayout();
}

function showGraphOnly() {
  main.classList.add('graph-only');
  setActiveNav(null);
  clearHighlight();
  history.replaceState(null, '', location.pathname);
  relayout();
}

/* ---------- sidebar tree ---------- */
function buildTree(nodes) {
  const root = { dirs: {}, files: [] };
  nodes.forEach(n => {
    const parts = n.id.split('/');
    let cur = root;
    for (let i = 0; i < parts.length - 1; i++) {
      cur.dirs[parts[i]] = cur.dirs[parts[i]] || { dirs: {}, files: [] };
      cur = cur.dirs[parts[i]];
    }
    cur.files.push(n);
  });
  return root;
}

function renderTree(tree) {
  const ul = document.createElement('ul');
  // Concept pages first, then subdirectories (so a directory's own overview sits
  // above its children).
  tree.files.sort((a, b) => a.title.localeCompare(b.title)).forEach(n => {
    const li = document.createElement('li');
    const a = document.createElement('a');
    a.href = '#' + encodeURIComponent(n.id);
    a.dataset.id = n.id;
    if (n.status && n.status !== 'stable') a.classList.add(n.status);
    a.innerHTML = `<span class="dot" style="background:${n.color}"></span><span>${escapeHtml(n.title)}</span>`;
    a.addEventListener('click', ev => { ev.preventDefault(); openConcept(n.id); });
    li.appendChild(a);
    ul.appendChild(li);
  });
  // Underscore-prefixed directories (e.g. _types) hold meta concepts: list them last.
  Object.keys(tree.dirs).sort((a, b) => (a[0] === '_') - (b[0] === '_') || a.localeCompare(b)).forEach(name => {
    const li = document.createElement('li');
    li.className = 'dir';
    const label = document.createElement('div');
    label.className = 'label';
    label.textContent = name.startsWith('_') ? name : name.replace(/[-_]/g, ' ');
    li.appendChild(label);
    li.appendChild(renderTree(tree.dirs[name]));
    ul.appendChild(li);
  });
  return ul;
}

function setActiveNav(id) {
  document.querySelectorAll('#nav a, #loglink a').forEach(a => a.classList.remove('active'));
  if (id === 'log') { const l = document.querySelector('#loglink a'); l && l.classList.add('active'); return; }
  if (id === 'index') { const h = document.querySelector('#nav a.homelink'); h && h.classList.add('active'); return; }
  if (!id) return;
  const a = document.querySelector(`#nav a[data-id="${cssEscape(id)}"]`);
  a && a.classList.add('active');
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
nav.appendChild(renderTree(buildTree(DATA.nodes)));
if (DATA.log) {
  const link = document.createElement('a');
  link.href = '#log';
  link.innerHTML = '📓 <span>Change log</span>';
  link.addEventListener('click', ev => { ev.preventDefault(); openLog(); });
  document.getElementById('loglink').appendChild(link);
}

/* ---------- search ---------- */
document.getElementById('search').addEventListener('input', ev => {
  if (window.matchMedia('(max-width: 860px)').matches) {
    closeMobilePanels();
    document.body.classList.add('nav-open');
    navToggle.setAttribute('aria-expanded', 'true');
  }
  const q = ev.target.value.trim().toLowerCase();
  DATA.nodes.forEach(n => {
    const props = (n.properties || []).map(p => p.join(' ')).join(' ');
    const hay = (n.title + ' ' + n.description + ' ' + n.type + ' ' + n.tags.join(' ') + ' ' + n.status + ' ' + props).toLowerCase();
    const hit = !q || hay.includes(q);
    const navA = document.querySelector(`#nav a[data-id="${cssEscape(n.id)}"]`);
    navA && navA.classList.toggle('hidden', !hit);
    if (main.classList.contains('graph-only')) cy.getElementById(n.id).toggleClass('faded', !!q && !hit);
  });
});

/* ---------- legend ---------- */
function buildLegend() {
  const legend = document.getElementById('legend');
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
}

/* ---------- helpers ---------- */
function escapeHtml(s) { return String(s).replace(/[&<>]/g, c => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;' }[c])); }
function escapeAttr(s) { return escapeHtml(s).replace(/"/g, '&quot;'); }
function cssEscape(s) { return (window.CSS && CSS.escape) ? CSS.escape(s) : s.replace(/["\\]/g, '\\$&'); }

/* ---------- initial state ---------- */
runLayout();
buildLegend();
clearHighlight();
const start = decodeURIComponent(location.hash.slice(1));
if (start === 'log') openLog();
else if (byId[start]) openConcept(start);
else if (DATA.index) openIndex();
else showGraphOnly();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    raise SystemExit(main())

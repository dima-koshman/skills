import json
import pathlib
import re
import subprocess
import sys
from typing import cast

import pytest
import yaml

_SCRIPTS = pathlib.Path(__file__).parent.parent / ".agents/skills/okf/scripts"


@pytest.fixture
def bundle(tmp_path: pathlib.Path) -> pathlib.Path:
    root = tmp_path / "bundle"
    _write(root / "people/ana.md", {"type": "Person", "title": "Ana"}, "Engineer.")
    _write(
        root / "services/api.md",
        {
            "type": "Service",
            "title": "API",
            "description": "The API.",
            "owner": "/people/ana.md",
            "depends_on": ["/services/db.md", "/services/missing.md"],
            "kind": "custom",
            "generated": {"by": "human:ana", "at": "2026-10-01T10:00:00Z"},
            "verified": {"by": "human:ana", "at": "2026-10-02T10:00:00Z"},
            "stale_after": "2020-01-01T00:00:00Z",
            "sources": [
                {"id": "conf", "resource": "https://example.com/page", "title": "Page"},
                {"id": "db", "resource": "/services/db.md"},
            ],
        },
        "Runs on Kubernetes.[^conf]\n\n[^conf]: Confluence page",
    )
    _write(
        root / "services/db.md",
        {
            "type": "Service",
            "title": "DB",
            "status": "deprecated",
            "timestamp": "2025-01-01T00:00:00Z",
            "verified": [{"by": "process:nightly", "at": "2026-10-03T00:00:00Z"}],
        },
        "Old database.",
    )
    return root


def test_index_declares_okf_v0_2(bundle: pathlib.Path) -> None:
    _ = _run("okf_index.py", str(bundle))

    assert 'okf_version: "0.2"' in (bundle / "index.md").read_text()


def test_index_marks_deprecated_concepts(bundle: pathlib.Path) -> None:
    _ = _run("okf_index.py", str(bundle))

    lines = (bundle / "index.md").read_text().splitlines()
    db_line = next(line for line in lines if "[DB]" in line)
    assert "deprecated" in db_line


def test_site_reads_generated_and_falls_back_to_timestamp(bundle: pathlib.Path) -> None:
    nodes = _nodes(bundle)

    assert nodes["services/api.md"]["generated"] == {
        "by": "human:ana",
        "at": "2026-10-01T10:00:00Z",
    }
    assert nodes["services/db.md"]["generated"] == {
        "by": "",
        "at": "2025-01-01T00:00:00Z",
    }


def test_site_derives_trust_tier_from_verified(bundle: pathlib.Path) -> None:
    nodes = _nodes(bundle)

    assert nodes["services/api.md"]["trust"] == "human-reviewed"
    assert nodes["services/db.md"]["trust"] == "machine-confirmed"
    assert nodes["people/ana.md"]["trust"] == "unverified"


def test_site_treats_bare_verified_mapping_as_list(bundle: pathlib.Path) -> None:
    assert _nodes(bundle)["services/api.md"]["verified"] == [
        {"by": "human:ana", "at": "2026-10-02T10:00:00Z"}
    ]


def test_site_lifecycle_status_and_staleness(bundle: pathlib.Path) -> None:
    nodes = _nodes(bundle)

    assert nodes["people/ana.md"]["status"] == "stable"
    assert nodes["services/db.md"]["status"] == "deprecated"
    assert nodes["services/api.md"]["stale"] is True
    assert nodes["people/ana.md"]["stale"] is False


def test_site_turns_frontmatter_concept_paths_into_labeled_edges(
    bundle: pathlib.Path,
) -> None:
    edges = cast(list[dict[str, str]], _data(bundle)["edges"])

    owner = {"source": "services/api.md", "target": "people/ana.md", "label": "owner"}
    depends = {
        "source": "services/api.md",
        "target": "services/db.md",
        "label": "depends_on",
    }
    assert owner in edges
    assert depends in edges
    assert all(edge["target"] != "services/missing.md" for edge in edges)


def test_site_lists_extra_frontmatter_as_linked_properties(
    bundle: pathlib.Path,
) -> None:
    rows = cast(list[list[str]], _nodes(bundle)["services/api.md"]["properties"])
    properties = {row[0]: row[1] for row in rows}

    assert properties["owner"] == "[Ana](#node:people/ana.md)"
    assert properties["kind"] == "custom"
    assert "generated" not in properties and "sources" not in properties


def test_site_links_sources_and_footnotes(bundle: pathlib.Path) -> None:
    node = _nodes(bundle)["services/api.md"]
    sources = cast(list[dict[str, str]], node["sources"])
    body = str(node["body"])

    assert sources[0] == {
        "id": "conf",
        "resource": "https://example.com/page",
        "title": "Page",
        "href": "https://example.com/page",
    }
    assert sources[1]["href"] == "#node:services/db.md"
    assert "[^conf]:" not in body
    assert re.search(r'<sup class="fn"><a href="#src-conf">', body)


@pytest.mark.parametrize("trust", ["unverified", "machine-confirmed", "human-reviewed"])
def test_reader_omits_verification_pills(bundle: pathlib.Path, trust: str) -> None:
    rendered = _reader_html(bundle, "services/api.md", {"trust": trust})

    assert trust not in rendered
    assert "<h1>API</h1>" in rendered
    assert "#node:people/ana.md" in rendered


@pytest.mark.parametrize("stale", [False, True])
def test_reader_omits_freshness_pills(bundle: pathlib.Path, stale: bool) -> None:
    rendered = _reader_html(bundle, "services/api.md", {"stale": stale})

    assert "fresh until" not in rendered
    assert "stale since" not in rendered
    assert "2020-01-01T00:00:00Z" not in rendered


def test_reader_omits_authorship_and_verification_line(bundle: pathlib.Path) -> None:
    rendered = _reader_html(bundle, "services/api.md", {})

    assert "Generated by" not in rendered
    assert "Verified by" not in rendered
    assert "2026-10-01T10:00:00Z" not in rendered
    assert "2026-10-02T10:00:00Z" not in rendered
    assert 'id="src-conf"' in rendered


@pytest.mark.parametrize("status", ["draft", "deprecated"])
def test_reader_keeps_lifecycle_status_pill(bundle: pathlib.Path, status: str) -> None:
    rendered = _reader_html(bundle, "services/api.md", {"status": status})

    assert f'class="pill status-{status}"' in rendered


def test_stable_reader_has_no_empty_lifecycle_row(bundle: pathlib.Path) -> None:
    rendered = _reader_html(bundle, "services/api.md", {})

    assert 'class="lifecycle"' not in rendered


def test_index_encodes_spaces_and_parentheses_in_concept_links(
    bundle: pathlib.Path,
) -> None:
    _write(
        bundle / "Platform Services/AI Gateway (LiteLLM)/repo.md",
        {"type": "Repository", "title": "Repo"},
        "Image.",
    )

    _ = _run("okf_index.py", str(bundle))

    index = (bundle / "index.md").read_text()
    assert "## AI Gateway (LiteLLM)" in index
    assert "[Repo](/Platform%20Services/AI%20Gateway%20%28LiteLLM%29/repo.md)" in index


def test_site_resolves_encoded_links_to_title_named_directories(
    bundle: pathlib.Path,
) -> None:
    _write(
        bundle / "Platform People/AI Platform Team.md",
        {"type": "Team", "title": "AI Platform Team"},
        "Team.",
    )
    _write(
        bundle / "Platform Services/AI Gateway (LiteLLM)/repo.md",
        {
            "type": "Repository",
            "title": "Repo",
            "owner": "/Platform People/AI Platform Team.md",
            "sources": [
                {"id": "team", "resource": "/Platform People/AI Platform Team.md"}
            ],
        },
        "Owned by [the team](/Platform%20People/AI%20Platform%20Team.md).",
    )

    nodes = _nodes(bundle)
    repo = nodes["Platform Services/AI Gateway (LiteLLM)/repo.md"]
    assert (
        repo["body"]
        == "Owned by [the team](#node:Platform%20People/AI%20Platform%20Team.md)."
    )
    assert repo["properties"] == [
        ["owner", "[AI Platform Team](#node:Platform%20People/AI%20Platform%20Team.md)"]
    ]
    sources = cast(list[dict[str, object]], repo["sources"])
    assert sources[0]["href"] == "#node:Platform%20People/AI%20Platform%20Team.md"
    edges = cast(list[dict[str, object]], _data(bundle)["edges"])
    assert any(
        edge["target"] == "Platform People/AI Platform Team.md" for edge in edges
    )


def test_site_directory_labels_preserve_the_exact_directory_name(
    bundle: pathlib.Path,
) -> None:
    output = bundle.parent / "labels.html"
    _ = _run("okf_site.py", str(bundle), "-o", str(output))
    javascript = r"""
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync(process.argv[1], 'utf8');
const definition = html.match(/function dirLabel\(path\) \{.*?\n}/s)[0];
const context = { dirs: { 'Platform People/AI Platform Team': { name: 'AI Platform Team', concepts: ['one', 'two'] } } };
process.stdout.write(vm.runInNewContext(definition + '\ndirLabel("Platform People/AI Platform Team")', context));
"""
    result = subprocess.run(
        ["node", "-e", javascript, str(output)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == "AI Platform Team"
    nav_style = next(
        line
        for line in output.read_text().splitlines()
        if "#nav .dir > .label {" in line
    )
    assert "text-transform:uppercase" not in nav_style


def test_site_edge_click_finds_encoded_concept_link(bundle: pathlib.Path) -> None:
    output = bundle.parent / "edge.html"
    _ = _run("okf_site.py", str(bundle), "-o", str(output))
    javascript = r"""
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync(process.argv[1], 'utf8');
const definition = html.match(/function openEdgeLink\(edge\) \{.*?\n\}/s)[0];
let opened = '', scrolled = false;
const anchor = {
  getAttribute: () => '#node:Platform%20People/AI%20Platform%20Team.md',
  scrollIntoView: () => { scrolled = true; },
  classList: { add: () => {}, remove: () => {} },
};
const context = {
  edge: { data: key => ({ source: 'source.md', target: 'Platform People/AI Platform Team.md',
    links: [{ target: 'Platform People/AI Platform Team.md' }] })[key] },
  isDirId: () => false,
  openConcept: id => { opened = id; },
  doc: { querySelectorAll: () => [anchor], querySelector: () => null },
  setTimeout: () => {},
};
vm.runInNewContext(definition + '\nopenEdgeLink(edge)', context);
process.stdout.write(JSON.stringify({ opened, scrolled }));
"""
    result = subprocess.run(
        ["node", "-e", javascript, str(output)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {"opened": "source.md", "scrolled": True}


def _write(path: pathlib.Path, frontmatter: dict[str, object], body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = yaml.safe_dump(frontmatter, sort_keys=False)
    _ = path.write_text(f"---\n{header}---\n\n{body}\n")


def _run(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [sys.executable, str(_SCRIPTS / script), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"{script} exited {result.returncode}:\n{result.stderr}"
    )
    return result


def _reader_html(
    bundle: pathlib.Path, concept_id: str, overrides: dict[str, object]
) -> str:
    """Execute the generated reader in Node with only browser/graph APIs stubbed."""
    output = bundle.parent / "reader.html"
    _ = _run("okf_site.py", str(bundle), "-o", str(output))
    javascript = r"""
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync(process.argv[1], 'utf8');
const data = JSON.parse(html.match(/const DATA = (\{.*?\});\n/s)[1]);
const node = data.nodes.find(node => node.id === process.argv[2]);
Object.assign(node, JSON.parse(process.argv[3]));
const names = ['escapeHtml', 'escapeAttr', 'lifecycleHtml', 'provenanceHtml',
               'propertiesHtml', 'sourcesHtml', 'openConcept'];
const definitions = names.map(name => {
  const start = html.indexOf('function ' + name + '(');
  if (start < 0) {
    if (name === 'provenanceHtml') return '';
    throw new Error('Missing reader function: ' + name);
  }
  const lineEnd = html.indexOf('\n', start);
  const firstLine = html.slice(start, lineEnd);
  const end = firstLine.trimEnd().endsWith('}') ? lineEnd : html.indexOf('\n}', start) + 2;
  return html.slice(start, end);
}).join('\n');
const doc = { innerHTML: '', scrollTop: 0,
  appendChild(child) { this.innerHTML += '<div class="' + child.className + '">' + child.innerHTML + '</div>'; } };
const noop = () => {};
const context = {
  byId: { [node.id]: node }, node, doc,
  representative: id => id,
  closeMobilePanels: noop, wireDocLinks: noop, setActiveNav: noop,
  highlight: noop, focusOn: noop,
  main: { classList: { remove: noop } },
  document: { createElement: () => ({ className: '', innerHTML: '' }) },
  marked: { parse: value => value, parseInline: value => value },
  history: { replaceState: noop },
};
vm.runInNewContext(definitions + '\nopenConcept(node.id);', context);
process.stdout.write(doc.innerHTML);
"""
    result = subprocess.run(
        ["node", "-e", javascript, str(output), concept_id, json.dumps(overrides)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout


def _data(bundle: pathlib.Path) -> dict[str, object]:
    output = bundle.parent / "site.html"
    _ = _run("okf_site.py", str(bundle), "-o", str(output))
    match = re.search(r"const DATA = (\{.*?\});\n", output.read_text(), re.S)
    assert match is not None
    return cast(dict[str, object], json.loads(match.group(1).replace("<\\/", "</")))


def _nodes(bundle: pathlib.Path) -> dict[str, dict[str, object]]:
    nodes = cast(list[dict[str, object]], _data(bundle)["nodes"])
    return {str(node["id"]): node for node in nodes}


def test_index_lists_underscore_meta_directories_last(bundle: pathlib.Path) -> None:
    _write(
        bundle / "_types/service.md",
        {"type": "Concept Type", "title": "Service"},
        "Def.",
    )

    _ = _run("okf_index.py", str(bundle))

    headings = [
        line
        for line in (bundle / "index.md").read_text().splitlines()
        if line.startswith("# ")
    ]
    assert headings[-1] == "# _types"

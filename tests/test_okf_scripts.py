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


def test_site_focus_reveals_connected_concepts_before_highlighting(
    bundle: pathlib.Path,
) -> None:
    output = bundle.parent / "focus.html"
    _ = _run("okf_site.py", str(bundle), "-o", str(output))
    javascript = r"""
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync(process.argv[1], 'utf8');
const names = ['connectedDirectories', 'focusConnections'];
const definitions = names.map(name => html.match(new RegExp('function ' + name + '\\([^]*?\\n}', 's'))[0]).join('\n');
const selected = 'People/AI Platform Team/ibrahim-aliyev.md';
const edges = [
  { source: selected, target: 'Services/AI Gateway (LiteLLM)/ai-gateway-general.md' },
  { source: 'Systems/gitlab.md', target: selected },
  { source: 'Processes/ci.md', target: 'Systems/consul.md' },
];
let opened = '', expandedAtOpen = [];
const expanded = new Set(['People', 'People/AI Platform Team']);
const context = {
  DATA: { edges }, expanded,
  window: { matchMedia: () => ({ matches: false }) },
  representative: id => id === selected ? selected : 'dir:' + id.split('/')[0],
  ancestorsOf: id => id.split('/').slice(0, -1).map((_, i) => id.split('/').slice(0, i + 1).join('/')),
  isDirId: id => id.startsWith('dir:'), dirOf: id => id.slice(4),
  setExpanded: (paths, open, done) => { for (const path of paths) expanded.add(path); done(); },
  openConcept: id => { opened = id; expandedAtOpen = [...expanded].sort(); },
  openDir: () => { throw Error('opened directory for a concept'); },
};
vm.runInNewContext(definitions + '\nfocusConnections(' + JSON.stringify(selected) + ')', context);
process.stdout.write(JSON.stringify({ opened, expandedAtOpen }));
"""
    result = subprocess.run(
        ["node", "-e", javascript, str(output)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {
        "opened": "People/AI Platform Team/ibrahim-aliyev.md",
        "expandedAtOpen": [
            "People",
            "People/AI Platform Team",
            "Services",
            "Services/AI Gateway (LiteLLM)",
            "Systems",
        ],
    }


def test_site_single_click_refocuses_an_already_selected_node(
    bundle: pathlib.Path,
) -> None:
    output = bundle.parent / "click.html"
    _ = _run("okf_site.py", str(bundle), "-o", str(output))
    javascript = r"""
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync(process.argv[1], 'utf8');
const definition = html.match(/function onSingleClick\(target\) \{.*?\n\}/s)[0];
let focused = '', cleared = false;
const target = { id: () => 'people/ana.md', isEdge: () => false, hasClass: () => true };
const context = { target, cy: {}, isDirId: () => false,
  focusConnections: id => { focused = id; },
  clearHighlight: () => { cleared = true; },
  openConcept: () => {}, openDir: () => {}, openEdgeLink: () => {} };
vm.runInNewContext(definition + '\nonSingleClick(target)', context);
process.stdout.write(JSON.stringify({ focused, cleared }));
"""
    result = subprocess.run(
        ["node", "-e", javascript, str(output)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {"focused": "people/ana.md", "cleared": False}


def test_site_node_menu_orders_focus_before_directory_action(
    bundle: pathlib.Path,
) -> None:
    output = bundle.parent / "menu.html"
    _ = _run("okf_site.py", str(bundle), "-o", str(output))
    html = output.read_text()
    menu = re.search(r'<div id="node-menu"[^>]*>(.*?)</div>', html, re.S)
    assert menu is not None
    assert re.findall(r'data-action="([^"]+)"', menu.group(1)) == ["focus", "toggle"]
    javascript = r"""
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync(process.argv[1], 'utf8');
const definition = html.match(/function onNodeMenuAction\(action, id\) \{.*?\n\}/s)[0];
const actions = [];
const context = {
  focusConnections: id => actions.push(['focus', id]),
  onDoubleClick: target => actions.push(['toggle', target.id()]),
  cy: { getElementById: id => ({ id: () => id, nonempty: () => true }) },
};
vm.runInNewContext(definition + '\nonNodeMenuAction("focus", "people/ana.md"); onNodeMenuAction("toggle", "people/ana.md")', context);
process.stdout.write(JSON.stringify(actions));
"""
    result = subprocess.run(
        ["node", "-e", javascript, str(output)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == [
        ["focus", "people/ana.md"],
        ["toggle", "people/ana.md"],
    ]


def test_site_focus_keeps_mobile_graph_visible(bundle: pathlib.Path) -> None:
    output = bundle.parent / "mobile-focus.html"
    _ = _run("okf_site.py", str(bundle), "-o", str(output))
    javascript = r"""
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync(process.argv[1], 'utf8');
const definition = html.match(/function focusConnections\(id\) \{.*?\n\}/s)[0];
const classes = new Set(['graph-only']);
let aria = '';
const context = {
  connectedDirectories: () => [],
  setExpanded: (paths, open, done) => done(),
  isDirId: () => false,
  openConcept: () => { classes.delete('graph-only'); classes.delete('mobile-graph'); },
  main: { classList: { contains: name => classes.has(name), add: name => classes.add(name) } },
  graphToggle: { setAttribute: (name, value) => { if (name === 'aria-expanded') aria = value; } },
  window: { matchMedia: () => ({ matches: true }) },
};
vm.runInNewContext(definition + '\nfocusConnections("people/ana.md")', context);
process.stdout.write(JSON.stringify({ visible: classes.has('mobile-graph'), aria }));
"""
    result = subprocess.run(
        ["node", "-e", javascript, str(output)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {"visible": True, "aria": "true"}


def test_site_node_menu_survives_programmatic_pan(bundle: pathlib.Path) -> None:
    output = bundle.parent / "pan-menu.html"
    _ = _run("okf_site.py", str(bundle), "-o", str(output))
    javascript = r"""
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync(process.argv[1], 'utf8');
const bindings = html.match(/^cy\.on\('[^']+', hideNodeMenu\);$/mg) || [];
const handlers = {};
let hidden = false;
const context = {
  cy: { on: (events, handler) => { for (const event of events.split(' ')) handlers[event] = handler; } },
  hideNodeMenu: () => { hidden = true; },
};
vm.runInNewContext(bindings.join('\n'), context);
if (handlers.pan) handlers.pan();
process.stdout.write(JSON.stringify({ hidden }));
"""
    result = subprocess.run(
        ["node", "-e", javascript, str(output)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {"hidden": False}


def test_site_matching_overview_renders_one_collapsible_sidebar_entry(
    bundle: pathlib.Path,
) -> None:
    _write(
        bundle / "Platform Services/AI Gateway/AI Gateway child.md",
        {"type": "Repository", "title": "Child"},
        "Child repository.",
    )
    _write(
        bundle / "Platform Services/AI Gateway.md",
        {"type": "Service", "title": "AI Gateway"},
        "Gateway overview.",
    )
    output = bundle.parent / "merged-tree.html"
    _ = _run("okf_site.py", str(bundle), "-o", str(output))
    javascript = r"""
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync(process.argv[1], 'utf8');
const data = JSON.parse(html.match(/const DATA = (\{.*?\});\n/s)[1]);
const names = ['buildTree', 'renderTree'];
const definitions = names.map(name => html.match(new RegExp('function ' + name + '\\([^]*?\\n}', 's'))[0]).join('\n');
function element(tag) {
  return { tag, children: [], dataset: {}, className: '', innerHTML: '',
    classList: { add() {} }, setAttribute() {}, addEventListener() {}, appendChild(child) { this.children.push(child); } };
}
const document = { createElement: element };
const dirs = {};
for (const n of data.nodes) {
  const parts = n.id.split('/');
  for (let i = 1; i < parts.length; i++) {
    const path = parts.slice(0, i).join('/');
    (dirs[path] ||= { name: parts[i - 1], concepts: [] }).concepts.push(n.id);
  }
}
dirs['Platform Services/AI Gateway'].overviewId = 'Platform Services/AI Gateway.md';
const context = { DATA: data, document, dirs, escapeHtml: s => s, escapeAttr: s => s,
  dirLabel: path => dirs[path].name, expanded: new Set(), expandDir() {}, collapseDir() {},
  openConcept() {}, openDir() {} };
const tree = vm.runInNewContext(definitions + '\nrenderTree(buildTree(DATA.nodes))', context);
const services = tree.children.find(li => li.dataset.dir === 'Platform Services');
const siblings = services.children[1].children;
const merged = siblings.filter(li => li.dataset.dir === 'Platform Services/AI Gateway');
const overviewLinks = siblings.flatMap(li => li.children[0].children || [])
  .filter(el => el.dataset.id === 'Platform Services/AI Gateway.md');
const overviewColor = data.nodes.find(n => n.id === 'Platform Services/AI Gateway.md').color;
const linkMarkup = overviewLinks[0].innerHTML;
process.stdout.write(JSON.stringify({ merged: merged.length, siblings: siblings.length,
  overviewLinks: overviewLinks.length, children: merged[0].children[1].children.length,
  dotBeforeTitle: linkMarkup === '<span class="dot" style="background:' + overviewColor +
    '"></span><span>AI Gateway</span>' }));
"""
    result = subprocess.run(
        ["node", "-e", javascript, str(output)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {
        "merged": 1,
        "siblings": 1,
        "overviewLinks": 1,
        "children": 1,
        "dotBeforeTitle": True,
    }


def test_site_matching_overview_replaces_synthetic_graph_directory(
    bundle: pathlib.Path,
) -> None:
    _write(
        bundle / "Platform Services/AI Gateway/repo.md",
        {"type": "Repository", "title": "Repo"},
        "Child repository.",
    )
    _write(
        bundle / "Platform Services/AI Gateway.md",
        {"type": "Service", "title": "AI Gateway"},
        "Gateway overview.",
    )
    output = bundle.parent / "merged-graph.html"
    _ = _run("okf_site.py", str(bundle), "-o", str(output))
    javascript = r"""
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync(process.argv[1], 'utf8');
const data = JSON.parse(html.match(/const DATA = (\{.*?\});\n/s)[1]);
const names = ['ancestorsOf', 'representative', 'directoryForNode', 'graphNodeForRepresentative'];
const definitions = names.map(name => html.match(new RegExp('function ' + name + '\\([^]*?\\n}', 's'))[0]).join('\n');
const byId = Object.fromEntries(data.nodes.map(n => [n.id, n]));
const dirs = {
  'Platform Services': { name: 'Platform Services', concepts: ['Platform Services/AI Gateway/repo.md'] },
  'Platform Services/AI Gateway': { name: 'AI Gateway', concepts: ['Platform Services/AI Gateway/repo.md'], overviewId: 'Platform Services/AI Gateway.md' },
};
const expanded = new Set(['Platform Services']);
const context = { byId, dirs, expanded, DIR_PREFIX: 'dir:',
  isDirId: id => id.startsWith('dir:'), dirOf: id => id.slice(4),
  dirLabel: path => dirs[path].name };
const collapsed = vm.runInNewContext(definitions + '\nrepresentative("Platform Services/AI Gateway/repo.md")', context);
const node = vm.runInNewContext(definitions + '\ngraphNodeForRepresentative("Platform Services/AI Gateway.md")', context);
expanded.add('Platform Services/AI Gateway');
const expandedChild = vm.runInNewContext(definitions + '\nrepresentative("Platform Services/AI Gateway/repo.md")', context);
process.stdout.write(JSON.stringify({ collapsed, expandedChild, id: node.data.id,
  label: node.data.label, classes: node.classes }));
"""
    result = subprocess.run(
        ["node", "-e", javascript, str(output)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {
        "collapsed": "Platform Services/AI Gateway.md",
        "expandedChild": "Platform Services/AI Gateway/repo.md",
        "id": "Platform Services/AI Gateway.md",
        "label": "AI Gateway",
        "classes": "overview status-stable",
    }


def test_site_merged_node_toggles_own_directory_and_opens_its_page(
    bundle: pathlib.Path,
) -> None:
    output = bundle.parent / "merged-actions.html"
    _ = _run("okf_site.py", str(bundle), "-o", str(output))
    javascript = r"""
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync(process.argv[1], 'utf8');
const names = ['directoryForNode', 'onDoubleClick', 'openDir'];
const definitions = names.map(name => html.match(new RegExp('function ' + name + '\\([^]*?\\n}', 's'))[0]).join('\n');
const path = 'Platform Services/AI Gateway';
const id = path + '.md';
const expanded = new Set();
const actions = [];
const dirs = { [path]: { overviewId: id } };
const target = { id: () => id, isEdge: () => false };
const context = { dirs, expanded, target, cy: {}, DIR_PREFIX: 'dir:',
  isDirId: id => id.startsWith('dir:'), dirOf: id => id.slice(4),
  parentDirOf: () => 'Platform Services',
  expandDir: (path, done) => { expanded.add(path); done(); },
  collapseDir: (path, done) => { expanded.delete(path); done(); },
  openConcept: id => actions.push(['open', id]),
  doc: { innerHTML: '' },
};
vm.runInNewContext(definitions + '\nonDoubleClick(target); onDoubleClick(target); openDir(' + JSON.stringify(path) + ')', context);
process.stdout.write(JSON.stringify({ actions, expanded: expanded.has(path) }));
"""
    result = subprocess.run(
        ["node", "-e", javascript, str(output)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {
        "actions": [["open", "Platform Services/AI Gateway.md"]] * 3,
        "expanded": False,
    }


def test_site_search_keeps_merged_section_title_visible_for_child_match(
    bundle: pathlib.Path,
) -> None:
    output = bundle.parent / "merged-search.html"
    _ = _run("okf_site.py", str(bundle), "-o", str(output))
    javascript = r"""
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync(process.argv[1], 'utf8');
const definition = html.match(/function searchNavMatch\([^]*?\n}/s)[0];
const overview = 'Platform Services/AI Gateway.md';
const context = { directoryForNode: id => id === overview ? 'Platform Services/AI Gateway' : null };
const result = vm.runInNewContext(definition + '\n[searchNavMatch(' + JSON.stringify(overview) +
  ', ["Platform Services/AI Gateway/repo.md"]), searchNavMatch(' + JSON.stringify(overview) +
  ', ["Platform Services/AI Gateway Extended/repo.md"])]', context);
process.stdout.write(JSON.stringify(result));
"""
    result = subprocess.run(
        ["node", "-e", javascript, str(output)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == [True, False]


def test_site_type_legend_matches_merged_overview_or_children(
    bundle: pathlib.Path,
) -> None:
    output = bundle.parent / "merged-type.html"
    _ = _run("okf_site.py", str(bundle), "-o", str(output))
    javascript = r"""
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync(process.argv[1], 'utf8');
const definition = html.match(/function nodeMatchesType\([^]*?\n}/s)[0];
const overview = 'Platform Services/AI Gateway.md';
const context = {
  byId: { [overview]: { type: 'Service' } },
  dirs: { 'Platform Services/AI Gateway': { types: new Set(['Repository']) } },
  directoryForNode: id => id === overview ? 'Platform Services/AI Gateway' : null,
  isDirId: () => false,
};
const result = vm.runInNewContext(definition + '\n["Service", "Repository", "Person"].map(type => nodeMatchesType(' +
  JSON.stringify(overview) + ', type))', context);
process.stdout.write(JSON.stringify(result));
"""
    result = subprocess.run(
        ["node", "-e", javascript, str(output)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == [True, True, False]


def test_site_active_merged_overview_highlights_its_sidebar_section(
    bundle: pathlib.Path,
) -> None:
    output = bundle.parent / "merged-active.html"
    _ = _run("okf_site.py", str(bundle), "-o", str(output))
    javascript = r"""
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync(process.argv[1], 'utf8');
const definition = html.match(/function setActiveNav\([^]*?\n}/s)[0];
function classes() {
  const values = new Set();
  return { add: value => values.add(value), remove: value => values.delete(value),
    contains: value => values.has(value) };
}
const label = { classList: classes() };
const link = { classList: classes(), parentElement: label };
link.classList.add('overview-link');
const context = {
  document: { querySelectorAll: () => [link, label],
    querySelector: selector => selector.includes('a[data-id=') ? link : null },
  isDirId: () => false, cssEscape: value => value,
};
vm.runInNewContext(definition + '\nsetActiveNav("Platform Services/AI Gateway.md")', context);
process.stdout.write(JSON.stringify({ link: link.classList.contains('active'),
  section: label.classList.contains('active') }));
"""
    result = subprocess.run(
        ["node", "-e", javascript, str(output)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {"link": True, "section": True}


def test_site_caption_counts_collapsed_merged_overviews_as_directories(
    bundle: pathlib.Path,
) -> None:
    output = bundle.parent / "merged-caption.html"
    _ = _run("okf_site.py", str(bundle), "-o", str(output))
    javascript = r"""
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync(process.argv[1], 'utf8');
const definition = html.match(/function graphCounts\([^]*?\n}/s)[0];
const ids = ['Platform Services/AI Gateway.md', 'people/ana.md', 'dir:systems'];
const context = {
  cy: { nodes: () => ids.map(id => ({ id: () => id })) },
  expanded: new Set(),
  isDirId: id => id.startsWith('dir:'),
  directoryForNode: id => id.startsWith('dir:') ? id.slice(4) :
    id === ids[0] ? 'Platform Services/AI Gateway' : null,
};
process.stdout.write(JSON.stringify(vm.runInNewContext(definition + '\ngraphCounts()', context)));
"""
    result = subprocess.run(
        ["node", "-e", javascript, str(output)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {"concepts": 2, "directories": 2}


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

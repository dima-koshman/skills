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

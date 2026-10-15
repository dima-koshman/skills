---
type: Concept
title: OKF Visualizers
description: Comparison of the upstream static HTML viewer with our custom graph-and-reader renderer,
  including adoption instructions and compatibility limits.
tags:
- ai-engineering
- context
parent: /ai-engineering/context.md
related:
- /ai-engineering/context/okf.md
note_date: '2026-09-30'
sources:
- id: ref-1
  resource: https://github.com/GoogleCloudPlatform/open-knowledge-format#visualize
  title: github.com
- id: ref-2
  resource: https://okf.md/tools/#2-static-html-visualizer-vizhtml
  title: 'Tools directory: static visualizer'
- id: ref-3
  resource: https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/src/reference_agent/viewer/generator.py
  title: 'Generator: link extraction, reserved-file handling, type colors'
- id: ref-4
  resource: https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/src/reference_agent/viewer/static/viz.js
  title: Browser logic and metadata display
- id: ref-5
  resource: https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/pyproject.toml
  title: Package dependencies
generated:
  by: codex/gpt-6
  at: '2026-10-15T15:23:06+04:00'
---

Reference: <https://github.com/GoogleCloudPlatform/open-knowledge-format#visualize>

Note dated: 2026-09-30 18:00:00+00:00.

The [OKF](/ai-engineering/context/okf.md) tools directory links Google's reference-agent
`visualize` command. It renders a bundle into one HTML file with embedded data
and a browser-side graph. This is a reference consumer, not a required part of
the format. Comparison below is based on upstream source and generator runs
against both local bundles on 2026-09-30.

## Comparison

| Capability | Local `okf_site.py` | Upstream `visualize` |
| --- | --- | --- |
| Basic view | Graph and reader, directory tree | Graph and detail panel |
| Navigation | Index landing page, change log, mobile Contents/Graph controls, Back/Forward history, typed backlinks | Computed “Cited by” backlinks and selectable graph layouts |
| Search | Title, description, type, tags | Title, concept ID, tags |
| Types | Dynamically assigned colors and clickable legend | Type filter; fixed colors for BigQuery Dataset, BigQuery Table, Reference; other types share gray |
| v0.2 metadata | Shows lifecycle status; preserves provenance/trust in embedded data without displaying them | Displays sources, authorship, verification, status, trust tier, and staleness |
| Bundle-relative graph links | Resolves `/concept.md` and relative links | Current extractor skips targets starting with `/` |
| Reserved files | Excludes index and log from concepts; renders them separately | Skips index, but includes log as an Unknown concept |
| Dependencies | Python standard library and PyYAML | Full CLI package also depends on Google ADK, BigQuery, Pydantic, and markdownify |
| Distribution | One generated HTML file | One generated HTML file |
| Offline viewing | CDN libraries required unless vendored | CDN libraries required unless vendored |

Both use Cytoscape.js and marked.js. Neither needs a backend to browse the
generated file. Upstream's documentation describes bundle-relative navigation,
but its current Python graph extractor explicitly discards those link targets.
Running the unchanged upstream generator modules against our bundles produced
**zero edges** in each. The log was also included as a node. These are concrete
compatibility limits, not limitations of the OKF format.

## Can it replace the custom viewer?

**Not as a drop-in replacement today.** Keep the custom viewer for normal
browsing. Upstream is worth evaluating for its backlinks, graph layouts, and
v0.2 metadata display, but losing our cross-link graph defeats its main purpose.

Three options:

1. **Keep the custom renderer** (recommended now): preserve graph links,
   directory navigation, mobile controls, and the current build tasks.
2. **Preview upstream alongside it**: generate a separate `viz.html`; accept
   the current graph limitations while exploring its metadata presentation.
3. **Adopt upstream after compatibility work**: ensure bundle-root links work,
   both reserved filenames are handled, and our custom types are distinguishable.
   Converting links to document-relative form in a disposable export can test
   the graph without rewriting canonical bundle identities. Verify mobile
   reading and index/log access before replacing the current workflow.

## Current local workflow (2026-10-15)

**Wiki: regenerate, render and open** selects `wiki/` (the authoritative source,
default) or `openwiki/` (generated experiment). The local reader merges sibling
directory-overview concepts, uses `_types/` descriptions and `primary_fields` for
properties and technical details, draws typed frontmatter edges, and renders
Mermaid diagrams. Both bundles can therefore be inspected directly. The upstream
comparison above remains the result of the dated inspection, not a fresh upstream audit.

## How to run upstream

From a checkout of the upstream repository, the documented CLI path is:

```bash
git clone https://github.com/GoogleCloudPlatform/open-knowledge-format.git
cd open-knowledge-format
python3 -m venv .venv
.venv/bin/pip install .
.venv/bin/python -m reference_agent visualize \
  --bundle /Users/koshmandmitry/Projects/dima/wiki \
  --out /tmp/wiki-viz.html \
  --name "Maintained Wiki"
.venv/bin/python -m reference_agent visualize \
  --bundle /Users/koshmandmitry/Projects/dima/openwiki \
  --out /tmp/openwiki-viz.html \
  --name "Generated OpenWiki"
```

The package requires Python >=3.11. Pin the checkout to a reviewed commit for
repeatable use. Open either output in a browser. Rendering existing Markdown
does not invoke enrichment or require BigQuery/Gemini credentials; however,
the CLI eagerly imports agent dependencies, so the full package installation
is heavier than the local renderer.

Verification boundary: this review ran the unchanged viewer and document-parser
modules with PyYAML in a temporary package layout. It did not install the full
agent dependency tree or run the full CLI above. The commands match the
inspected README, package manifest, and CLI arguments. No renderer or build-task
replacement was made.

## Resources

- [Tools directory: static visualizer](https://okf.md/tools/#2-static-html-visualizer-vizhtml)
- [Upstream README and commands](https://github.com/GoogleCloudPlatform/open-knowledge-format#visualize)
- [Generator: link extraction, reserved-file handling, type colors](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/src/reference_agent/viewer/generator.py)
- [Browser logic and metadata display](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/src/reference_agent/viewer/static/viz.js)
- [Package dependencies](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/pyproject.toml)

---
name: okf
description: >
  Use when reading, authoring, or updating an OKF (Open Knowledge Format) bundle —
  Google's vendor-neutral markdown-plus-frontmatter standard for agent-readable
  knowledge about data and systems. Triggers on "OKF", "open knowledge format",
  "/okf", requests to document a table, dataset, service, metric, runbook, playbook,
  API, or join path so an agent can read it, or to make internal knowledge
  agent-readable or portable. Covers the concept-document format (v0.2: provenance,
  trust, lifecycle), cross-linking, regenerating index.md, keeping log.md current,
  and rendering the bundle as a browsable HTML knowledge graph.
---

# Open Knowledge Format (OKF)

OKF represents knowledge — metadata, context, and curated insight about data and
systems — as **a directory of markdown files with YAML frontmatter**. No schema
registry, no central authority, no required tooling. One concept per file; the
file path is the concept's identity.

`references/spec.md` is the upstream **v0.2** specification, vendored verbatim. Read
it before authoring a new bundle or when a detail here is not enough; it is the
source of truth for field names, link forms, and conformance rules.

Scripts live in this skill's `scripts/` directory and need only Python 3.12+ and
PyYAML. From any repository, run them by absolute path, e.g.
`uv run --no-project --with pyyaml python ~/Projects/dima/.agents/skills/okf/scripts/okf_site.py <bundle-dir>`.

## Reading a bundle

1. Start at the bundle-root `index.md` if present — it is a progressive-disclosure
   listing of what the bundle contains. If absent, walk the tree yourself.
2. Each non-reserved `.md` file is one concept (`index.md` and `log.md` are
   reserved). Its frontmatter `type` tells you what kind of thing it is; the body
   holds the detail (often under `# Schema`, `# Examples`).
3. Follow markdown links to related concepts. Bundle-relative links begin with
   `/` (from the bundle root); relative links use `./`. Frontmatter values may also
   be bundle-relative paths to other concepts (spec §6.2) — treat them as typed
   relationships named by their key (e.g. `owner: /people/ana.md`).
4. Judge trust and freshness from frontmatter, not prose: `verified` gives the trust
   tier (none ⇒ unverified; only non-`human:` actors ⇒ machine-confirmed; any
   `human:` actor ⇒ human-reviewed), `status: deprecated` means kept only for history,
   and a passed `stale_after` means re-check before relying on it.
5. **Consume permissively** (spec §11): never reject a bundle for missing optional
   fields, unknown `type` values, unknown extra frontmatter keys, broken links,
   or a missing `index.md`. A broken link may just be not-yet-written knowledge.

## Authoring or updating a concept

- **One concept per file.** The file's path within the bundle *is* its identity,
  so choose a stable location; prefer moving concepts rarely. Readable directory
  names with spaces are supported. When a directory has an overview concept,
  matching its directory name, overview filename and `title` keeps the catalog,
  navigation tree and graph labels consistent. Individual concept filenames can
  remain stable slugs.
- **Frontmatter** — `type` is the only required field. Add `title`, `description`
  (a single sentence — it is reused in `index.md`), `resource` (canonical URI, if
  the concept describes a real asset) and `tags` when they apply. Any extra
  producer-defined keys are fine; when a key points at another concept, give a
  bundle-relative path (or a list of them) so tools can draw a labeled edge.
- **Provenance, trust, lifecycle (v0.2, §5)** — all optional, but use them:
  - `sources:` list of `{ id, resource, title, author?, last_modified? }`; `resource` is
    a URL, a bundle-relative path, or a scope descriptor. Attribute individual claims
    with markdown footnotes whose label is a source `id` (`…sharded daily.[^ga4]`).
    This **replaces** v0.1's body `# Citations` list.
  - `generated: { by, at }` — who wrote the current content and when it last changed
    meaningfully. This **replaces** v0.1's `timestamp`.
  - `verified:` list of `{ by, at }` — who confirmed it against its sources; separate
    from authorship. Add an event only when a real check happened.
  - `status: draft | stable | deprecated` (absent ⇒ stable); `stale_after:` an absolute
    instant after which the concept should be re-checked.
  - Actors (§7): `human:<id>` for people (required for human-authored or
    human-confirmed content), `<producer>/<version>` for agents (e.g.
    `claude-code/claude-opus-5-5`), `process:<id>` for automation.
  - Timestamps are ISO 8601 with an explicit offset (`2026-10-13T09:00:00Z`).
- **Body** — standard markdown; favor structure (headings, tables, fenced code)
  over prose. Conventional headings: `# Schema`, `# Examples`, `# Computation`.
- **Links** — prefer the bundle-relative form (`[customers](/tables/customers.md)`).
  Percent-encode spaces and parentheses in Markdown link URLs; keep frontmatter
  concept paths readable. Convey the *kind* of relationship in the surrounding prose
  (or as a frontmatter key).
- **Markdown linting** — OKF's convention of several top-level `#` sections
  alongside a frontmatter `title` intentionally trips markdownlint's MD025 (single
  H1) and MD041 (first-line heading). Ship a `.markdownlint.json` disabling `MD025`
  and `MD041` so bundles lint cleanly.

After adding, renaming, moving, or deleting any concept, do BOTH of the following.

## 1. Regenerate index.md

`index.md` is a build artifact derived from concept frontmatter — never hand-edit
it. Regenerate it with the bundled script:

```bash
# Single catalog at the bundle root, mirroring the directory hierarchy (default):
python scripts/okf_index.py <bundle-dir>

# One index.md per directory (that dir's concepts + links to subdirectories):
python scripts/okf_index.py <bundle-dir> --per-directory
```

The script overwrites existing `index.md` files, warns (without failing) on any
concept missing frontmatter or a `type`, tags each entry with its type (and its
status when not `stable`), and stamps `okf_version: "0.2"` into the bundle-root
index's frontmatter — the only index that carries frontmatter. Since it fully
regenerates, keep human-written descriptions in the concept files, not in `index.md`.

## Render a browsable HTML graph (optional)

To make a bundle navigable for humans, generate a single self-contained HTML page
with `scripts/okf_site.py` (the graph/markdown libraries load from a CDN, so
viewing needs internet):

```bash
python scripts/okf_site.py <bundle-dir>          # writes <bundle>/okf-site.html
python scripts/okf_site.py <bundle-dir> -o /tmp/graph.html
```

It renders an interactive knowledge graph (nodes = concepts colored by `type`,
edges = cross-links) beside a reading panel. The reader shows each concept's
lifecycle status, a Properties table of producer-defined keys (concept paths become
links), the body, and its `sources` with footnotes linked to them. Descriptions and
free-form property values render inline Markdown, with in-bundle links opening their concepts;
titles, types, tags, and URLs remain plain labels or links. Trust/freshness
pills and the generated/verified line are omitted from concept pages; the underlying
v0.2 metadata remains in frontmatter and embedded data for agents and tooling. Frontmatter concept paths also
become **labeled edges** named after their key; deprecated concepts are dimmed and
dashed, drafts dashed. Every directory starts **collapsed**: the sidebar tree and the graph share one
expanded/collapsed state. A directory without an overview is one grey rounded node, sized by its concept count; when
`<directory>.md` exists beside it, that concept and directory share one colored graph node and one sidebar section.
The merged sidebar row carries the concept type's colored dot; clicking anywhere in that row except its
caret expands the directory and opens the overview content on first selection. Clicking the selected row again
toggles its children. Its caret or a double-click on the merged sidebar row also toggles the children.
Concept links keep the overview file's original path. In the graph, double-clicking a leaf or nested directory node
collapses it into its parent; a top-level directory toggles its own children. Opening a concept (link, search, URL hash)
expands its ancestors. A single click centers a node, reveals the directories containing its linked concepts, and
highlights only that node, its edges and its directly connected nodes. Right-clicking a node offers focus first, then
its own-directory toggle (or parent collapse for a leaf), then a third "Collapse into parent directory" action only
for nested directories, including directory overviews. Double-clicking empty space or an edge fits the whole graph.
Graph and sidebar concept clicks share a ~150 ms window so a double-click can take precedence without making ordinary
navigation feel slow. The graph matches taps by node ID because Cytoscape can provide different target wrappers for
the same node; Cytoscape's native double-tap event catches slower pairs without delaying single clicks or repeating
the double-click action. The full layout uses fcose (cose as fallback); expanding or collapsing places only
the new nodes around their anchor, and "↻ Re-layout" redoes the full layout. The output is a build artifact — regenerate it, don't
hand-edit, and consider git-ignoring it.

## 2. Update log.md (via git + reasoning)

`log.md` is a human-meaningful, newest-first history — not a mechanical diff dump.
Write it yourself; do not automate it away:

1. Inspect what actually changed: `git status`, `git diff`, and `git log --oneline -5`
   for context. Base the entry on the real change, not an assumption.
2. Append under today's `## YYYY-MM-DD` heading (create it if absent, newest date
   first). Use a convention label — `**Creation**`, `**Update**`, `**Deprecation**`,
   `**Initialization**` — followed by a one-line prose summary that links the
   affected concept(s), e.g.:

   ```markdown
   ## 2026-07-04
   * **Update**: Revised the schema of [orders](/tables/orders.md) to add `channel`.
   ```

3. `log.md` may live at any level of the hierarchy; update the one nearest the
   scope you changed (usually the bundle root).

## Refreshing a knowledge base (periodic content review)

A bundle's concepts capture a point-in-time understanding and cite external
sources that drift: standards get revised, protocols and tools evolve or get
deprecated, and better resources appear. Knowledge decays unless it is refreshed —
so a long-lived bundle needs periodic review, not just edits when the user happens
to ask.

**When:** on a cadence the user sets (e.g. quarterly), when the user flags that a
domain has moved, when concepts pass their `stale_after`, or before relying on a
bundle for important work. This is a review pass, not something to run on every edit.

**How to review a bundle:**

1. **Inventory** the concepts from `index.md` (or by walking the tree). Start with
   concepts whose `stale_after` has passed, then the unverified ones.
2. For each concept, collect its `resource:` URI and every `sources[].resource`, and
   **fetch them**. Note dead links, redirects, and moved pages.
3. **Compare the concept's claims against the current source.** Flag drift:
   renamed or removed items, changed counts or IDs, deprecated features, superseded
   versions.
4. **Research the topic on the web** for changes, deprecations, and new
   authoritative resources the concept does not yet cite.
5. **Summarize proposed changes per concept.** Suggest concrete edits; when the
   scope is large or a call is judgment-heavy, ask the user which concepts or
   areas to update rather than rewriting unilaterally.
6. **Apply approved edits**: update `generated` on changed concepts, add a `verified`
   event for concepts you re-checked against their sources (even if unchanged), move
   `stale_after` forward, mark superseded concepts `status: deprecated`, regenerate
   `index.md` and the HTML site, and add a dated `log.md` `Update` entry saying what
   changed and why.

Keep edits surgical — update what actually drifted; don't rewrite concepts that
still hold. Structural changes (a renamed taxonomy, a split/merged concept) are
larger and should be brainstormed with the user before restructuring directories.

## Keeping current with the spec (rare, periodic)

OKF is a young, fast-moving draft (vendored here: **v0.2**). **Occasionally** — not
every run, only when starting substantial OKF work after a long gap, or if something
in a bundle looks inconsistent with `references/spec.md` — check upstream for a newer
revision:

- Spec: <https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md>

If the version has advanced past 0.2, tell the user and offer to update
`references/spec.md`, the `OKF_VERSION` constant in `scripts/okf_index.py`, the
renderer in `scripts/okf_site.py`, their tests (`tests/test_okf_scripts.py` in the
dima repo), and this skill together. Don't silently assume 0.2 is still current.

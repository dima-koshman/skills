---
name: okf
description: >
  Use when reading, authoring, or updating an OKF (Open Knowledge Format) bundle —
  Google's vendor-neutral markdown-plus-frontmatter standard for agent-readable
  knowledge about data and systems. Triggers on "OKF", "open knowledge format",
  "/okf", requests to document a table, dataset, view, metric, runbook, playbook,
  API, or join path so an agent can read it, or to make internal knowledge
  agent-readable or portable. Covers the concept-document format, cross-linking,
  regenerating index.md, and keeping log.md current.
---

# Open Knowledge Format (OKF)

OKF represents knowledge — metadata, context, and curated insight about data and
systems — as **a directory of markdown files with YAML frontmatter**. No schema
registry, no central authority, no required tooling. One concept per file; the
file path is the concept's identity.

`references/spec.md` is a condensed v0.1 reference. Read it before authoring a
new bundle or when a detail here is not enough; it is the source of truth for
field names, link forms, and conformance rules.

## Reading a bundle

1. Start at the bundle-root `index.md` if present — it is a progressive-disclosure
   listing of what the bundle contains. If absent, walk the tree yourself.
2. Each non-reserved `.md` file is one concept. Its frontmatter `type` tells you
   what kind of thing it is; the body holds the detail (often under `# Schema`,
   `# Examples`, `# Citations`).
3. Follow markdown links to related concepts. Bundle-relative links begin with
   `/` (from the bundle root); relative links use `./`.
4. **Consume permissively** (spec §9): never reject a bundle for missing optional
   fields, unknown `type` values, unknown extra frontmatter keys, broken links,
   or a missing `index.md`. A broken link may just be not-yet-written knowledge.

## Authoring or updating a concept

- **One concept per file.** The file's path within the bundle *is* its identity,
  so choose a stable location; prefer moving concepts rarely.
- **Frontmatter** — `type` is the only required field. Add `title`, `description`
  (a single sentence — it is reused in `index.md`), `resource` (canonical URI, if
  the concept describes a real asset), `tags`, and `timestamp` (ISO 8601) when
  they apply. Any extra producer-defined keys are fine.
- **Body** — standard markdown; favor structure (headings, tables, fenced code)
  over prose. Use the conventional headings `# Schema`, `# Examples`,
  `# Citations` when applicable.
- **Links** — prefer the bundle-relative form (`[customers](/tables/customers.md)`).
  Convey the *kind* of relationship in the surrounding prose; the link itself is
  untyped.

After adding, renaming, moving, or deleting any concept, do BOTH of the following.

## 1. Regenerate index.md

`index.md` is a build artifact derived from concept frontmatter — never hand-edit
it. Regenerate it with the bundled script (PyYAML is the only dependency):

```bash
# Single catalog at the bundle root, grouping every concept by type (default):
python scripts/okf_index.py <bundle-dir>

# One index.md per directory (that dir's concepts + links to subdirectories):
python scripts/okf_index.py <bundle-dir> --per-directory
```

The script overwrites existing `index.md` files, warns (without failing) on any
concept missing frontmatter or a `type`, and stamps `okf_version` into the
bundle-root index's frontmatter — the only index that carries frontmatter. Since
it fully regenerates, keep human-written descriptions in the concept files, not
in `index.md`.

## Render a browsable HTML graph (optional)

To make a bundle navigable for humans, generate a single self-contained HTML page
with `scripts/okf_site.py` (stdlib + PyYAML; the graph/markdown libraries load
from a CDN, so viewing needs internet):

```bash
python scripts/okf_site.py <bundle-dir>          # writes <bundle>/okf-site.html
python scripts/okf_site.py <bundle-dir> -o /tmp/graph.html
```

It renders an interactive knowledge graph (nodes = concepts colored by `type`,
edges = cross-links) beside a reading panel that renders each concept's markdown
with its in-bundle links wired to navigate the graph. Like `index.md` and
`okf-site.html`, the output is a build artifact — regenerate it, don't hand-edit,
and consider git-ignoring it.

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
sources that drift: standards get revised (the OWASP Agentic Top 10 changes year
to year), protocols and tools evolve or get deprecated (MCP, agent frameworks),
and better resources appear. Knowledge decays unless it is refreshed — so a
long-lived bundle needs periodic review, not just edits when the user happens to
ask.

**When:** on a cadence the user sets (e.g. quarterly), when the user flags that a
domain has moved, or before relying on a bundle for important work. This is a
review pass, not something to run on every edit.

**How to review a bundle:**

1. **Inventory** the concepts from `index.md` (or by walking the tree).
2. For each concept, collect its `resource:` URI and every citation link, and
   **fetch them**. Note dead links, redirects, and moved pages — a broken link or
   a stale `timestamp` is a cheap signal of what to review first.
3. **Compare the concept's claims against the current source.** Flag drift:
   renamed or removed items, changed counts or IDs (e.g. a threat list growing
   from 10 to 12), deprecated features, superseded versions.
4. **Research the topic on the web** for changes, deprecations, and new
   authoritative resources the concept does not yet cite.
5. **Summarize proposed changes per concept.** Suggest concrete edits; when the
   scope is large or a call is judgment-heavy, ask the user which concepts or
   areas to update rather than rewriting unilaterally.
6. **Apply approved edits**, bump each changed concept's `timestamp`, regenerate
   `index.md` and the HTML site, and add a dated `log.md` `Update` entry saying
   what changed and why.

Keep edits surgical — update what actually drifted; don't rewrite concepts that
still hold. Structural changes (a renamed taxonomy, a split/merged concept) are
larger and should be brainstormed with the user before restructuring directories.

## Keeping current with the spec (rare, periodic)

OKF is a young, fast-moving draft (currently v0.1). **Occasionally** — not every
run, only when starting substantial OKF work after a long gap, or if something in
a bundle looks inconsistent with `references/spec.md` — check upstream for a newer
revision:

- Spec: <https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md>

If the version has advanced past 0.1, or fields/reserved filenames have changed,
tell the user and offer to update `references/spec.md`, the `OKF_VERSION` constant
in `scripts/okf_index.py`, and this skill accordingly. Don't silently assume 0.1
is still current.

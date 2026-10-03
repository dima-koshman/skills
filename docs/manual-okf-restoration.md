# Restoring the manual OKF knowledge base

Recorded on 2026-10-03. This is a recovery plan; OpenWiki remains the active
workflow. Keep the maintained [source notes](../wiki/) even if generated tooling
changes.

## Recovery snapshot

The latest commit on the current branch containing the complete manual OKF setup is
[`e235a1efae8617f91291e5e0b85b610b3ba24dbf`](https://github.com/dima-koshman/skills/commit/e235a1efae8617f91291e5e0b85b610b3ba24dbf).
At the time of writing, this is HEAD; the legacy files' removal is uncommitted.
Use this fixed hash rather than a future HEAD.

The snapshot contains:

- `.agents/skills/okf/`: format instructions, a pinned specification, index generator,
  and custom HTML visualizer.
- `.agents/skills/okf-ai-engineering/`: routing skill and `ai-engineering/` bundle
  with 47 concept documents.
- `.agents/skills/okf-development/`: routing skill and `development/` bundle
  with 5 concept documents.
- Integration examples in `.vscode/tasks.json`, `.pre-commit-config.yaml`, and
  `.github/workflows/pages.yml`.

The last commit that changed the custom renderer itself was
[`1803b6360cc2ee3aef5bf106999c4265bbe87228`](https://github.com/dima-koshman/skills/commit/1803b6360cc2ee3aef5bf106999c4265bbe87228)
(mobile search opens the Contents panel). Use the newer recovery snapshot above
for the complete setup.

## 1. Extract and test without replacing current files

Run from the repository root. This requires Git, uv, and access to PyYAML, either
cached or downloadable. The archive is extracted into a temporary directory.

```sh
snapshot=e235a1efae8617f91291e5e0b85b610b3ba24dbf
preview=$(mktemp -d "${TMPDIR:-/tmp}/manual-okf.XXXXXX")
git archive "$snapshot" \
  .agents/skills/okf \
  .agents/skills/okf-ai-engineering \
  .agents/skills/okf-development | tar -x -C "$preview"

for bundle in \
  "$preview/.agents/skills/okf-ai-engineering/ai-engineering" \
  "$preview/.agents/skills/okf-development/development"; do
  uv run --no-project --with pyyaml python \
    "$preview/.agents/skills/okf/scripts/okf_index.py" "$bundle" || break
  uv run --no-project --with pyyaml python \
    "$preview/.agents/skills/okf/scripts/okf_site.py" "$bundle" || break
done

open "$preview/.agents/skills/okf-ai-engineering/ai-engineering/okf-site.html"
open "$preview/.agents/skills/okf-development/development/okf-site.html"
```

The custom visualizer provides a Markdown reader, hierarchical navigation, search,
type filters, and an interactive graph: concepts are nodes and Markdown cross-links
are edges. It supports mobile navigation and highlights a selected concept's links.
Its HTML embeds the bundle content, but loads Cytoscape.js and marked.js from a CDN;
viewing requires network access unless those libraries are separately vendored.

## 2. Choose the maintained layout

Recommended: keep `wiki/ai-engineering/` and `wiki/software-engineering/` as the
maintained bundles, recover the two Python generators, and make small routing
skills point at those bundles. This preserves the clearer software-engineering
name and avoids maintaining duplicate source copies inside skills.

For an exact historical layout instead, first save current work, then restore only
the three legacy directories:

```sh
git restore --source=e235a1efae8617f91291e5e0b85b610b3ba24dbf --worktree -- \
  .agents/skills/okf \
  .agents/skills/okf-ai-engineering \
  .agents/skills/okf-development
```

This overwrites working-tree files at those paths without changing the index.
Review the result and explicitly stage the intended restoration; previously staged
deletions will otherwise remain staged.

For the recommended layout, restore only `.agents/skills/okf` with the same command,
then adapt the historical routing skills to the current source locations.

## 3. Restore format metadata and preserve newer knowledge

The historical scripts target **OKF 0.1**. Restore that working baseline first;
upgrading to another specification revision is a separate compatibility task.

For each maintained concept:

1. Keep one concept per Markdown file and preserve its current content and citations.
2. Add YAML frontmatter. `type` is required by the indexer; `title` and a short
   `description` make navigation useful. Add `tags` or `resource` when appropriate.
3. Retain relative Markdown links, checking that targets exist within the intended
   bundle. The old renderer supports bundle links; do not assume cross-bundle links
   become edges in a single combined graph.
4. Generate `index.md`; never put unique editorial content in generated indexes.
5. Maintain a concise `log.md` for meaningful editorial changes if retaining the
   historical workflow. Restore bundle-local Markdown lint settings where needed
   for generated headings (the old skill disables MD025 and MD041).

Example frontmatter:

```yaml
---
type: concept
title: Agent runtime
description: Execution lifecycle and boundaries of an agent runtime.
tags: [agents, architecture]
---
```

Do not replace current notes wholesale with the old snapshot. The migration left
58 maintained notes, while the snapshot has 52 concepts. Newer additions include
Jev/CLM coverage, learning resources, simplicity, and format/visualizer comparisons.
Compare by content and topic, and carry those additions and corrections forward.
Recover useful historical metadata without undoing newer source research.

## 4. Generate and visualize the maintained bundles

After restoring metadata and the helper scripts, run from the repository root:

```sh
for bundle in wiki/ai-engineering wiki/software-engineering; do
  uv run --no-project --with pyyaml python \
    .agents/skills/okf/scripts/okf_index.py "$bundle" || break
  uv run --no-project --with pyyaml python \
    .agents/skills/okf/scripts/okf_site.py "$bundle" || break
done

open wiki/ai-engineering/okf-site.html
open wiki/software-engineering/okf-site.html
```

Generation is deterministic Python processing of Markdown and metadata; it uses no
LLM or model tokens. Humans or coding agents research and edit the concepts. The
generators produce catalogs and visualizations, not synthesized knowledge or Claims.

## 5. Reconnect automation selectively

- Add VS Code tasks to regenerate both bundles and open their HTML files. Recover
  historical task examples with `git show <snapshot>:.vscode/tasks.json`, adapting
  bundle paths to the chosen layout.
- Add deterministic pre-commit generation for both bundles with PyYAML available.
  Trigger it when concept files or generator scripts change. Review and stage
  generated changes before committing.
- If fully switching away from OpenWiki, remove its model-backed pre-push hook and
  disable its scheduled update workflow. Remove or clearly label its old tasks.
  Archive generated OpenWiki output if useful; keep the maintained source notes.
- Recover optional static hosting from
  `git show <snapshot>:.github/workflows/pages.yml`, adapting output paths and
  verifying the published entry pages. Local HTML viewing needs no hosting.
- Update agent routing instructions to identify the maintained bundles and generated
  indexes. Review skill installation/lock entries if distributing the routing skills.

In these inspection commands, replace `<snapshot>` with the full recovery hash.
Copy only the relevant configuration entries: restoring entire historical shared
config files would overwrite unrelated improvements made since that snapshot.

## Verification before adopting it

- Both generators complete without warnings and include every intended concept.
  Exit status alone is insufficient: the scripts can warn about missing concepts.
- Every concept has valid metadata, and all intended internal links resolve.
- Each HTML page opens; search, concept selection, type filters, graph links, and
  mobile navigation work. Confirm CDN availability or vendor the libraries.
- A second generation run produces no unexpected diff.
- Tasks and hooks target the chosen maintained paths, and no unintended model-backed
  update remains enabled if the migration is complete.

The historical extraction and generation commands were smoke-tested on 2026-10-03:
both generators exited successfully for both bundles, producing 47 concepts and
144 links for AI engineering, and 5 concepts and 12 links for development, with no
warnings. Browser interaction and a rebuilt current-source layout were not tested.

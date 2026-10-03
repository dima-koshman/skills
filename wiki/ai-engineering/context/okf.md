# Open Knowledge Format (OKF)

Google's vendor-neutral markdown-plus-frontmatter standard for agent-readable knowledge.

Reference: <https://github.com/GoogleCloudPlatform/open-knowledge-format>

Note dated: 2026-09-30 18:00:00+00:00.

OKF represents knowledge — the metadata and curated context around data and
systems — as a directory of markdown files with YAML frontmatter. One concept
per file; the file path is the concept's identity. No schema registry, no
central authority, no required tooling. This very bundle is an OKF bundle.

## Relationship with skills

OKF is *knowledge* (declarative facts), distinct from an agent **skill**
(procedural capability) and from [MCP](mcp.md) (a transport for tools
and resources). An agent could consume an OKF bundle as its knowledge base while
a skill provides the procedure to traverse it and MCP exposes the live tools.

## Upstream v0.2 and the local v0.1 pin

Checked on 2026-09-30: the upstream specification is **v0.2**, while the local
OKF skill's condensed reference is a v0.1 snapshot captured on 2026-07-04 and
the index generator still declares `okf_version: "0.1"`. These bundles retain
that declaration; this review does not constitute a full format migration.

The core remains a directory of Markdown concepts with `type` as the only
always-required field. Reserved `index.md` and `log.md`, cross-linking, and
permissive consumption remain. The new version makes provenance and trust
machine-readable:

| Area | v0.2 convention |
| --- | --- |
| Provenance | `sources` entries with a required `resource` and optional stable `id`; claim footnotes join to those IDs |
| Authorship and freshness | `generated: { by, at }`; optional absolute `stale_after` instant |
| Verification | `verified` events, separate from authorship; consumers derive unverified, machine-confirmed, or human-reviewed trust tiers |
| Lifecycle | `status` of `draft`, `stable`, or `deprecated`; absence means stable |
| Computation | `Attested Computation` concepts with executor, receipt, and deterministic attester conventions |

Despite the minor version number, upstream explicitly calls out two breaking
changes: `timestamp` is superseded by `generated.at`, and body `# Citations`
lists are superseded by frontmatter `sources`. A v0.2 consumer can still consume
v0.1 documents with the documented fallbacks. Our `# Resources` links remain
useful reading links, but do not populate structured provenance automatically.

A local migration should update the pinned reference, authoring skill, and
index version together; migrate known authorship/provenance without inventing
verification events; and check both renderers. Merely changing the version
constant would not teach the current renderer to display v0.2 trust fields.
The [visualizer comparison](okf-visualizers.md) records upstream's
capabilities and the compatibility problems reproduced with these bundles.

## Resources

- [OKF v0.2 specification and v0.1 changelog (§13)](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md)
- [Earlier specification location, also serving v0.2 when checked](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
- [OKF tools directory](https://okf.md/tools/)

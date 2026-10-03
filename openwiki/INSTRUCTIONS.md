# Engineering knowledge base

These preferences supplement OpenWiki's built-in instructions. Use OpenWiki's
default output format and maintenance workflow.

Build a subject-oriented knowledge base from Markdown under `wiki/` only.
`wiki/ai-engineering/` covers AI systems; `wiki/software-engineering/` covers
general software engineering, distributed systems, learning, and reliability.
These are reference notes, not an application whose implementation needs documenting.

## Sources and scope

- Treat `wiki/` as human-maintained source material. Never modify it.
- Ignore all other project files and unrelated Git history as subject matter.
- Source notes are plain Markdown. They do not require OKF frontmatter, generated
  indexes, or maintenance logs; OpenWiki owns the generated knowledge structure.
- Preserve primary-source URLs, qualifications, disagreements, and evidence gaps.
  A claim supported by a local note is not independently verified against its
  external source. Do not imply that linked web pages were fetched when they were not.
- References to "our tooling" or "this bundle" describe the source notes' original
  context; do not present those historical statements as current OpenWiki behavior.

## Generated wiki

- Organize concepts by subject and meaningful relationships rather than one
  output page per input file.
- Preserve accurate curated explanations. Consolidate duplication without losing
  useful distinctions, citations, or caveats.
- Use document-relative Markdown links between generated concepts so the
  OpenWiki visualizer resolves them correctly.
- Keep AI engineering and software engineering discoverable from `quickstart.md`.
- Treat generated pages as derived material, not independent evidence for claims.
- On updates, follow changes in source notes and preserve unrelated accurate content.

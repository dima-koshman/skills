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

## Links and reading resources

- When reusing a relative link, resolve its target from the original source
  file's directory, then calculate a new relative path from the generated
  page's directory. Preserve a fragment only when it exists at the chosen target.
- Link to generated subject pages for synthesized explanations and to actual
  `wiki/` files for source notes. Choose an existing target; the source tree and
  generated tree have different layouts. For example, a Raft source-note link
  from `openwiki/software-engineering/distributed-systems/foundations.md` is
  `../../../wiki/software-engineering/distributed-systems/raft.md`.
- Preserve useful primary-source URLs, selected chapter links, download links,
  and the guidance explaining why to read them. Carry these into the generated
  reading or resources section instead of relying solely on a source-note link.
  Keep distinctions between editions, journal and conference versions, and free
  downloads versus paid access explicit.

## Page verification

- Before submitting each generated page, check local link targets and heading
  fragments from that page's location, including reference-style links. Check
  navigation when pages are created, moved, or regrouped. Local checks do not
  establish that external URLs were fetched or verified.
- Repair the underlying hrefs for any `openwiki: broken internal link` warnings,
  then remove the resolved warning comments. Report unresolved links as defects;
  deleting a warning alone does not fix its target.
- Check changed pages for Markdown errors, including ordered lists interrupted
  by comments, missing blank lines, and unclosed code fences. Run the available
  Markdown linter on the actual changed files; an ignore rule that skips
  `openwiki/` is not a successful check of those files.
- Include link and Markdown checks in the completion audit. State what was
  checked and report failures or unavailable checks explicitly.

## Source coverage

- Before planning an init or an unscoped update, enumerate all Markdown source
  files under `wiki/` and compare them with the generated subject pages. Account
  for each source as substantively covered, needing new or updated coverage, or
  excluded with a specific reason. A source path in frontmatter, a navigation
  link, or a mention in `quickstart.md` alone is not substantive coverage.
- Read sources needing coverage and preserve their distinct concepts, practical
  guidance, trade-offs, primary-source links, and qualifications in generated
  subject pages. Several sources may contribute to one page; create additional
  subject pages when combining them would obscure meaningful distinctions.
- Reading guides and resource lists need coverage too: retain their selection
  guidance, reading order, and useful reference links. Pure navigation maps or
  duplicate notes may be accounted for through existing coverage; explicitly
  identify any exclusions and their reasons in the run summary.
- On updates, check newly added and changed notes as well as older notes that
  remain uncovered. Valid existing Claims and a completed previous run do not
  prove that all source topics are covered. Do not submit an empty or
  quickstart-only plan while substantive coverage gaps remain in scope.
- Put the relevant source paths in each planned page's `seedPaths` and carry its
  coverage, link, and verification requirements into the page job's instructions.
  Update navigation when subject pages are added or regrouped, after their
  content is generated.
- For an explicitly scoped update, apply this audit within the requested scope
  and its affected references. Preserve unrelated coverage and report remaining
  gaps without broadening the requested work.
- Before completing the run, check the resulting pages against the source
  coverage audit. Every in-scope source must have substantive coverage or an
  explicit exclusion reason. Report unresolved gaps as incomplete coverage;
  successful page jobs alone are not evidence of complete source coverage.

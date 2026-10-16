---
type: Practice
title: Monorepo vs Polyrepo
description: Keep many projects in one version-controlled repository, or give each its own — a trade
  between atomic, globally consistent change and independent, loosely coupled ownership.
tags:
- software-engineering
- source-control
parent: /software-engineering/source-control.md
related:
- /software-engineering/reliability/simplicity.md
- /software-engineering/architecture/architectural-patterns.md
- /software-engineering/communication/protobuf.md
sources:
- id: anthropic-scion
  resource: https://www.anthropic.com/engineering/redesigning-source-control
  title: Redesigning source control at Anthropic
  author: Nick G. and the Anthropic source control team
  last_modified: '2026-10-15T00:00:00Z'
- id: google-piper
  resource: https://cacm.acm.org/research/why-google-stores-billions-of-lines-of-code-in-a-single-repository/
  title: Why Google Stores Billions of Lines of Code in a Single Repository (CACM, July 2016)
  author: Rachel Potvin and Josh Levenberg
- id: swe-at-google
  resource: https://abseil.io/resources/swe-book/html/ch16.html
  title: 'Software Engineering at Google, ch. 16: Version Control and Branch Management'
  author: Titus Winters
- id: luu
  resource: https://danluu.com/monorepo/
  title: Advantages of monorepos
  author: Dan Luu
- id: klein
  resource: https://medium.com/@mattklein123/monorepos-please-dont-e9a279be011b
  title: 'Monorepos: Please don''t!'
  author: Matt Klein
- id: meta-sapling
  resource: https://engineering.fb.com/2022/11/15/open-source/sapling-source-control-scalable/
  title: 'Sapling: Source control that''s user-friendly and scalable'
  author: Meta Engineering
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-10-16T13:00:00+04:00'
---

A **monorepo** holds many projects — services, libraries, tools, sometimes
research code — in one repository with one history. A **polyrepo** setup gives
each project or team its own repository and shares code through versioned
packages. A monorepo is a *source-control* decision, not an architecture: a
monorepo can hold a hundred independently deployed microservices, and a
polyrepo can hold a monolith split across library repos.

## Why it surprises people

Most open-source and small-company experience is polyrepo: one GitHub repo per
project, and git itself is designed for that. Yet many of the largest
engineering organizations run monorepos — Google (Piper), Meta
(Mercurial, then Sapling), Microsoft's Windows (git with a virtual filesystem),
Uber, Twitter, and Anthropic. The two worlds rarely meet, so the choice looks
eccentric from outside.

## Anthropic's case (October 2026)

Anthropic describes migrating *its* monorepo off git to an in-house system,
**Scion**, plus a code-review tool, **Antique**.[^anthropic-scion] The post
takes the monorepo as given and does **not** state why they chose it; it
explains what scaling it cost:

| Signal | Figure reported |
| --- | --- |
| Main-branch history | ~100 GB; compressed working copy >25 GB |
| CI checkouts | ~25 million per day; naive fetching ≈ 600 PB/day of git traffic |
| Merged changes | ~2,500/day (May 2026) → >30,000/day (September 2026) |
| Prior workaround | several hundred git mirrors, shallow/sparse/partial clones, blob-storage seeds |
| Result | checkouts in seconds instead of minutes; ~200× smaller CPU/memory footprint than the mirrors |

The core mismatch: git is offline-first and every clone is a full copy, while
nearly all of Anthropic's clients are always-online agents and jobs. Scion is
server-heavy with thin clients, sparse optional working copies, API access
without a local checkout, and cheap lock-free commits. At agent scale a
merge queue with a global lock stops working, so they rely on post-merge and
pre-deploy testing and let Claude fix the resulting conflicts.[^anthropic-scion]

The rationale is not stated, but the usual monorepo arguments below fit an
agent-heavy shop especially well. An agent working in one checkout sees every
caller of an API and can change them all in one commit. With one version of
every internal dependency, there is no compatibility matrix to reason about.
Research and product code share libraries without a release process between
them. *This is inference, not Anthropic's stated reasoning.*

## The trade-off

| Dimension | Monorepo | Polyrepo |
| --- | --- | --- |
| Cross-project change | One atomic commit changes an API and all callers; bisect spans projects[^luu] | Coordinated releases across repos; slower, more deliberate[^klein] |
| Dependency versions | One version of everything (the One-Version Rule); no diamond conflicts[^google-piper][^swe-at-google] | Each repo pins versions; drift and diamond dependencies accumulate |
| Discoverability | Grep/code search over all code by default[^luu] | Needs extra tooling to search or even find repos |
| Ownership and access | Needs path-level ownership (OWNERS files) and directory permissions built on top[^google-piper][^anthropic-scion] | Natural per-repo permissions and team autonomy |
| Coupling | Easy to depend on anything, so unwanted dependencies creep in; needs visibility rules[^google-piper] | Boundaries enforced by package interfaces |
| Build and CI | Needs a dependency-graph build (Bazel/Buck/Nx) to test only what changed | Each repo builds itself; simple until cross-repo integration testing |
| VCS scale | Stock git breaks past some size; requires sparse checkout, virtual FS, or a custom VCS[^google-piper][^meta-sapling][^anthropic-scion] | Stock git and GitHub work unchanged |
| Deploys | Commits are atomic, deploys are not — services still roll out independently[^klein] | Same — deploys are independent anyway |

Two points carry most of the debate:

- **The benefits come from tooling, not the directory layout.** Google built
  Piper, the CitC cloud workspace, Blaze/Bazel, code search, and automated
  large-scale changes (Rosie) to make one repository work for ~25,000
  engineers. A January 2015 snapshot reported ~86 TB, ~2 billion lines, and
  ~35 million commits.[^google-piper] Meta built Sapling, its Mononoke server
  and EdenFS so that operations scale with the files a developer touches, not
  with repository size.[^meta-sapling] Anthropic built Scion.[^anthropic-scion]
  Without that investment a large monorepo is slow and painful.
- **The critique: at scale you need the same tooling either way.** Matt Klein
  (Envoy, Lyft) argues that monorepo advantages fade at scale. Large commits get
  split anyway, deploys are never atomic, and the custom VCS and build
  investment is enormous. Polyrepos keep coupling explicit.[^klein] Dan Luu
  concedes that atomic cross-project commits matter less at very large
  companies.[^luu] Even Google's own book says the monorepo is not the right
  answer for everyone. What it insists on is the One-Version Rule below, which a
  polyrepo setup can also follow.[^swe-at-google]

## The One-Version Rule

> Developers must never have a choice of "What version of this component should
> I depend upon?"[^swe-at-google]

The rule is not about one repository per library. It says every consumer uses
the **same version** of each dependency. If `observability-core` is internal,
every service runs the same release (or the same commit), and no service stays
behind on `0.9.2` while others move to `0.10.1`. It covers third-party packages
too: one checked-in version of each, in the steady state.[^swe-at-google]

| Gain | Cost |
| --- | --- |
| One behavior to reason about and debug across all services | An upgrade touches every consumer at once, so migrations are coupled |
| No diamond dependency, where two libraries need incompatible versions of a third | Whoever ships a breaking change must update or coordinate all callers |
| No long tail of old versions to support and patch | Needs tooling for large-scale changes and strong tests to make that safe |

Version skew does not remove the migration cost; it defers it and spreads it
across teams as debt. Google's book calls version numbers "timestamps":
allowing skew adds a time dimension that is costly to manage. For a dependency
that cannot be upgraded atomically, it recommends adding the new version,
blocking new users of the old one, and migrating incrementally until the old one
is gone.[^swe-at-google] In a monorepo the rule is nearly free, because
consumers depend on the code at head and there is no version to pick. In a
polyrepo it takes enforcement, such as a shared constraints file, automated
upgrade PRs, and a deadline after which old versions fail CI.

## When to choose which

- **Small team, one product, shared code:** a monorepo with stock git is
  cheap and usually the better default. The scaling problems are years away.
- **Many teams, strong platform investment, frequent cross-cutting changes**
  (shared libraries, schemas like [Protocol Buffers](/software-engineering/communication/protobuf.md),
  agent-driven refactors): monorepo, *if* you fund a graph-aware build,
  code ownership, and eventually VCS scaling.
- **Independent products, external contributors, strict access separation,
  or no platform team:** polyrepo. Invest in package publishing, dependency
  update bots, and cross-repo code search instead.
- Either way, judge the total complexity against a concrete requirement — the
  same test [Simplicity](/software-engineering/reliability/simplicity.md) applies to any
  infrastructure choice.

## Resources

- [Redesigning source control at Anthropic](https://www.anthropic.com/engineering/redesigning-source-control)
  (2026) — monorepo scaling under agent-driven merge volume; why git's design stops fitting.
- [Why Google Stores Billions of Lines of Code in a Single Repository](https://cacm.acm.org/research/why-google-stores-billions-of-lines-of-code-in-a-single-repository/)
  (CACM, 2016) — the canonical case, including the costs Google pays.
- [Software Engineering at Google, ch. 16](https://abseil.io/resources/swe-book/html/ch16.html)
  — Titus Winters on the One-Version Rule, trunk-based development, and why the monorepo is optional.
- [Advantages of monorepos](https://danluu.com/monorepo/) — Dan Luu's short case for.
- [Monorepos: Please don't!](https://medium.com/@mattklein123/monorepos-please-dont-e9a279be011b)
  (2019) — Matt Klein's case against.
- [Sapling](https://engineering.fb.com/2022/11/15/open-source/sapling-source-control-scalable/)
  (Meta, 2022) — how Meta scaled its monorepo and what it open-sourced.

[^anthropic-scion]: Redesigning source control at Anthropic (2026)
[^google-piper]: Potvin and Levenberg, CACM, July 2016
[^swe-at-google]: Software Engineering at Google, chapter 16
[^luu]: Dan Luu, Advantages of monorepos
[^klein]: Matt Klein, Monorepos: Please don't! (January 2019)
[^meta-sapling]: Meta Engineering, Sapling (November 2022)

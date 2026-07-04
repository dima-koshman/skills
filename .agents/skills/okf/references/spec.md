# OKF v0.1 — condensed reference

> **Pinned snapshot of OKF v0.1, captured 2026-07-04.** Authoritative source:
> <https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md>.
> This is a deliberate snapshot, kept in sync with the `OKF_VERSION` constant in
> `scripts/okf_index.py`. Reconcile with upstream per the SKILL.md
> "Keeping current with the spec" section — don't edit it to match a newer
> upstream revision without also bumping the script and the skill together.

Condensed from the official [Open Knowledge Format specification](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
(v0.1 Draft). This is a working summary for authoring and consuming bundles;
the linked SPEC.md is authoritative if the two ever disagree.

OKF represents *knowledge* — the metadata, context, and curated insight around
data and systems — as **a directory of markdown files with YAML frontmatter**.
No schema registry, no central authority, no required tooling. "If you can
`cat` a file, you can read OKF; if you can `git clone` a repo, you can ship it."

Design goals: **readable** by humans without tooling, **parseable** by agents
without bespoke SDKs, **diffable** in version control, **portable** across tools
and time.

## Bundle structure (§3)

A bundle is a directory tree of markdown files. Each concept is one file; the
file path is the concept's identity.

```
my_bundle/
├── index.md              # Optional. Directory listing for progressive disclosure.
├── log.md                # Optional. Chronological history of updates.
├── datasets/
│   ├── index.md
│   └── sales.md
└── tables/
    ├── index.md
    ├── orders.md
    └── customers.md
```

### Reserved filenames (§3.1)

| Filename    | Meaning                                     |
|-------------|---------------------------------------------|
| `index.md`  | Directory listing (see §6).                 |
| `log.md`    | Update history (see §7).                    |

All other `.md` files are **concept documents**.

## Concept documents (§4)

Each concept is a UTF-8 markdown file with two parts: a YAML frontmatter block
delimited by `---` lines, then a free-form markdown body.

### Frontmatter (§4.1)

```yaml
---
type: <Type name>                  # REQUIRED
title: <display name>              # Recommended
description: <one-line summary>    # Recommended
resource: <canonical URI>          # Recommended (omit for abstract concepts)
tags: [<tag>, <tag>]               # Optional
timestamp: <ISO 8601 datetime>     # Optional — last meaningful change
# … any producer-defined key/value pairs
---
```

- **`type`** is the *only* required field. Short string identifying the kind of
  concept — used for routing, filtering, presentation. Examples: `BigQuery
  Table`, `BigQuery Dataset`, `API Endpoint`, `Metric`, `Playbook`, `Reference`.
  Types are **not** registered centrally; pick descriptive, self-explanatory
  values. Consumers must tolerate unknown types (treat as generic concepts).
- Recommended fields, in priority order: `title`, `description`, `resource`,
  `tags`, `timestamp`.
- **Extensions:** producers may add any keys; consumers should preserve unknown
  keys when round-tripping and must not reject documents with unrecognized fields.

### Body (§4.2)

Standard markdown. Favor structural markdown (headings, lists, tables, fenced
code) over freeform prose — structure aids both human reading and agent
retrieval. No required sections. Conventional headings, used when applicable:

| Heading       | Purpose                                              |
|---------------|------------------------------------------------------|
| `# Schema`    | Structured description of an asset's columns/fields. |
| `# Examples`  | Concrete usage examples, often fenced code blocks.   |
| `# Citations` | External sources backing body claims (see §8).       |

### Example concept (§4.3)

```markdown
---
type: BigQuery Table
title: Customer Orders
description: One row per completed customer order across all channels.
resource: https://console.cloud.google.com/bigquery?p=acme&d=sales&t=orders
tags: [sales, orders, revenue]
timestamp: 2026-05-28T14:30:00Z
---

# Schema

| Column        | Type      | Description                                         |
|---------------|-----------|-----------------------------------------------------|
| `order_id`    | STRING    | Globally unique order identifier.                   |
| `customer_id` | STRING    | Foreign key into [customers](/tables/customers.md). |
| `total_usd`   | NUMERIC   | Order total in US dollars.                          |

# Joins

Joined with [customers](/tables/customers.md) on `customer_id`.

# Citations

[1] [BigQuery table schema](https://console.cloud.google.com/bigquery?p=acme&d=sales&t=orders)
```

## Cross-linking (§5)

Concepts link to each other with standard markdown links, in two forms:

- **Absolute (bundle-relative)** — begins with `/`, interpreted from the bundle
  root: `[customers](/tables/customers.md)`. **Recommended** — stable when a
  document moves within its subdirectory.
- **Relative** — standard relative paths: `[neighbor](./other.md)`.

A link asserts an *untyped relationship*; the *kind* of relationship
(parent/child, references, joins-with, depends-on) is conveyed by surrounding
prose, not the link. Consumers **must tolerate broken links** — a link to a
target that doesn't exist is not malformed; it may be not-yet-written knowledge.

## Index files (§6)

An `index.md` MAY appear in any directory (including the root) to enumerate that
directory's contents for **progressive disclosure**. Index files contain **no
frontmatter** (the one exception: the bundle-root index may declare
`okf_version` — see §11). The body is one or more grouped sections:

```markdown
# Section / Group Heading

* [Title 1](relative-url-1) - short description of item 1
* [Title 2](relative-url-2) - short description of item 2

# Another Section

* [Subdirectory](subdir/) - short description of the subdirectory
```

Entries should reuse the `description` from the linked concept's frontmatter.
Producers may generate `index.md` automatically; consumers may synthesize one on
the fly when none is present.

## Log files (§7)

A `log.md` MAY appear at any level to record the history of changes to that
scope. A flat list of ISO-8601 date-grouped entries, **newest first**:

```markdown
# Directory Update Log

## 2026-05-22
* **Update**: Added new BigQuery table reference for [Customer Metrics](/tables/customer-metrics.md).
* **Creation**: Established the [Dataplex Playbook](/playbooks/dataplex.md).

## 2026-05-15
* **Initialization**: Created foundational directory structure.
```

Date headings **must** use `YYYY-MM-DD`. Entries are prose; the leading bold word
(`**Update**`, `**Creation**`, `**Deprecation**`, `**Initialization**`, …) is a
convention, not a requirement.

## Citations (§8)

Sources for claims in a body should be listed under a `# Citations` heading at the
bottom of the document, numbered. Links may be absolute URLs, bundle-relative
paths, or paths into a `references/` subdirectory that mirrors external material
as first-class OKF concepts.

## Conformance (§9)

A bundle is conformant with OKF v0.1 if:

1. Every non-reserved `.md` file contains a parseable YAML frontmatter block.
2. Every frontmatter block has a non-empty `type` field.
3. Reserved filenames (`index.md`, `log.md`) follow §6 / §7 when present.

**Permissive consumption** — consumers must NOT reject a bundle for: missing
optional frontmatter fields, unknown `type` values, unknown extra frontmatter
keys, broken cross-links, or missing `index.md` files.

## Versioning (§11)

Versioned `<major>.<minor>`. A **minor** bump adds backward-compatible things
(new optional fields, new conventional headings). A **major** bump may break
(renaming required fields, changing reserved filenames). A bundle may declare its
target version with `okf_version: "0.1"` in the **bundle-root `index.md`
frontmatter** — the only place frontmatter is permitted in an `index.md`.
Consumers that don't understand a declared version should attempt best-effort
consumption rather than refusing the bundle.

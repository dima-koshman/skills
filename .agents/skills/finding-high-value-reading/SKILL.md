---
name: finding-high-value-reading
description: Use when Dima asks what to read, learn or follow on a topic — engineering blog posts, papers, talks, postmortems, newsletters, "lessons learned", "why did company X decide Y", industry best practices, news worth knowing, trending or "repo of the day" GitHub repositories, or "what don't I know that I don't know" about something he is working on. Finds a short, verified list of high-signal resources (old or new) matched to his reader profile and the OKF wiki at ~/Projects/dima/wiki, and offers to capture the best ones into it.
---

# Finding High-Value Reading

## Overview

The goal is to surface **unknown unknowns**: the reasoning, trade-offs and lessons that
practitioners at strong engineering organizations take for granted but that rarely reach
tutorials. One post like Anthropic's monorepo/Scion write-up is worth more than ten
how-to articles, because it shows *a decision, its cost, and the alternative rejected*.

Core principle: **recommend only what you fetched this turn.** Titles, authors, URLs
and dates from memory are often wrong. A plausible-looking dead link wastes the reader's
trust. Every item you list must have been opened and checked.

Recency is not the criterion. A 2016 paper that explains *why* beats a 2026 news item
that only says *what*.

## Workflow

### 1. Ground the interest in the reader profile and the wiki

Read `references/interests.md` first: current focus, how deep he wants to go, and
what to filter out. When he states a new interest, depth preference or dismissal
during the session, update that file with the date.

The wiki at `~/Projects/dima/wiki` (an OKF v0.2 bundle, see the `okf` skill) is the
record of what Dima knows and is studying.

- If the topic is explicit, find the matching concepts:
  `grep -ril "<topic>" ~/Projects/dima/wiki --include=*.md`.
- If the topic is vague ("what should I read?"), read the newest entries in
  `~/Projects/dima/wiki/log.md` and the area list in `~/Projects/dima/wiki/index.md`.
  Recent additions are the current interest.
- Collect what is **already known**, so you don't recommend it again:
  `grep -rhoE "https?://[^ )>\"']+" ~/Projects/dima/wiki --include=*.md | sort -u`.
- Note **gaps**: a concept with only one side of a debate, no primary source, no
  lessons from real use, or a passed `stale_after`. A gap is the best thing to fill.

### 2. Search for decisions, not definitions

Run several searches in one turn. Phrase queries the way practitioners title the
posts that carry reasoning:

| Want | Query patterns |
| --- | --- |
| Decision rationale | `"why we" <topic>`, `"we moved from" <x>`, `"we chose" <x> over`, `<company> engineering <topic>` |
| Lessons learned | `<topic> "lessons learned"`, `"in retrospect"`, `"what we got wrong"`, `<topic> at scale` |
| Failures | `<topic> postmortem`, `<topic> outage "root cause"`, `"considered harmful"` |
| The other side | `"against" <topic>`, `<topic> "please don't"`, `<topic> criticism` |
| Canonical / evergreen | `<topic> paper`, `<topic> site:queue.acm.org`, `<topic> site:usenix.org` |
| Community-vetted | `hn.algolia.com/?q=<topic>&sort=byPopularity` (old classics surface here) |

Start from the curated list in `references/sources.md`, matched to the topic.
Follow citations: the best post on a topic usually links the two or three that
shaped it.

### 3. Verify and rank

Fetch every candidate. Keep it only if it exists, is substantive, and you can state
its author and date. Rank on:

1. **Primary**: written by the people who built or decided the thing.
2. **Reasoning**: states the trade-off, the alternatives rejected, and numbers.
3. **Honesty about cost**: says what went wrong or what it cost.
4. **Durability**: principles that outlive the tool version.
5. **Counterweight**: for every strong claim, include the best opposing view.
6. **Depth fit**: match the depth preference in `interests.md`. Hold back
   implementation deep-dives unless he asked for them.

Drop SEO explainers, vendor listicles, and AI-generated "X vs Y" pages. A secondhand
summary is acceptable only when the primary source is unreachable, and must be labeled
as secondhand.

### 4. Present a short list

5-10 items, grouped by what they teach (for example *decision rationale*, *lessons /
postmortems*, *counterpoint*, *foundations*). For each item:

- **[Title](url)**: author/org, date, rough length or format.
- One line on **what is surprising or non-obvious** in it, and why it matters for the
  current interest.

Mark anything already in the wiki, and say where the topic has a gap the list does
not fill. When the question is also "where should I look in general", point to the
relevant groups of `references/sources.md` rather than pasting the whole list.

### 5. Offer to capture into the wiki

The wiki is where reading turns into knowledge. Offer to capture the items Dima found
valuable, using the `okf` skill:

- Add to an existing concept's `sources` with a **meaningful, stable `id`** (`google-piper`,
  not `ref-1`). Cite claims in the body with `[^id]` footnotes. An id nothing cites is
  noise in the reader.
- Or create a concept (`type: Practice`/`Concept`, or `Reference` for a reading
  note) under the matching area. Then regenerate `index.md`, add a `log.md` entry,
  and re-render the site. The `okf` skill covers each step.

## Trending repositories

For "repo of the day", "what's trending" or "new tools in X":

1. Fetch [GitHub Trending](https://github.com/trending?since=daily), plus the
   language pages that match the profile (`/trending/python`, `/trending/mojo`).
   Use `since=weekly` when daily is noisy or the request isn't time-sensitive.
2. Filter against `interests.md`: keep repos about AI and agents, developer
   tooling, GPU and compute, infrastructure, or a current focus topic. Drop
   awesome-lists, course dumps, crypto, and anything in *Not interested*.
3. Open each survivor's README. Keep it only if you can say what it does and why
   it is gaining attention: a new capability, a notable author or org, or a
   cheaper or faster alternative to something known.
4. Report 3-5 repos: **[owner/name](url)**, the stars gained in the period, and one
   line on why it matters to him. Say plainly if nothing relevant trended today.

Stars measure attention, not quality. A repo can trend because of one viral post.

## Common mistakes

- Listing well-known names from memory without fetching: the URL is wrong, or the post
  says something else.
- Optimizing for new: a "latest news" list rarely contains unknown unknowns.
- One-sided lists: a monorepo reading list with no Matt Klein is advocacy, not learning.
- Dumping 30 links: the value is in the selection and the one-line "why".

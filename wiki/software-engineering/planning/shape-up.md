---
type: Reference
title: Shape Up
aliases:
- Appetite vs Estimate
- Fixed Time, Variable Scope
description: Ryan Singer's book on Basecamp's product process; its core idea is the appetite, a fixed time budget
  with variable scope, set before the solution is designed.
tags:
- software-engineering
- planning
resource: https://basecamp.com/shapeup
parent: /software-engineering/planning.md
related:
- /software-engineering/planning/shaping.md
- /software-engineering/planning/responding-to-raw-ideas.md
- /software-engineering/planning/betting-and-building.md
status: draft
sources:
- id: shapeup
  resource: https://basecamp.com/shapeup
  title: 'Shape Up: Stop Running in Circles and Ship Work that Matters'
  author: Ryan Singer
- id: shapeup-ch3
  resource: https://basecamp.com/shapeup/1.2-chapter-03
  title: 'Chapter 3: Set Boundaries'
  author: Ryan Singer
- id: shapeup-ch8
  resource: https://basecamp.com/shapeup/2.2-chapter-08
  title: 'Chapter 8: The Betting Table'
  author: Ryan Singer
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-17T12:00:00+04:00'
---

Shape Up is Basecamp's product development process, free to read online.[^shapeup] Work is shaped before it is
committed to, then built by a small team in a fixed cycle. The shaping steps and the pitch are in
[Shaping Work Before the Pitch](/software-engineering/planning/shaping.md). The idea worth keeping even without the rest of the process
is the **appetite**.

# Appetite vs estimate

> "Estimates start with a design and end with a number. Appetites start with a number and end with a design."[^shapeup-ch3]

| | Estimate | Appetite |
| --- | --- | --- |
| Fixed | Scope (the design) | Time |
| Variable | Time (the number) | Scope |
| Question | "How long will this take?" | "How much is this problem worth to us?" |
| Kind of statement | A forecast about the work | A value judgment about the problem |

An estimate does not fix time and scope by itself. The trap comes when the estimate becomes a deadline: scope,
date and an optimistic number are then all fixed, and the slack comes out of quality or overtime.

Chapter 3 ("Set Boundaries") also argues:[^shapeup-ch3]

- **Sizes.** A small batch is 1–2 weeks for one designer and one or two programmers. A big batch is the same team for
  six weeks. Work too big for six weeks gets narrowed or split.
- **"Good" is relative.** Without a time limit there is always a better version, so the appetite is what makes "good
  enough" definable.
- **The appetite constrains twice:** once while shaping the design, and again while building, where the fixed time
  forces the choice between core and peripheral scope.
- **Narrow the problem.** Ask "what's really going wrong?" instead of "what could we build?". In the book's example, a
  one-day warning replaced a six-week permissions project.
- **Grab-bags are not projects.** "Redesign X" or anything called "2.0" should be split into problems, each with its
  own appetite.
- **Raw ideas get a soft no.** The default answer is "Interesting. Maybe some day.", not a backlog entry. See
  [Responding to Raw Ideas](/software-engineering/planning/responding-to-raw-ideas.md).

The companion rule is the **circuit breaker**: a project that does not ship in its cycle is cancelled by default, not
extended.[^shapeup-ch8] Cycles are six weeks, followed by a two-week cool-down with no scheduled work.[^shapeup-ch8]
Those rules and the rest of parts 2 and 3 (betting, whole projects, scopes, the hill chart, QA) are in
[Betting and Building in Cycles](/software-engineering/planning/betting-and-building.md).

# Trade-offs

These are our own analysis, not claims from the book.

## Pros

- The date is certain by design: something ships on time, so there is no "90% done for a month".
- "What is core?" gets decided early and repeatedly, not discovered at the deadline.
- Suits uncertain work that cannot be estimated honestly: research, ML model quality, UX.
- Stops gold-plating.
- Caps the downside at one appetite's worth of time.

## Cons

- Needs scope that can really be cut. Compliance, security fixes, contractual work and migrations often have fixed
  scope.
- Someone with authority must make cut decisions, against a well-shaped pitch. Shaping costs senior time.
- "Variable scope" can become cover for under-delivering, or teams cut quality instead of scope.
- The circuit breaker is emotionally and politically hard to honor.
- Assumes uninterrupted time and a team that controls the whole project. On-call load and waiting on other teams
  break both.

# When to use which

| Work | Better fit |
| --- | --- |
| Vague goals, new features, product bets | Appetite |
| Research, model or quality tuning | Appetite (fix time, take the best result) |
| Security and compliance fixes | Estimate (scope is not negotiable) |
| Upgrades and migrations with known steps | Estimate (checklist) |
| Incidents and interrupts | Neither: a separate reserved capacity or rotation |

The appetite can be adopted without the rest of Shape Up (six-week cycles, betting table, cool-down), for example
inside two-week sprints:

1. Give each story an appetite (one sprint or two) and a list of what is out of scope.
2. Decide what to cut at the midpoint, not at the end.
3. No rollover by default: work that did not fit is reshaped as a new bet.
4. Keep estimates for fixed-scope work. Protect appetites from interrupts with a rotating on-call person rather than a
   share of everyone's time.
5. Start external dependencies (approvals, other teams' queues) before the appetite clock starts, or shape them out
   of scope.

A time-boxed spike that must end in a written decision is already an appetite.

[^shapeup]: Ryan Singer, *Shape Up*, basecamp.com/shapeup.
[^shapeup-ch3]: Chapter 3, "Set Boundaries".
[^shapeup-ch8]: Chapter 8, "The Betting Table".

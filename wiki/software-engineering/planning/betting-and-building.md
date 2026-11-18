---
type: Practice
title: Betting and Building in Cycles
aliases:
- Betting Table
- Cool-Down
- Circuit Breaker
- Assign Projects, Not Tasks
- Scopes
- Hill Chart
- Imagined vs Discovered Tasks
description: Parts 2 and 3 of Shape Up, reduced to the ideas worth reusing. Longer cycles with a cool-down,
  a clean slate, bets instead of plans, whole projects handed to a team, scopes cut by structure, to-do
  lists that grow before they shrink, the circuit breaker, and QA for the edges.
tags:
- software-engineering
- planning
parent: /software-engineering/planning.md
related:
- /software-engineering/planning/shape-up.md
- /software-engineering/planning/shaping.md
- /software-engineering/architecture.md
status: draft
sources:
- id: shapeup-ch7
  resource: https://basecamp.com/shapeup/2.1-chapter-07
  title: 'Chapter 7: Bets, Not Backlogs'
  author: Ryan Singer
- id: shapeup-ch8
  resource: https://basecamp.com/shapeup/2.2-chapter-08
  title: 'Chapter 8: The Betting Table'
  author: Ryan Singer
- id: shapeup-ch10
  resource: https://basecamp.com/shapeup/3.1-chapter-10
  title: 'Chapter 10: Hand Over Responsibility'
  author: Ryan Singer
- id: shapeup-ch12
  resource: https://basecamp.com/shapeup/3.3-chapter-12
  title: 'Chapter 12: Map the Scopes'
  author: Ryan Singer
- id: shapeup-ch13
  resource: https://basecamp.com/shapeup/3.4-chapter-13
  title: 'Chapter 13: Show Progress'
  author: Ryan Singer
- id: shapeup-ch14
  resource: https://basecamp.com/shapeup/3.5-chapter-14
  title: 'Chapter 14: Decide When to Stop'
  author: Ryan Singer
- id: humphrey-2007
  resource: https://doi.org/10.1037/0021-9010.92.5.1332
  title: 'Integrating motivational, social, and contextual work design features: a meta-analytic summary and
    theoretical extension of the work design literature'
  author: Stephen E. Humphrey, Jennifer D. Nahrgang, Frederick P. Morgeson
- id: nagappan-2008
  resource: https://www.cs.umd.edu/users/basili/publications/proceedings/P125.pdf
  title: 'The Influence of Organizational Structure on Software Quality: An Empirical Case Study'
  author: Nachiappan Nagappan, Brendan Murphy, Victor R. Basili
- id: dora-loosely-coupled
  resource: https://dora.dev/capabilities/loosely-coupled-teams/
  title: 'Capabilities: Loosely coupled teams'
  author: DORA
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-18T16:25:00+04:00'
---

Part 2 of [Shape Up](/software-engineering/planning/shape-up.md) is about choosing what to build each cycle, and
part 3 is about how a team builds it. Most of part 2 is written for whoever runs the company's product process. This
concept keeps the ideas that work at any size. Sections marked "our take" are our own analysis, not the book's.

# Cycles and cool-down

- **Longer cycles.** Basecamp works in six-week cycles. The book calls two-week sprints "too short to get anything
  meaningful done" and costly in planning overhead. Six weeks is "long enough to finish something meaningful and
  still short enough to see the end from the beginning."[^shapeup-ch8]
- **Cool-down.** Each cycle is followed by two weeks with no scheduled work. People fix bugs, explore ideas and try
  new technical options, and the next cycle is decided then, not in the rush at the end of a cycle.[^shapeup-ch8]
- **Bugs wait for cool-down.** Only a real crisis interrupts a cycle, such as data loss or the app grinding to a halt.
  Other bugs go to cool-down. A bug too big for cool-down is pitched at the betting table like any other project.
  Once a year, a whole cycle is a "bug smash".[^shapeup-ch8]
- **Clean slate.** Bet one cycle at a time, and "never carry scraps of old work over without first shaping and
  considering them as a new potential bet." Work that needs two cycles is still bet one cycle at a time, each with a
  working result at its end.[^shapeup-ch8]

**Our take.** Six weeks suits Basecamp, and may not suit a team with frequent interrupts or outside deadlines. The
point is that the sprint length is a choice. Pick the shortest cycle in which a whole piece of work can ship.
Cool-down is the part that carries over best. Bug fixes and unscoped work get a protected slot instead of
interrupting planned work, and the gap gives time to decide what's next.

# Betting versus planning

The book admits the difference is mostly in expectations: "We talk about 'betting' instead of planning because it
sets different expectations."[^shapeup-ch8] A bet has three properties:

| Property | Meaning |
| --- | --- |
| A payout | The pitch is shaped so that something meaningful is finished at the end. The cycle isn't a box filled with tasks. |
| A commitment | The team gets the whole cycle, uninterrupted. "Losing the wrong hour can kill a day. Losing a day can kill a week." |
| A capped downside | A six-week bet can lose at most six weeks (the circuit breaker below). |

Around the bet, the book sets these rules:[^shapeup-ch7][^shapeup-ch8]

- **No backlog.** Only a few pitches are considered: ones shaped in the last cycle, plus older ones someone chose to
  revive. Pitches that aren't picked are let go, and anyone who still wants one tracks it themselves. "Really
  important ideas will come back to you."
- **Final decision.** The people at the betting table can commit the time. At Basecamp they are the CEO, the CTO, a
  senior programmer and the product strategist. Nobody approves the plan afterwards, and nobody interrupts it.

**Our take.** It is pitch-based planning, and calling it that loses nothing. Planning on shaped pitches, one cycle
ahead, gives the same results when it keeps the same rules:

| | Typical sprint planning | Betting |
| --- | --- | --- |
| Input | A backlog of tickets | A few shaped pitches |
| Sized by | Estimates and velocity | Appetite |
| Who splits it into tasks | Usually done before the sprint | The team, during the cycle |
| Unfinished work | Rolls over | Cancelled by default; reshaped if still wanted |
| Interrupts | Absorbed by the sprint | Not allowed, except a real crisis |

# The circuit breaker

"If they don't finish, by default the project doesn't get an extension."[^shapeup-ch8] The book gives three reasons:

1. No runaway projects. A project that was worth six weeks isn't worth two, three or ten times that.
2. Missing the deadline signals a shaping problem. The fix is to reshape the problem, not to spend more time on the
   same approach.
3. Teams own the scope. A hard deadline makes them keep asking what to cut.

A project is extended only in rare cases. The remaining tasks must be real must-haves, and all the remaining work
must be "downhill" (no open questions; see the hill below). Uphill work at the deadline means a hole in the shaping,
and the project goes back to shaping.[^shapeup-ch14]

# Hand over whole projects, not tasks

The team receives the whole pitch and defines its own tasks. "Splitting the project into tasks up front is like
putting the pitch through a paper shredder."[^shapeup-ch10] The book gives two reasons:[^shapeup-ch10]

- **Engagement.** "Talented people don't like being treated like 'code monkeys' or ticket takers."
- **A better whole.** Nobody can predict at the start what all the pieces need in order to fit. People doing the work
  see missing pieces. People given only tasks don't feel responsible for how the pieces fit together.

This is autonomy inside limits. The shaping already set the boundaries, and the team fills in the outline.

## Is it backed by research?

**Our take.** In part. The evidence supports autonomy and whole work in general. It doesn't test this practice, and
it doesn't show better products.

- **Autonomy and whole work.** The job characteristics model (Hackman and Oldham) names "task identity" (doing a
  whole, identifiable piece of work) and autonomy among the features that make work motivating. A meta-analysis of
  259 studies and about 219,000 people found autonomy to be one of the two strongest predictors of job satisfaction,
  and it was also linked to better performance and less exhaustion.[^humphrey-2007] Most of these studies are
  correlational and rely on self-reports.
- **Software delivery.** DORA's research finds that teams who can test, deploy and change their systems without
  depending on other teams deliver better.[^dora-loosely-coupled] This is about not waiting on others, not about
  motivation, but it points the same way.
- **What is not shown.** That "projects turn out better" is Basecamp's experience. Autonomy also needs shaped work and
  a capable team. Handing a vague project to a junior team isn't the same practice.

# Scopes: split by structure, not by role

Inside the team, the book warns against lists per role (a designer's list, a programmer's list). People complete
their tasks, but the tasks don't add up to a finished part of the project early enough.[^shapeup-ch12] Instead the
project is split into **scopes**: parts of the problem that can be finished on their own in a few days, each
including its front-end and back-end work. The book's example outside software: an event organizer tracks Food
Menu, Venue Setup and Light/Sound, not one list per volunteer, so the organizer can see which areas are
done.[^shapeup-ch12]

Why structure works better:[^shapeup-ch12]

- **"Done" means something.** A finished scope is working software. Finished role tasks are pieces that, "fingers
  crossed", come together at the end.
- **Status is visible.** You can see what's done and what isn't for the project as a whole.
- **Scopes become the language of the project.** "After Bucket Access is done we can implement Invite Clients."
- **New tasks have a home.** That includes bugs, which go into the scope they affect, not a "bugs" list.

Scopes are discovered, not planned. They show up after the first week of real work, when the team can see how the
parts depend on each other. Signs a scope is wrong: it's hard to say how done it is, its name is generic
("front-end", "bugs"), or it's too big to finish soon.[^shapeup-ch12]

**Our take.** The book is about roles inside one team, not about splitting work between teams. The same reasoning
applies there, though. Cutting a project along team boundaries (an API team, a UI team) is the role split at a larger
scale, with the integration risk at the end. Conway's law says systems tend to copy the structure of the
organizations that build them. On Windows Vista, measures of organizational structure predicted which binaries would
fail.[^nagappan-2008] Prefer slices that one team can finish end to end, and use DORA's "inverse Conway maneuver"
(shape the teams to match the architecture you want).[^dora-loosely-coupled]

# To-do lists grow before they shrink

- **Imagined and discovered tasks.** The team starts with tasks it imagines from the pitch. The tasks it discovers by
  doing real work "make up the true bulk of the project and sometimes present the hardest
  challenges."[^shapeup-ch10] So "to-do lists actually grow as the team makes progress", and counting open tasks
  can't tell you how far along a project is.[^shapeup-ch13]
- **Estimates hide uncertainty.** Two tasks estimated at four hours can mean very different things. One has been done
  ten times; the other has never been done and might take three days.[^shapeup-ch13]
- **Work is a hill.** Going uphill is figuring out the approach. Downhill is execution, once all the work is visible.
  Each scope is placed on a hill chart. A dot that doesn't move is "effectively a raised hand". Uphill is only
  finished when it's built, not just thought through: "I've thought about this", then "I've validated my approach",
  then "I don't believe there are other unknowns".[^shapeup-ch13]
- **Scariest first.** Push the most unknown, most important scopes uphill first, and leave routine work for the end,
  when it can be done quickly or cut.[^shapeup-ch13]

**Our take.** The conclusion depends on what is fixed. With estimates (fixed scope), budget more time the more
unknowns the task has: give a range instead of one number, and widen it for work the team hasn't done before. Shape
Up, which fixes time, doesn't add time for uncertainty. It removes the unknowns while shaping, solves the unknowns
that remain first, and cuts scope at the end. Both rest on the same observation: work with unknowns isn't half done
when half its tasks are checked off.

# Scope hammering and QA

- **Compare to the baseline, not the ideal.** Ask whether the work is better than what customers have now, not whether
  it is perfect.[^shapeup-ch14]
- **Scope grows like grass**, through no one's fault. Teams get the authority to keep cutting it. Nice-to-haves are
  marked with `~` and usually never get built. "Cutting scope isn't lowering quality": it is choosing what the product
  is good at.[^shapeup-ch14]
- **QA is for the edges.** Programmers write their own tests and the team owns basic quality, so the single QA
  person looks for edge cases outside the core. QA is "a level-up, not a gate". Its findings are nice-to-haves until
  the team promotes one to a must-have.[^shapeup-ch14]
- Basecamp treats **code review** the same way: useful when there is time, not a required step.[^shapeup-ch14]

**Our take.** "QA for the edges" works only because the team tests the core itself. Without that, QA becomes the
gate it was meant not to be. Required code review, as in regulated environments, is a constraint the book doesn't
have.

[^shapeup-ch7]: Chapter 7, "Bets, Not Backlogs".
[^shapeup-ch8]: Chapter 8, "The Betting Table".
[^shapeup-ch10]: Chapter 10, "Hand Over Responsibility".
[^shapeup-ch12]: Chapter 12, "Map the Scopes".
[^shapeup-ch13]: Chapter 13, "Show Progress".
[^shapeup-ch14]: Chapter 14, "Decide When to Stop".
[^humphrey-2007]: Humphrey, Nahrgang and Morgeson, *Journal of Applied Psychology* 92(5), 2007.
[^nagappan-2008]: Nagappan, Murphy and Basili, ICSE 2008.
[^dora-loosely-coupled]: DORA, "Loosely coupled teams" capability.

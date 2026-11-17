---
type: Practice
title: Shaping Work Before the Pitch
aliases:
- Shaping
- Scoping an Idea
- Pitch
description: The steps that turn a raw idea into a pitch, following Shape Up. Narrow the problem, set an appetite,
  rough out the solution, find rabbit holes, then check it with experts while it is still easy to change.
tags:
- software-engineering
- planning
parent: /software-engineering/planning.md
related:
- /software-engineering/planning/shape-up.md
- /software-engineering/planning/responding-to-raw-ideas.md
status: draft
sources:
- id: shapeup-ch2
  resource: https://basecamp.com/shapeup/1.1-chapter-02
  title: 'Chapter 2: Principles of Shaping'
  author: Ryan Singer
- id: shapeup-ch3
  resource: https://basecamp.com/shapeup/1.2-chapter-03
  title: 'Chapter 3: Set Boundaries'
  author: Ryan Singer
- id: shapeup-ch4
  resource: https://basecamp.com/shapeup/1.3-chapter-04
  title: 'Chapter 4: Find the Elements'
  author: Ryan Singer
- id: shapeup-ch5
  resource: https://basecamp.com/shapeup/1.4-chapter-05
  title: 'Chapter 5: Risks and Rabbit Holes'
  author: Ryan Singer
- id: shapeup-ch6
  resource: https://basecamp.com/shapeup/1.5-chapter-06
  title: 'Chapter 6: Write the Pitch'
  author: Ryan Singer
- id: shapeup-glossary
  resource: https://basecamp.com/shapeup/4.5-appendix-06
  title: Glossary
  author: Ryan Singer
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-17T18:05:00+04:00'
---

Shaping is the work done on an idea before anyone commits to building it. It ends with a pitch. This concept follows
part 1 of [Shape Up](/software-engineering/planning/shape-up.md). Sections marked as our own analysis are not from
the book.

# Definitions

- **Pitch:** "A document that presents a shaped project idea for consideration at the betting table."[^shapeup-glossary]
  Chapter 6 adds: "The purpose of the pitch is to present a good potential bet."[^shapeup-ch6]
- **Shape:** "Make an abstract project idea more concrete by defining key elements of the solution before betting on
  it."[^shapeup-glossary]
- **Raw ideas:** "Requests or feature ideas that are expressed in words and haven't been shaped."[^shapeup-glossary]
- **Rabbit hole:** "Part of a project that is too unknown, complex, or open-ended to bet on."[^shapeup-glossary]

# What shaped work looks like

Shaped work has three properties:[^shapeup-ch2]

| Property | Meaning |
| --- | --- |
| Rough | It looks unfinished on purpose, so the people who build it still have room to design. |
| Solved | The main elements of the solution are worked out and connect together. |
| Bounded | It has an appetite and says what *not* to do: "It tells the team where to stop." |

The hard part is the level of abstraction: "not too vague and not too concrete."[^shapeup-ch2] Wireframes or
mockups made too early "define too much detail too early" and leave designers no room. A project described in a few
words gives the team too little to make trade-offs with.[^shapeup-ch2]

In the book, shaping is done in private by a small group: "Shaping is a closed-door, creative process."[^shapeup-ch2]
The wider team sees it only after a bet is made.

# Steps before the pitch

The book lists four steps: set boundaries, rough out the elements, address risks and rabbit holes, and write the
pitch.[^shapeup-ch2] Talking to experts is part of step 3.

## 1. Set boundaries

- **Set an appetite.** Decide how much time the problem is worth before designing anything. "You can think of the
  appetite as a time budget for a standard team size."[^shapeup-ch3]
- **Narrow the problem.** Don't take the request at face value. Ask "What's really going wrong?" instead of "What
  could we build?"[^shapeup-ch3] In the book's calendar example, the real need was smaller than the request.
- **Split grab-bags.** "Redesign X" or "2.0" is a list of problems, and each one needs its own appetite.[^shapeup-ch3]

## 2. Rough out the elements

- Work fast and stay rough. Use **breadboards** (places, affordances and the connections between them, all as words)
  for flows, and **fat marker sketches** when the layout is the real problem.[^shapeup-ch4]
- Don't make a spec: "It's more like the boundaries and rules of a game."[^shapeup-ch4] Specific mockups bias whoever
  builds it later, so keeping it rough "leaves this important room for creativity in the later stages."[^shapeup-ch4]

## 3. Address risks and rabbit holes

- **Walk through a use case in slow motion** and look for holes.[^shapeup-ch5] Useful questions from the book:
  - Does this need new technical work we have never done?
  - Are we assuming a design solution exists that we couldn't come up with ourselves?
  - Is there a hard decision to settle now so it doesn't trip up the team?
- **Patch** each hole with a decision, **declare cases out of bounds** to stay within the appetite, and **cut** parts
  that were exciting while sketching but aren't needed.[^shapeup-ch5]

## 4. Talk with technical experts

This is the first time the idea leaves the closed door, and it is still easy to change.[^shapeup-ch5]

- **Say it is just an idea**, "a potential bet, not something that's coming down the pipe yet."[^shapeup-ch5]
- **Ask the right question.** "Is this possible?" is useless: "In software, everything is possible but nothing is
  free." Ask "is X possible in 6-weeks?" instead.[^shapeup-ch5]
- **Hunt for time bombs.** Tell them you are looking for risks that could blow up the project once a team is on it,
  and ask whether the problem could be simplified or approached differently.[^shapeup-ch5]
- **"Try to keep the clay wet."** Use a whiteboard, not a document or slides, and stick to the concept you already
  worked out.[^shapeup-ch5]
- The result may be a few changes, or another round of shaping.[^shapeup-ch5]

## 5. Then write the pitch

Once the idea has patches for its rabbit holes and fences around what is out of bounds, it can be written up for
people with less context.[^shapeup-ch5] A pitch has five ingredients:[^shapeup-ch6]

| Ingredient | Content |
| --- | --- |
| Problem | The raw idea, use case or observation that motivates the work. Best told as one specific story. |
| Appetite | How much time we want to spend, and how that constrains the solution. |
| Solution | The core elements, in a form people can understand immediately. |
| Rabbit holes | Details of the solution called out to avoid problems. |
| No-gos | Anything specifically excluded, to fit the appetite or keep the problem tractable. |

## What makes a good pitch

Chapter 6's guidance, with its UI examples taken out.[^shapeup-ch6]

- **Problem and solution together.** "It's critical to always present both a problem and a solution together." A
  solution without a problem turns the discussion into a matter of taste, with nothing to test options against. "A
  problem without a solution is unshaped work" and goes back to shaping.
- **One specific story for the problem.** "The best problem definition consists of a single specific story that shows
  why the status quo doesn't work." That story is what the solution is judged against. It also shows who has the
  problem: a strong solution for users who barely matter is still a bad bet.
- **The appetite is stated.** "Stating the appetite in the pitch prevents unproductive conversations." The question
  becomes "what does a solution look like if this is worth two weeks?". Anyone can propose an expensive solution; a
  simple one that fits takes insight.
- **Concrete enough for outsiders, no more.** Working notes made while shaping read as "you had to be there" to
  others, so the pitch adds some concreteness. It still doesn't over-specify, because detail boxes in the people who
  build it and pulls discussion into details. Show the linchpin parts concretely, keep the rest rough, and say which
  parts are only illustrations.
- **Rabbit holes and no-gos are decisions.** A rabbit hole is often a few lines that patch one risk. A no-go names
  what is excluded and accepts that it might have been better, because it doesn't fit the appetite.
- **Written for people with less context and read before the meeting.** Comments are "not to say yes or no", only to
  poke holes or add missing information. The decision happens where bets are made. The pitch should still work as a
  quick live presentation if people didn't read it.

Our own adaptation for work that isn't UI: the "sketch" can be a sequence or data-flow diagram, an API contract, a
schema change or the shape of a config file. Draw only the part a reviewer must see to believe the idea works.

# Checklist before writing a pitch

This is our own condensed version of the steps above.

- [ ] The problem is one specific story, not a solution or a grab-bag.
- [ ] There is an appetite, and it was set before the design.
- [ ] The solution is rough: elements and flows, no pixel mockups.
- [ ] Every element connects; the main use case was walked through step by step.
- [ ] Rabbit holes are listed, each with its patch or decision.
- [ ] Out-of-bounds cases and cut features are written down as no-gos.
- [ ] Someone with the technical knowledge has asked "possible within the appetite?" and their concerns are handled.

# Tension: private shaping or open collaboration

This section is our own analysis.

The book keeps shaping private until the expert check, which protects the idea from early criticism and from
setting expectations. The cost is that domain knowledge arrives late. In a team without a separate shaping role, a
middle path works: shape alone up to rough elements, then invite one or two people early, and say clearly that the
idea is rough and may be dropped. Being rough is what makes inviting changes cheap. Once the work looks finished,
people stop suggesting changes and start approving or rejecting it.

[^shapeup-ch2]: Chapter 2, "Principles of Shaping".
[^shapeup-ch3]: Chapter 3, "Set Boundaries".
[^shapeup-ch4]: Chapter 4, "Find the Elements".
[^shapeup-ch5]: Chapter 5, "Risks and Rabbit Holes".
[^shapeup-ch6]: Chapter 6, "Write the Pitch".
[^shapeup-glossary]: Glossary (appendix).

---
type: Reference
title: AI Productivity Evidence
description: What controlled trials and surveys show about AI's effect on software development speed, and what they don't measure.
tags:
- ai-engineering
- development
parent: /ai-engineering/development.md
related:
- /ai-engineering/development/agent-self-improvement.md
- /ai-engineering/development/ai-native-sdlc.md
sources:
- id: cui-field-experiments
  resource: https://www.microsoft.com/en-us/research/?p=1148213
  title: 'The Effects of Generative AI on High-Skilled Work: Evidence from Three Field Experiments with Software Developers'
  author: Cui, Demirer, Jaffe, Musolff, Peng and Salz
- id: peng-copilot
  resource: https://arxiv.org/abs/2302.06590
  title: 'The Impact of AI on Developer Productivity: Evidence from GitHub Copilot'
  author: Peng, Kalliamvakou, Cihon and Demirer
  last_modified: '2023-02-13'
- id: metr-2025
  resource: https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/
  title: Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity
  author: METR
  last_modified: '2025-07-10'
- id: metr-2026-update
  resource: https://metr.org/blog/2026-02-24-uplift-update/
  title: We are Changing our Developer Productivity Experiment Design
  author: METR
  last_modified: '2026-02-24'
- id: metr-2026-survey
  resource: https://metr.org/blog/2026-05-11-ai-usage-survey/
  title: Measuring the Self-Reported Impact of Early-2026 AI on Technical Worker Productivity
  author: Joel Becker
  last_modified: '2026-05-11'
- id: dora-2025
  resource: https://research.google/pubs/dora-2025-state-of-ai-assisted-software-development-report/
  title: DORA 2025 State of AI-assisted Software Development Report
  author: DORA
- id: anthropic-rsi
  resource: https://www.anthropic.com/institute/recursive-self-improvement
  title: When AI builds itself
  author: Marina Favaro and Jack Clark
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-04T14:29:12+04:00'
stale_after: '2027-02-04T00:00:00+04:00'
---

AI probably speeds up most software development. The size of the gain for today's agents on real delivery is poorly measured. The one famous slowdown came from a specific setting and older tools, and it shouldn't be quoted as a general result.

| Study | Design | Tools | Result |
| --- | --- | --- | --- |
| Cui et al.[^cui-field-experiments] | 3 field RCTs, 4,867 developers | Autocomplete | 26% more completed tasks (SE 10.3%), larger for less experienced developers |
| Peng et al.[^peng-copilot] | RCT, 95 recruited freelancers, one task | Autocomplete, 2022 | 55.8% faster (95% CI 21–89%) |
| METR 2025[^metr-2025] | RCT, 16 experienced developers on their own large repos | Early-2025 | 19% slower; they believed 20% faster |
| METR late 2025[^metr-2026-update] | RCT, 57 developers | Late-2025 | 18% less time for returning developers (CI -38% to +9%), 4% for new ones (CI -15% to +9%) |
| METR survey[^metr-2026-survey] | Survey, 349 technical workers | Early-2026 agents | Median self-reported value 1.4–2x, speed 3x |
| DORA 2025[^dora-2025] | Survey, nearly 5,000 professionals | Mixed | Calls AI an "amplifier" of existing strengths and weaknesses |

# How to read this

METR says its late-2025 data is unreliable. Developers who wouldn't work without AI increasingly declined to take part, so the estimate is likely a lower bound. Time tracking also breaks down when people run several agents at once.[^metr-2026-update] AI use is now hard to randomize, because the most affected people opt out.

Self-reports run high. METR writes that survey results "are not necessarily grounded in reality".[^metr-2026-survey] Anthropic says its 8x growth in engineers' code output is "almost certainly an overstatement of the true productivity gain".[^anthropic-rsi]

# What is missing

No study in this set measures current agents at scale in a controlled way, or end-to-end delivery such as lead time, rework and incidents. Code volume and completed tasks are proxies. The Cui and Peng results predate agents, and only Cui's abstract was read for this note.

[^cui-field-experiments]: Microsoft Research page, June 2025. Abstract only.
[^peng-copilot]: arXiv, 2023-02-13.
[^metr-2025]: METR, 2025-07-10. METR marks these results out of date.
[^metr-2026-update]: METR, 2026-02-24.
[^metr-2026-survey]: Joel Becker, METR, 2026-05-11.
[^dora-2025]: DORA abstract, 2025.
[^anthropic-rsi]: Favaro and Clark, The Anthropic Institute, updated 2026-09-18.

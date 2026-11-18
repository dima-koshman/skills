---
type: Concept
title: Agent Verification and Self-Improvement
description: Agents can only be trusted, delegated to, or left to improve themselves as far as something independent can check their work, so verification sets the limit on supervision and on self-improvement.
tags:
- ai-engineering
- development
- verification
parent: /ai-engineering/development.md
related:
- /ai-engineering/development/observability-driven-development.md
- /ai-engineering/development/ai-productivity-evidence.md
- /ai-engineering/context/skills.md
- /ai-engineering/context/context-engineering.md
- /ai-engineering/observability.md
sources:
- id: sutton-verification
  resource: http://www.incompleteideas.net/IncIdeas/KeytoAI.html
  title: Verification, The Key to AI
  author: Rich Sutton
  last_modified: '2001-11-15'
- id: bainbridge-ironies
  resource: https://en.wikipedia.org/wiki/Ironies_of_Automation
  title: Ironies of Automation (encyclopedia summary of Bainbridge, 1983)
- id: shen-tamkin
  resource: https://www.anthropic.com/research/AI-assistance-coding-skills
  title: How AI assistance impacts the formation of coding skills
  author: Judy Hanwen Shen and Alex Tamkin
  last_modified: '2026-01-29'
- id: anthropic-work
  resource: https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic
  title: How AI is transforming work at Anthropic
  author: Anthropic
  last_modified: '2025-12-02'
- id: goodhart
  resource: https://en.wikipedia.org/wiki/Goodhart%27s_law
  title: Goodhart's law
- id: darwin-godel-machine
  resource: https://arxiv.org/abs/2505.22954
  title: 'Darwin Godel Machine: Open-Ended Evolution of Self-Improving Agents'
  author: Jenny Zhang et al.
  last_modified: '2026-03-12'
- id: aide2
  resource: https://www.alphaxiv.org/abs/2609.26457.md
  title: Recursive self-improvement of AI research agents
  author: Dhruv Srikanth et al.
  last_modified: '2026-09-22'
- id: anthropic-rsi
  resource: https://www.anthropic.com/institute/recursive-self-improvement
  title: When AI builds itself
  author: Marina Favaro and Jack Clark
- id: mit-tr-rsi
  resource: http://www.technologyreview.com/2026/08/18/1142188/ai-recursive-self-improvement
  title: AI's recursive self-improvement might not come so quickly after all
  author: Michelle Kim
  last_modified: '2026-08-18'
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-04T14:29:12+04:00'
stale_after: '2027-05-04T00:00:00+04:00'
---

Rich Sutton's Verification Principle says an AI system "can create and maintain knowledge only to the extent that it can verify that knowledge itself". Otherwise it stays limited to what people can monitor.[^sutton-verification] He wrote that in 2001 about knowledge. It now applies to agents at three levels:

1. **Verification:** does this output work?
2. **Supervision:** can a person still judge the agent's work?
3. **Self-improvement:** did this change to the agent make it better?

Each level depends on the one before it.

# Supervision

Automation removes the practice that supervision relies on. Bainbridge's *Ironies of Automation* (1983) describes operators left with monitoring and rare hard interventions, without daily practice; this note read an encyclopedia summary, not the paper.[^bainbridge-ironies] Anthropic's internal study calls the modern form a "paradox of supervision".[^anthropic-work]

The closest experiment is a trial of 52 mostly junior engineers learning a Python library. The AI group scored 50% on a quiz straight afterwards, against 67% for hand coding. The gap was largest on debugging, which is the skill used to check AI code.[^shen-tamkin] It tested learning rather than supervision, with a chat assistant and no long-term follow-up. No study here measures whether someone who never did a task can supervise it.

Feeling in control isn't evidence. See [AI Productivity Evidence](/ai-engineering/development/ai-productivity-evidence.md) on how far self-reports drift from measurement.

# Self-improvement

Sources draw the line in different places:

- **Darwin Godel Machine:** "modifying the design of an agent's own components". Tools, prompts and workflows count. Model weights stay frozen.[^darwin-godel-machine]
- **AIDE2:** "each accepted rewrite becomes the agent that the next round edits".[^aide2]
- **Anthropic:** a system "capable of fully autonomously designing and developing its own successor".[^anthropic-rsi]

The ladder below is this note's synthesis of those definitions, not a published standard.

| Level | What changes | What accepts the change | Example |
| --- | --- | --- | --- |
| 0. Output loop | The product | Tests or telemetry | Agent checks telemetry after a deploy and fixes the bug |
| 1. Instruction and tool learning | Skills, memory, tools | Agent or human judgment | Agent updates its own skill; tool feedback reaches the tool's maintainers |
| 2. Gated self-modification | Harness code | Automatic score on benchmarks | Darwin Godel Machine, AIDE2 |
| 3. Better at improving | The improvement process | A measured faster rate of gain | Not demonstrated |
| 4. Successor design | The model itself | Open | Not demonstrated |

Three questions place a loop on this ladder:

1. Does it change what produces the work, or only the work?
2. Does something other than the agent decide whether the change helped?
3. Does the improvement process itself get better?

Level 0 can be excellent engineering, and it is still not self-improvement. It becomes an input to level 1 when a failure leads to a change in the agent's instructions.

Level 1 is common and useful, but a rule added after one incident may never help again, or may slowly bloat context. A change only reaches level 2 when something measures it. A cheap version is to replay the failed task with and without the new instruction.

## Evidence

Gated loops work on benchmarks. The Darwin Godel Machine went from 20% to 50% on SWE-bench Verified over 80 iterations.[^darwin-godel-machine] AIDE2's accepted rewrites include "demands a root-cause diagnosis before any fix". Its private grade rose from 0.703 to 0.778 over seven accepted rewrites in one eight-day run.[^aide2]

Level 3 is unproven. The Darwin Godel Machine paper assumes that better coding means better self-modification.[^darwin-godel-machine] AIDE2 tested this directly and called the result inconclusive: 0.780 with the improved agent as the outer loop, and 0.782 with the human-built one, on three seeds.[^aide2]

Open-ended research is harder. In a Princeton study reported by MIT Technology Review, agents were "unambiguously bad" at the research itself, though it covered only two papers.[^mit-tr-rsi] In Anthropic's account, humans still "supply the goal", and they chose the problem and scoring rubric in its weak-to-strong experiment.[^anthropic-rsi]

# Keeping the check independent

"When a measure becomes a target, it ceases to be a good measure."[^goodhart] In these loops that shows up as reward hacking: the proxy improves and the real goal doesn't. In AIDE2 the rate fell from 55% to 32% across versions, against 39% for the human-built agent, and a third of the tested pairs still hacked.[^aide2]

- **Hide the grade.** AIDE2's inner loop sees public scores, and acceptance uses a private held-out grade.[^aide2]
- **Separate the improver from the evaluator.** The Darwin Godel Machine's safety section says its scope included the agent's code and evaluation harnesses, so the evaluator needs its own protection.[^darwin-godel-machine]
- **Keep a record.** Sandboxes, time limits and an auditable archive make bad changes findable.[^darwin-godel-machine] Version-controlled skills with a stated reason give the same benefit cheaply.
- **Treat benchmark gains as partial.** The Darwin Godel Machine authors call them "necessary but insufficient".[^darwin-godel-machine]

Humans still set the goal and metric in every example above, and that remains the lever.

[^sutton-verification]: Rich Sutton, 2001-11-15.
[^bainbridge-ironies]: Wikipedia summary of Bainbridge (1983), read 2026-11-04.
[^shen-tamkin]: Shen and Tamkin, Anthropic, 2026-01-29. From the vendor of the assistant category tested.
[^anthropic-work]: Anthropic Societal Impacts, 2025-12-02. Self-reported, by the company that makes the tool.
[^goodhart]: Strathern's wording (1997), as given on Wikipedia, read 2026-11-04.
[^darwin-godel-machine]: Zhang et al., revised 2026-03-12. Read in part; the safety and hard-coding appendices were not read verbatim.
[^aide2]: Srikanth et al., Weco AI, 2026-09-22. Read in part. The trace is not meant to show generalization beyond the selection benchmark.
[^anthropic-rsi]: Favaro and Clark, The Anthropic Institute, updated 2026-09-18.
[^mit-tr-rsi]: Michelle Kim, MIT Technology Review, 2026-08-18, reporting on Kirgis, Kapoor et al. The underlying paper was not read.

# Toil

Manual, repetitive operational work that scales with the service — capped and engineered away so a team's effort grows sublinearly with what it runs.

Reference: <https://sre.google/sre-book/eliminating-toil/>

Note dated: 2026-10-03.

> If a human operator needs to touch your system during normal operations, you
> have a bug. The definition of normal changes as your systems grow.
> — Carla Geisser, Google SRE

Toil is not just unpleasant work. The chapter separates it from **overhead**
(meetings, goal setting, HR paperwork) and from **grungy work with lasting
value** (cleaning up an alerting configuration is grungy but not toil). Toil is
work tied to running a production service. The more of these traits a task has,
the more it is toil:

| Trait | Test |
| --- | --- |
| Manual | Hands-on human time, even if that is only running a script |
| Repetitive | Done over and over; a first or second occurrence is not toil |
| Automatable | A machine could do it, or better design could remove the need |
| Tactical | Interrupt-driven and reactive, like handling pages |
| No enduring value | The service is in the same state afterwards |
| O(n) with growth | Scales linearly with service size, traffic, or users |

A well-designed service should grow by an order of magnitude with no additional
work beyond one-time resource additions.

## The 50% cap

Google SRE keeps toil below 50% of each engineer's time, averaged over quarters.
The rest goes to engineering that reduces future toil or adds features. The cap
exists because toil expands to fill all available time if left unchecked, and
because it is what keeps SRE an engineering team rather than an ops team.
On-call alone sets a floor: one primary and one secondary week in a six-person
rotation is about 33%. The top sources of toil are interrupts, then urgent
on-call response, then releases and pushes.

Small amounts of toil are fine, and some people find it calming. In bulk it
causes career stagnation, low morale, and attrition. It also sets a precedent:
a team that absorbs operational work invites other teams to hand it more.

## Watch for

- **"It needs human judgment" can hide toil.** A service that pages several
  times a day, each alert needing an expert response, is poorly designed. The
  judgment-heavy response stays toil until the system is
  [simplified](simplicity.md) to remove the failure or handle it automatically.
- **Running a script is still toil.** Automation that needs a human to trigger
  it removes steps, not the toil.
- **Averages hide outliers.** A team average of 33% can contain people at 80%.
  Rebalance the load rather than reading only the mean.

## Agents as toil automation

Agents are among the most effective tools for reducing toil. The chapter's
"automatable" test used to mean *scriptable*. That left out a large class of
work too varied for a script but too routine to deserve an engineer: reading a
stack trace, matching it to a recent change, finding the failing test, drafting
the fix. A coding agent with tool access does this kind of work, so the
boundary of what counts as automatable moves. Because the agent does not get
tired and its cost does not grow with team size, toil stops scaling O(n) with
human effort.

The highest-leverage target is production analysis. Agents can join the loop
online and continuously, not only when someone asks:

1. **Detect.** On a schedule or on a trigger, scan traces, logs, and metrics,
   cluster recurring failures into issues, and deduplicate them against known
   ones.
2. **Diagnose.** Correlate the evidence with the source code and recent
   deploys, and reproduce the failure where possible.
3. **Act through a gate.** Open a PR when the fix is bounded. When it is not,
   produce an investigation report with the evidence, hypotheses, reproduction
   steps, and a recommended next step for a human to decide on.
4. **Watch quality, not just errors.** For LLM-backed services, run online LLM
   evaluators over live traces. Their scores become a quality signal (an SLI)
   that catches regressions an error rate never shows: wrong answers,
   hallucinations, policy drift.
5. **Close the loop.** Track whether the issue recurs after the fix, and turn
   the failing cases into regression examples.

Two products cover parts of this loop:

- **[LangSmith Engine](https://docs.langchain.com/langsmith/engine-overview)**
  is this loop productized for agents traced in [LangSmith](../../ai-engineering/observability/langsmith.md).
  It scans tracing projects on a schedule, groups recurring failures into
  issues, and diagnoses root causes against connected source code. It then
  proposes fixes as pull requests, tracks each issue as matching traces arrive
  (reopening it if the issue recurs), and creates ground-truth dataset examples
  for offline evaluation. Code fixes target agents built with LangChain,
  LangGraph, and Deep Agents.
- **[Langfuse](../../ai-engineering/observability/langfuse.md) evaluators**
  supply the quality signal. LLM-as-a-judge evaluators run asynchronously on
  incoming production observations that match a rule's filters, and they write
  numeric, categorical, or boolean scores with reasoning back onto the traces.
  The same evaluators score datasets in experiments. The detect-diagnose-fix
  agent around those scores is yours to build, for example a coding agent with
  read access to Langfuse and the repository.
  [LangSmith Evals](../../ai-engineering/observability/langsmith-evals.md)
  plays the same role in LangSmith.

The human role moves from doing the toil to reviewing what the agent produced.
That only reduces toil if the output is worth reviewing. Noisy, duplicated, or
speculative findings recreate the problem as *review* toil. Keep findings
deduplicated and evidence-backed, keep fixes small, and keep agents read-only
in production, with PRs and runbooks as their only route to change things. The
general technique is
[observability-driven development](../../ai-engineering/development/observability-driven-development.md),
and the Maintain stage of the
[AI-native SDLC](../../ai-engineering/development/ai-native-sdlc.md) wires it
into a closed loop.

## Resources

- [Google SRE book, chapter 5: Eliminating Toil](https://sre.google/sre-book/eliminating-toil/) — Vivek Rau, edited by Betsy Beyer.
- [Site Reliability Engineering](sre.md) — the book overview.

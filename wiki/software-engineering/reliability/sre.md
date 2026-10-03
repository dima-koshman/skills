# Site Reliability Engineering

Google's discipline of running production with software engineering: explicit reliability targets, an error budget that balances them against change, and automation in place of manual operations.

Reference: <https://sre.google/sre-book/>

*Site Reliability Engineering* (O'Reilly, 2016; edited by Betsy Beyer, Chris
Jones, Jennifer Petoff, and Niall Richard Murphy) is free to read online. Its
founding framing is SRE as "what happens when you ask a software engineer to
design an operations team." The book is a collection of essays, so individual
chapters stand on their own.

## Core ideas

- **Reliability is a target, not a maximum.** 100% is the wrong goal. Users
  cannot tell 99.99% from 100%, and every extra nine costs velocity
  ([Embracing risk](https://sre.google/sre-book/embracing-risk/)).
- **SLIs, SLOs, and error budgets.** Measure what users experience (SLI), set
  a target (SLO), and treat the shortfall allowed by the SLO as a budget. While
  budget remains, ship; once it is spent, slow releases and invest in stability
  ([Service level objectives](https://sre.google/sre-book/service-level-objectives/)).
- **Cap [toil](toil.md).** Toil is manual, repetitive, automatable work that
  scales with the service. SRE teams keep it under about half their time and
  engineer it away ([Eliminating toil](https://sre.google/sre-book/eliminating-toil/)).
  Agents now cover much of that automation, including continuous analysis of
  traces and metrics.
- **Monitor symptoms.** Use the four golden signals (latency, traffic, errors,
  saturation), and page only on user-visible, actionable problems
  ([Monitoring distributed systems](https://sre.google/sre-book/monitoring-distributed-systems/)).
- **Blameless postmortems.** Incidents are written up to fix systems and
  processes, not to assign fault
  ([Postmortem culture](https://sre.google/sre-book/postmortem-culture/)).
- **Release engineering and [simplicity](simplicity.md).** Small, reproducible,
  gradual releases and minimal accidental complexity make failures rare and
  attributable ([Release engineering](https://sre.google/sre-book/release-engineering/)).

## Book structure

| Part | Covers |
| --- | --- |
| I. Introduction | What SRE is; Google's production environment |
| II. Principles | Risk, SLOs, toil, monitoring, automation, release engineering, simplicity |
| III. Practices | Alerting, on-call, troubleshooting, incidents, postmortems, testing, load balancing, overload and cascading failures, distributed consensus, data integrity, launches |
| IV. Management | On-call onboarding, interrupts, operational overload, team collaboration |
| V. Conclusions | Lessons from other industries |

The appendices include practical templates, such as an
[example postmortem](https://sre.google/sre-book/example-postmortem/) and a
[launch checklist](https://sre.google/sre-book/launch-checklist/).

The same ideas reappear in agent-era practice. The
[AI-native SDLC](../../ai-engineering/development/ai-native-sdlc.md) uses
control-band monitoring and postmortem-to-eval loops in its Maintain stage, and
[observability-driven development](../../ai-engineering/development/observability-driven-development.md)
makes telemetry evidence for code changes.

## Resources

- [Site Reliability Engineering — table of contents](https://sre.google/sre-book/table-of-contents/)
- [The Site Reliability Workbook](https://sre.google/workbook/table-of-contents/) — the hands-on companion on implementing SLOs, alerting, and on-call

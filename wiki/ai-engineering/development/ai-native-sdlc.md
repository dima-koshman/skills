# AI-Native SDLC

A software lifecycle rebuilt as a loop of committed artifacts, with agents doing the work between gates and humans owning every judgment call.

The AI-native SDLC (also called the agentic SDLC or AI SDLC) keeps the control
objectives of the traditional lifecycle — accountability, review, separation of
duties, auditability — but changes how they are enforced. Instead of a linear
hand-off between roles, the six stages (Plan, Design, Build, Test, Deploy,
Maintain) form a loop. Each stage ends by committing an artifact to version
control, and that commit triggers the next stage. Human attention moves to the
gates, where people review what the agent produced and flagged instead of
starting each stage from scratch.

This page summarizes Anthropic's
[AI-Native SDLC Playbook](https://claude.com/blog/the-ai-native-sdlc-playbook)
(Louis Claxton, August 2026). The playbook is written around
[Claude Code](../agents/claude-code.md), but the structure carries over to any
capable coding [agent](../agents/agent.md) and [harness](../harness/harness.md).

## Why the lifecycle has to change

The traditional SDLC was optimized for a world where writing code was the most
expensive stage. PRDs, estimation rituals, and stage-gate security reviews
existed to force alignment before weeks or months of implementation. Its
controls also assume that a human performs every step.

Once agents write most of the diff, three things follow:

- **The bottleneck moves** to the stages either side of build — planning,
  review/test, and deploy — which still run at human speed.
- **Controls stop matching reality.** Line-by-line human review made sense when
  a person wrote each line; it cannot keep pace with agent output.
- **Governance costs rise** because exceptions still route through weekly or
  monthly committees.

Security is the clearest example: teams sized for human output either build a
review queue or let code ship under-reviewed, and a regulated organization can
accept neither. The checks have to run at agent speed.

## The artifact chain

The thread through the whole model is the committed artifact. Early stages use
Markdown because a product owner and an agent can both read and act on the same
file; from Build onward the artifact is code and its records.

| Stage | Traditional | AI-native | Committed artifact | Commit triggers |
| --- | --- | --- | --- | --- |
| Plan | Requirements by committee, workshops, sign-offs | Originator brainstorms with the agent; result captured as a proto-spec | `intent.md` | Requirements and design pass |
| Design | Analysts write the spec, designers parse it | One session produces requirements and design, constrained by policy [skills](../context/skills.md) | `spec.md` | Plan mode |
| Build | Handwritten code and tests, docs after the fact | Plan-first implementation; knowledge in `CLAUDE.md` and skills; hooks as guardrails | `plan.md`, diff, tests | PR |
| Test | QA gates at stage boundaries | Agent verifies its own work; continuous evals on agent configuration | Check output, eval results | Review |
| Deploy | Humans read every line; inconsistent governance | Agentic review passes; human approval for intent and risk; hooks as approval gates | PR with review findings | Pipeline |
| Maintain | Humans watch production | Deterministic monitors invoke the agent; findings re-enter as new intent | Incident record, new `intent.md` | Plan |

The chain of commits doubles as the audit trail: who asked for what, what the
agent produced, and who approved it.

## Stages and plays

The playbook organizes the work into *plays*. Each play states what changes,
prerequisites, execution steps, governance considerations, and leading/lagging
metrics. Plays are modular; adopt them in dependency order, not stage order.

### 1. Plan — capture intent

The originator (who need not be an engineer) describes the problem in their own
words; the agent asks the questions an analyst would — scope, users,
constraints, success criteria — and writes the result as `intent.md` from an
organizational template (itself a skill). The originator corrects it, and it is
committed to a shared, version-controlled home, typically an `intent/` folder in
the product repo. Non-git users commit through a VCS connector.

- **Governance:** author, timestamp, and revisions live in git; the product
  owner's accept/reject is the merge or the closed review.
- **Metrics:** time from first conversation to committed intent (weeks →
  hours); share of intents accepted into Design; intent edits made after the
  spec exists.

### 2. Design — requirements and design in one session

On acceptance of `intent.md`, the agent produces `spec.md` with the
organization's brand, security, compliance, and UX skills loaded, explicitly
flagging areas of concern and contradicting policies. Run it by hand first, then
as a slash command, then as a non-interactive job fired by the intent merge that
opens the spec as a PR. The product owner reviews rather than writes, resolves
each flag with its policy owner, and escalates higher-risk work to a tech lead.

- **Governance:** policy is applied *while* the spec is written, not discovered
  weeks later; the spec, the prompt, and the skill versions in force are all
  versioned.
- **Metrics:** time between the intent and spec commits; `spec.md` commits
  dated after the first `plan.md` (requirements rework).

### 3. Build — plan first, knowledge as files, guardrails as code

- **Plan mode as default.** The engineer gives the agent the intent and spec,
  asks for a plan naming the files, the order of work, and the proving tests,
  and interrogates it (what could break, riskiest step, rejected alternatives)
  until someone who never saw the conversation could implement from it. The plan
  is committed as `plan.md`; departures update it in the same commit. As
  guardrails mature, auto mode becomes the default for routine, well-covered,
  small-blast-radius work, shifting human review from watching edits to
  reviewing artifacts.
- **`CLAUDE.md`.** One page at the repo root: commands, binding conventions,
  architecture, and "things the agent gets wrong." Rule of thumb: a mistake made
  twice becomes a line in the file. Keep it short; stale content wastes context.
- **Skills as institutional knowledge.** Encode knowledge that must be applied
  consistently (a security standard, an API convention) as a skill owned by a
  named policy owner. A skill is an *advisory* control: it makes violations
  rare. Anything that must always hold needs a deterministic layer behind it.
- **Hooks as build-time guardrails.** The deterministic layer: block edits to
  protected paths, run formatters and linters after edits, keep credentials out
  of diffs. Keep them fast and file-scoped; heavy checks belong at commit or PR.
  Approval-asking hooks belong at Deploy, not in the parallel build path.
- **Parallel sessions and [subagents](../harness/subagents.md).** One engineer
  runs two or three sessions in separate git worktrees on independent tasks, and
  scales only while review keeps up. Recurring jobs (verifier, simplifier,
  researcher) become subagents with their own context and tool limits. The
  engineer's role shifts to orchestration.

### 4. Test — feedback loops and continuous evals

- **Give the agent a feedback loop.** Wrap verification in single commands
  (`make test`), document healthy output in `CLAUDE.md`, and state quantifiable
  targets. For bug fixes, commit a failing test first, then have the agent make
  it pass without editing it — enforced by a hook that blocks test-file edits
  during fix tasks. For UI, give it a browser or screenshot tool and the mock.
  Verification with pasted output is part of "done." (A verifier subagent is a
  fresh-context final check; the feedback loop runs throughout the task.)
- **Continuous evals in CI.** Agent configuration — model, prompts,
  `CLAUDE.md`, skills, hooks — is regression-tested like code. Collect 20–50 real
  tasks with accepted outcomes, express each as prompt plus acceptance checks,
  run them non-interactively on schedule and on any configuration change, and
  gate merges on pass rate. Every production incident becomes a permanent eval.
  The suite is live: retire cases that stop discriminating as models improve.
  See [LangSmith Evals](../observability/langsmith-evals.md) for a comparable
  evaluation system.

### 5. Deploy — review both ways, governance as code

- **AI in the PR review loop.** Every PR gets the same review passes, ranked by
  severity, defined in a `REVIEW.md` (bugs, security, compliance against
  `spec.md` and `plan.md`; what counts as Important vs. Nit; what to skip). The
  agent also addresses review comments on its own PRs. Findings never approve a
  PR — branch protection still requires a code owner. Repeated findings feed
  back into `CLAUDE.md`; the tech lead tunes the reviewer monthly.
- **Hooks as approval gates.** Each human approval the change process requires
  (change-management sign-off, release authorization, protected paths) becomes a
  pre-action hook that can allow, ask, or block, and explains itself when it
  blocks. Team hooks live in repo settings; non-negotiable ones in managed
  settings engineers cannot override. The playbook's regulated-enterprise
  example also uses managed permission rules, an OS-level sandbox with a
  network allowlist and credential denial, managed-only hooks and
  [MCP](../context/mcp.md) servers, an approved plugin marketplace, and a
  minimum client version.
- **CI/CD integration.** Start with read-only judgment steps in the pipeline
  (triage a failed build, summarize a flaky test, draft a changelog), then add
  write steps whose output always arrives as a PR. Run agent jobs sandboxed with
  short-lived scoped tokens and no standing production credentials. Expose
  deploy, status, and rollback as environment-scoped MCP tools so deployment
  power is an allowlist. Tier autonomy by environment — free in dev, hybrid in
  staging, gate-blocked in production — and make rollback the most rehearsed
  path in the pipeline.

> **Governing principle:** the agent may act up to the production gate and
> cannot pass it.

### 6. Maintain — close the loop

Here a trigger, not a person, invokes the agent. Between stages, an independent
confidence gate (a deterministic check or an adversarial reviewing agent) decides
whether output continues or escalates to a human.

- **Control-band breaches.** A deterministic, unit-tested detection script
  watches a metric with a rolling baseline (CI failure rate, post-deploy 5xx
  rate, PR cycle time) using Western Electric–style rules. Version-controlled
  tiers decide what the agent may do: 1σ logs; 2σ invokes it read-only to
  diagnose; 3σ lets it propose — open a PR into the review gate or trigger a
  pre-approved runbook such as rollback. The diagnosis is written as a new
  `intent.md`, triaged by the on-call engineer (fix, schedule, dismiss —
  dismissals tune the bands), and the eventual fix adds an eval. This is the
  same evidence-to-change loop as
  [observability-driven development](observability-driven-development.md), wired
  to run headless.
- **Recurring security scans.** A scan is a point-in-time statement about code
  under a particular model, and both halves go stale. Run scans on a schedule
  (weekly for active services), treat the first as a baseline, triage with
  confidence ratings, and record dismissals with a reason. Bounded fixes go
  through the PR gate; wider issues become `intent.md`; each fixed vulnerability
  class becomes an eval. Model-driven scans augment, not replace, deterministic
  SAST and dependency scanning.
- **On-call through chat.** The agent joins incident channels under its own
  identity as first responder; anyone in the channel can steer it, it verifies
  recovery through MCP, and it writes the post-mortem to a versioned lessons
  file. The channel becomes the audit trail. Small fixes arrive as PRs; larger
  work becomes intent, and the loop feeds itself.

## Governance invariants

- **Humans own judgment.** Agents draft, implement, review, and diagnose;
  people accept intent, approve specs and plans, approve PRs, and authorize
  releases.
- **Separation of duties.** The agent that wrote a change has no route to
  approve it; branch protection turns every agent write into a PR.
- **Advisory vs. deterministic controls.** Skills and `CLAUDE.md` make the right
  behavior likely; hooks, managed settings, sandboxing, and branch protection
  make the wrong behavior close to impossible. Policies that must always hold
  need both.
- **Attributable identity.** Interactive sessions are attributed to the engineer
  who ran them; non-interactive runs act under the agent's own identity so logs
  separate the two.
- **Everything is versioned.** Intent, spec, plan, prompts, skill versions,
  hooks, review policy, and monitoring bands all live in git and change through
  review. See [security](../security/security.md) for the threat model these
  controls address.

## Legacy systems and source of truth

Existing artifacts already live in Jira, ServiceNow, requirements tools, Figma,
and change boards that auditors accept. For each artifact type, name one source
of truth:

1. **Repo as source of truth** — Markdown artifacts are authoritative; the
   legacy system references commits. Cleanest for engineering-led organizations.
2. **Legacy system as source of truth** — the agent reads the record at session
   start and writes the outcome back through an MCP connector; Markdown files are
   working copies.
3. **Linkage as the minimum bar** — every artifact notes the record ID and every
   record carries the commit SHA. A reasonable starting point that accepts two
   sources of truth.

## Measuring it

Every play pairs a leading (speed) indicator with a lagging (quality)
indicator, most read straight from git, PR metadata, CI logs, or the
OpenTelemetry export. Representative pairs:

| Play | Leading | Lagging |
| --- | --- | --- |
| Intent | Conversation → committed intent | Intent acceptance rate |
| Design | Intent commit → spec commit | Spec changes after planning starts |
| Plan mode | First-pass merge share | Rework cycles; diff matches `plan.md` |
| Feedback loop | First-pass CI success | Review time per PR; change failure rate |
| Evals | Eval pass rate; incident → eval latency | CI-caught vs. production regressions |
| PR review | Time to first review | Defects caught pre-merge vs. escaped |
| CI/CD | Failures triaged without paging | DORA metrics |
| Closing the loop | Breach → intent in triage | Findings merged as fixes; repeat incidents |

## Adoption order

Plays with no prerequisites can start anywhere: intent capture, `CLAUDE.md`,
skills, hooks, and the feedback loop. The rest depend on earlier plays — for
example, continuous evals need `CLAUDE.md` and the feedback loop; CI/CD
automation needs the review gate and approval hooks in place *before* it
accelerates anything through them; and closing the loop needs intent, review,
hooks, and a rehearsed rollback. Start by prompting each step by hand; the end
state is a loop in which each accepted artifact fires the next gate.

## Citations

- [The AI-Native SDLC Playbook — Claude blog](https://claude.com/blog/the-ai-native-sdlc-playbook)
- [Claude Code admin setup](https://code.claude.com/docs/en/admin-setup)
- [Claude Code settings reference](https://code.claude.com/docs/en/settings)
- [Claude Code hooks](https://code.claude.com/docs/en/hooks)
- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [Claude Code sandboxing](https://code.claude.com/docs/en/sandboxing)
- [Claude Code monitoring (OpenTelemetry)](https://code.claude.com/docs/en/monitoring-usage)

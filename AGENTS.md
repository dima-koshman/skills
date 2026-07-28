# Agent Instructions

## Verification before completion

Evidence before claims, always. If you have not run the verification command in this
message, you cannot say it passes.

Before claiming anything is done, fixed, or passing:

1. Identify the command that proves the claim.
2. Run it fresh and in full — not a subset, not a previous run.
3. Read the actual output and exit code.
4. State the claim with the evidence, or state the real status.

What each claim actually requires:

| Claim | Requires |
| --- | --- |
| Tests pass | Test command output showing 0 failures |
| Linter clean | Linter output, 0 errors — a passing linter is not a passing build |
| Build succeeds | Build command, exit 0 |
| Bug fixed | The original failing symptom, retested |
| Regression test works | Red-green verified: revert the fix, confirm the test fails, restore |
| Subagent finished | The diff, read yourself — not the agent's self-report |
| Requirements met | Each requirement checked off individually |

Report skipped steps and failures plainly; a failed step reported honestly is worth more than
a green summary that hides it.

## Receiving code review

Review feedback is a technical claim to evaluate, not an order to execute.

- Read all of it before acting. If any item is unclear, ask before implementing *any*
  of them — items are often related, and partial understanding produces wrong work.
- Verify each suggestion against this codebase before implementing. Does it break
  existing behavior? Is there a reason the current code is the way it is?
- Push back with technical reasoning when a suggestion is wrong. Cite the code or test
  that proves it.
- Fix in order: blocking/security, then trivial, then complex. Test each individually.
- Apply YAGNI to review suggestions too: if a "make this proper" suggestion targets code
  nothing calls, propose deleting it instead.

## Subagents

- Subagents never inherit this session's context. Construct exactly the context they
  need; a vague delegation produces vague work. Verify results by reading the diff,
  not the agent's summary.

## Testing

- Write the test before the implementation, and watch it fail first. A test that passes
  the moment you write it has proven nothing.
- The failure must be for the expected reason — feature missing, not a typo or import error.
- One behavior per test, named for the behavior.
- Test real code. Reach for mocks only when there is no alternative, and never assert on
  mock call counts as a substitute for asserting on behavior.
- Never fix a bug without a test that reproduces it first.
- If a test is hard to write, the design is usually the problem — fix the design, not the test.

## Debugging

Find the root cause before proposing a fix. Symptom patches are not fixes.

- Read the error and the full stack trace before forming a theory.
- Reproduce consistently. If you can't, gather more data instead of guessing.
- Check what changed recently — diff, recent commits, new dependencies, config.
- In multi-component systems, instrument each boundary and run once to find *where* it
  breaks before theorizing about *why*.
- Form one hypothesis, make the smallest change that tests it, verify. If it's wrong,
  form a new hypothesis — don't stack fixes.
- **After 3 failed fixes, stop and question the architecture.** If each fix surfaces a new
  problem elsewhere, the design is wrong and more patches won't help. Raise it.

The `systematic-debugging` skill has the full process and tracing techniques.

## Planning and design

- For anything non-trivial, understand the problem before writing code: ask clarifying
  questions one at a time, propose 2-3 approaches with a recommendation, agree on the
  design first. Scale this to the task — a config change needs a sentence, not a spec doc.
- Prefer smaller, focused files with one clear responsibility. Files that change together
  belong together.
- In existing code, follow established patterns. Fix problems in code you're already
  touching; don't bundle unrelated refactoring.
- YAGNI. Remove speculative features from designs before implementing them.

The `brainstorming` and `writing-plans` skills cover the full workflow for larger work.

## Parallel execution

- Before making tool or subagent calls, check whether they depend on each other's output.
  If they don't, issue them together in one turn rather than one at a time — it saves
  latency and token cost.

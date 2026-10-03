# Simplicity

Reduce accidental complexity to make production systems easier to understand, change, and operate reliably.

Reference: <https://sre.google/sre-book/simplicity/>

Note dated: 2026-09-30 18:00:00+00:00.

Google's SRE book treats simplicity as a prerequisite for reliability. The aim
is to balance stability with agility: predictable code and reliable release
processes make changes easier to understand and failures easier to diagnose.

## Design consequences

- Distinguish **essential complexity**, inherent in the problem, from
  **accidental complexity**, introduced by implementation choices.
- Delete dead code rather than retaining commented blocks or permanently
  disabled features; version control preserves the history.
- Keep APIs small and purposeful. Fewer methods and parameters leave fewer
  behaviors to understand and maintain.
- Give modules and services clear responsibilities and loose coupling so they
  can change independently. Version interfaces and preserve compatibility;
  [Protocol Buffers](../communication/protobuf.md) illustrate the importance of
  compatibility at the data-format boundary.
- Release small, understandable changes so regressions can be attributed to a
  narrower set of causes.

Apply this when deciding whether to introduce a
[service mesh](../infrastructure/service-mesh.md): centralized traffic policy
may remove duplicated application code while adding operational components.
Judge the total complexity against a concrete requirement.

## Resources

- [Google SRE book, chapter 9: Simplicity](https://sre.google/sre-book/simplicity/) — Max Luebbe, edited by Tim Harvey.

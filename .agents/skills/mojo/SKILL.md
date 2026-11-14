---
name: mojo
description: Dima's general Mojo reference — style rules, debugging (mojo debug, LLDB, CUDA-GDB, MODULAR_DEBUG), NVIDIA compute-sanitizer (memcheck/racecheck/synccheck/initcheck), and macOS SDK/LLDB workarounds. Use when writing, editing, or reviewing Mojo code (including examples in explanations), debugging Mojo CPU/GPU programs, hunting GPU memory errors/races/deadlocks, or when the Mojo toolchain or LLDB on macOS reports Crashpad or Python formatter errors.
---

# Mojo

## Style preferences

### Spell out unsafe wildcard origins

When a wildcard origin is needed, prefer the explicit unsafe name:

| Prefer | Instead of |
| --- | --- |
| `MutUnsafeAnyOrigin` | `MutAnyOrigin` |
| `ImmUnsafeAnyOrigin` | `ImmutAnyOrigin` |

Keep `Unsafe` visible. These origins weaken lifetime and exclusivity checking;
the shorter aliases hide that important signal. Explicit unsafe naming is
consistent with Mojo's standard library and builtins.

This is a naming preference for wildcard origins, not a reason to replace a
tracked origin with an unsafe one.

## References

- [references/debugging.md](references/debugging.md) — `mojo debug`, LLDB and
  CUDA-GDB workflows, env vars, VS Code launch configs, GPU debugging playbook.
- [references/compute-sanitizer.md](references/compute-sanitizer.md) —
  `compute-sanitizer` tools, options, output reading, VS Code task, Mojo
  specifics.

## Toolchain workarounds

For macOS Mojo SDK (observed on 1.1.0, Pixi/conda environments) LLDB startup
errors — `Failed to initialize Crashpad` /
`unable to locate crashpad handler executable`, or
`This script interpreter does not support importing modules` — see
[references/macos-sdk-workarounds.md](references/macos-sdk-workarounds.md).

# macOS Mojo SDK workarounds

Observed on the macOS Mojo 1.1.0 SDK installed through Pixi. Both workarounds
edit files inside the installed environment, so SDK updates or environment
recreation may overwrite them. Recheck after upgrading, and verify the problem
still exists before reapplying. `$ENV` below means the environment prefix
(`$CONDA_PREFIX`, e.g. `<project>/.pixi/envs/default`).

## Crashpad handler lookup

Symptom: LLDB plugin initialization reports `Failed to initialize Crashpad`
with `unable to locate crashpad handler executable`, although the handler
exists.

For this exact lookup failure, check that `$ENV/bin/modular-crashpad-handler`
exists, then add or update this section in `$ENV/share/max/modular.cfg`:

```ini
[crash_reporting]
handler_path = <absolute path of $ENV>/bin/modular-crashpad-handler
```

Use the environment's actual absolute path; update it if the checkout or
environment moves. The explicit path removed the warning in a target-free LLDB
plugin-load check; crash capture and upload were not tested.

Crashpad is crash-reporting infrastructure used beyond interactive debugging,
including by the Mojo compiler and runtime components. This setting repairs
handler lookup for components that read this configuration; it does not ensure
that every standalone program or GPU failure produces a report. It does not
repair the underlying crash or change program correctness.

## Unsupported LLDB Python formatter imports

Symptom: `This script interpreter does not support importing modules` at
startup. The SDK's LLDB reports that it was built without scripting language
support, but `$ENV/bin/mojo-lldb-dap` unconditionally imports
`lldbDataFormatters.py` and `mlirDataFormatters.py`.

Disabling those two `--pre-init-command` arguments removes the errors (confirmed
by the user). Keep any explanatory comments above the command and use:

```bash
#!/bin/bash
# Python formatter imports disabled: bundled LLDB has no scripting support.
exec "$CONDA_PREFIX/bin/_mojo-lldb-dap" "$@"
```

Do not insert commented lines inside a backslash-continued command: doing so
can stop `"$@"` from being forwarded. This workaround skips the optional
Python formatters; it does not enable Python scripting or disable the native
Mojo debugger plugin.

The wrapper is supplied by the installed `mojo` package, not authored by the
project. Each environment has its own copy, and SDK updates or recreation may
overwrite edits. Recheck scripting support before reapplying to a newer SDK.

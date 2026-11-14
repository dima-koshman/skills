# Debugging Mojo (CPU and GPU)

Sources: mojo-gpu-puzzles Puzzle 9 (`book/src/puzzle_09/`, `problems/p09`),
its `.vscode/launch.json`, [Mojo debugging docs](https://mojolang.org/docs/tools/debugging/),
[GPU debugging guide](https://max.modular.com/gpu/debugging/), and the
[CUDA-GDB manual](https://docs.nvidia.com/cuda/cuda-gdb/index.html).
For LLDB startup errors on macOS see [macos-sdk-workarounds.md](macos-sdk-workarounds.md).
For memory/race/sync bugs without a debugger see [compute-sanitizer.md](compute-sanitizer.md).

## Rule one: don't debug optimized code

```bash
mojo build -O0 -g program.mojo -o program_debug
```

`-O0` keeps variables/structure, `-g` adds debug symbols. Source files given
directly to `mojo debug` already include debug info. Without symbols LLDB says
`use of undeclared identifier`.

## Four ways to launch

| Goal | Command |
| --- | --- |
| Host (CPU) code from source, LLDB | `mojo debug prog.mojo` |
| GPU kernels from source, CUDA-GDB | `mojo debug --cuda-gdb --break-on-launch prog.mojo` |
| Host code from binary, LLDB | `mojo debug prog_debug` |
| GPU kernels from binary, CUDA-GDB | `mojo debug --cuda-gdb --break-on-launch prog_debug` |

- Program flags go after the file: `mojo debug --cuda-gdb --break-on-launch p09.mojo --first-case`.
- Add `-I .` to import local packages (e.g. `mojo debug -I . solutions/p01/p01.mojo`).
- `--break-on-launch` is **required** for CUDA-GDB sessions: it stops at kernel
  launch so GPU breakpoints can be placed.
- `--vscode` (with the Mojo extension) opens the session in VS Code; with
  `--pid`/`--process-name` it attaches to a running process.
- `-D NAME` defines a compile-time name for `comptime if is_defined["NAME"]()`
  blocks (debug-only code).
- Source mode runs the program in-process, so frames may be JIT-labelled;
  binary mode gives cleaner output and repeatability.

## Environment variables

| Variable | Effect |
| --- | --- |
| `MODULAR_DEBUG=device-sync-mode` | Synchronize after every device op so CUDA errors are attributed to the real failing call (the error text itself suggests this) |
| `MODULAR_DEBUG=stack-trace-on-error` | Collect a stack trace when an error is raised |
| `MODULAR_DEVICE_CONTEXT_MEMORY_MANAGER_SIZE_PERCENT=0` | Disable buffer caching so OOB accesses are exposed (sanitizer) |
| `CUDBG_USE_LEGACY_DEBUGGER=1` | Use CUDA-GDB's classic backend if the connection drops (also `"legacyDebugger": true` in `launch.json`) |

For symbolicated crash traces: `mojo build` with debug info
(`-debug-level=line-tables` at minimum), then run the binary separately.

## Setup (NVIDIA only)

- CUDA Toolkit ≥ 12.4, `cuda-gdb` on `$PATH`. Conda's `cuda-gdb` package alone
  isn't sufficient; link the system toolkit's binaries into the env
  (`cuda-gdb-minimal`, `cuda-gdb-python3.X-tui`) — the puzzles repo does this
  with `scripts/setup-cuda-gdb.sh` looking at `$CUDA_HOME`, `/usr/local/cuda`,
  `/opt/cuda`, then `PATH`.
- Verify: `nvidia-smi`, `mojo debug --help` (should list `--cuda-gdb`),
  `cuda-gdb --version`.
- Limits: NVIDIA GPUs only; MAX custom-op kernels can't be debugged (only Mojo
  GPU code launched via `gpu.host`); CUDA-GDB has very limited support for
  Mojo CPU code (use LLDB for host code).

## VS Code (`.vscode/launch.json`)

```jsonc
{
  "type": "mojo-lldb",            // host code; "mojo-cuda-gdb" for GPU kernels
  "request": "launch",
  "name": "Mojo: Debug current Mojo file",
  "mojoFile": "${file}",          // or "program": "<binary>" for prebuilt
  "args": [],
  "env": [
    "PATH=${workspaceFolder}/.pixi/envs/default/bin:${env:PATH}",
    "MODULAR_DEBUG=device-sync-mode"
  ],
  "cwd": "${workspaceFolder}",
  "runInTerminal": false
}
```

CUDA-GDB variant: `"type": "mojo-cuda-gdb"`, plus `"breakOnLaunch": true`
(and optionally `"legacyDebugger": true`). Other `mojo-lldb` extras seen:
`"disableASLR": false`. In the VS Code debug console, prefix raw CUDA-GDB
commands with a backtick (remove any extra trailing backtick the console adds).
The Nsight VS Code Edition extension is needed for GPU debugging in VS Code.

## LLDB cheatsheet (host code)

```text
(lldb) br set -n main          # breakpoint on function (also: br set -n <fn>)
(lldb) br list | br delete 1 | br disable 1
(lldb) run                     # start
(lldb) continue | step | next | finish
(lldb) print var               # value
(lldb) print ptr[0]            # deref
(lldb) print arr[0]@4          # first 4 elements
```

In source mode the first `run` may stop in startup code before your code
(`continue` to reach it).

## CUDA-GDB cheatsheet (GPU kernels)

Abbreviations: `r` run, `c` continue, `n` next, `s` step, `b` break, `p` print,
`l` list, `q` quit.

```text
(cuda-gdb) run                          # stops at kernel launch (--break-on-launch)
(cuda-gdb) info cuda kernels|blocks|threads   # threads show per-thread file:line -> spots divergence
(cuda-gdb) cuda kernel                  # list/switch active kernels
(cuda-gdb) cuda block (0,0) thread (1,0,0)    # switch focus; no args shows current
(cuda-gdb) cuda thread (1,0,0)
(cuda-gdb) break file.mojo:56           # breakpoint by file:line (reliable)
(cuda-gdb) break kernel if i == 0       # conditional on a LOCAL variable
(cuda-gdb) print i                      # local thread index
(cuda-gdb) print a[i]                   # this thread's element
(cuda-gdb) print output.ptr[0]@4        # first 4 elements (TileTensor: use .ptr)
(cuda-gdb) watch arr[i] | rwatch arr[i] # break on write / read
(cuda-gdb) info registers $R0 $R1
```

Caveats (from the docs and the puzzles):
- `thread_idx.x`, `block_idx.x` and similar built-ins **do not evaluate**;
  capture them in a local (`var i = thread_idx.x`) and print that.
- Use `next`, not `step` (step dives into internals), and don't step far past
  the end of the kernel or you lose CUDA context. Stepping on GPU is
  unreliable in general; prefer breakpoints + `continue`.
- A breakpoint set before launch can land in a CPU function; `continue` to
  reach the GPU location. Docs say symbol breakpoints (`break kernel_name`) are
  not supported — use `file:line`; the puzzles report `break kernel` working in
  some versions, so try it but fall back to file:line.
- Other threads may already have run ahead; a thread's output slot can already
  be written when you inspect it.
- Use `print ptr[0]@N` to compare arrays at once; going one past the end
  (`@N+1`) exposes out-of-bounds reads.

## Diagnostic playbook (Puzzle 9 patterns)

| Symptom | Approach |
| --- | --- |
| `CUDA_ERROR_MISALIGNED_ADDRESS` / illegal address crash | Run with `MODULAR_DEBUG=device-sync-mode`; `mojo debug --cuda-gdb --break-on-launch`; at the stop, `print` every pointer parameter — a `0x0` (null) pointer is the culprit; test `a[i]` through each |
| Wrong results, no crash | Break in the kernel, step with `n`, print locals per thread (`cuda thread (..)`), compare `output[0]@N` to inputs; watch index math/off-by-one windows |
| Hang (deadlock) | Run, interrupt, `info cuda threads`: threads at different lines means divergence — a barrier not reached by all threads in the block. `compute-sanitizer --tool synccheck` can flag the same thing without a debugger |
| Passing test but suspicious | `compute-sanitizer --tool memcheck` (see compute-sanitizer.md) |
| Wrong shared-memory sums | `racecheck`; check unsynchronized `+=` on shared memory |

Barrier rule: every thread in a block must reach the same `barrier()`.
Conditional barriers are the classic deadlock.

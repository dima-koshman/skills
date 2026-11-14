# compute-sanitizer with Mojo GPU programs

NVIDIA-only (CUDA Toolkit; in pixi it comes from `cuda-toolkit = "12.*"`).
Sources: mojo-gpu-puzzles Puzzle 10 (`problems/p10`, `book/src/puzzle_10/`),
its VS Code task and `solutions/sanitizer.sh`, and the
[Compute Sanitizer docs](https://docs.nvidia.com/compute-sanitizer/ComputeSanitizer/index.html).

## Basic invocation

```bash
MODULAR_DEVICE_CONTEXT_MEMORY_MANAGER_SIZE_PERCENT=0 \
MODULAR_DEBUG=stack-trace-on-error \
  pixi run compute-sanitizer --tool memcheck mojo path/to/file.mojo [--program-flag]
```

- `MODULAR_DEVICE_CONTEXT_MEMORY_MANAGER_SIZE_PERCENT=0` disables the device
  context's buffer cache/pool. Without it, small out-of-bounds accesses land
  inside the big pooled allocation and memcheck does not see them. Use it for
  **memcheck** at least.
- `MODULAR_DEBUG=stack-trace-on-error` makes Mojo print a stack trace on
  unhandled errors (useful for the failing assert after a race).
- Run the sanitizer on `mojo file.mojo` (JIT) or on a binary built with
  `mojo build -O0 -g` (better symbols/line info).

## Which tool for which bug

| Tool | Detects | Notes |
| --- | --- | --- |
| `memcheck` (default) | Out-of-bounds/misaligned global, local, shared accesses; hardware exceptions; CUDA API errors; leaks (`--leak-check full`) | Run first; the other tools do no memory-access checking |
| `racecheck` | Shared-memory hazards: RAW, WAR, WAW | Shared memory only, not global memory |
| `synccheck` | Invalid `barrier()`/`__syncthreads`/`__syncwarp` use, e.g. a conditional barrier not reached by all threads | Reports 0 for a plain data race: race ≠ sync bug |
| `initcheck` | Reads of uninitialized global memory (`--initcheck-address-space` for shared, `--track-unused-memory`) | |

## Reading the output

- Every line is prefixed `=========`. Memcheck prints `Invalid __global__
  read/write of size N bytes`, the kernel `+offset`, `by thread (x,y,z) in
  block (...)`, and how far past the nearest allocation the access was.
- **Final line is authoritative**: `ERROR SUMMARY: N errors` (memcheck,
  synccheck, initcheck) or `RACECHECK SUMMARY: N hazard(s) displayed (E errors,
  W warnings)` (racecheck). The two formats differ; parse both when scripting
  (racecheck's summary does not contain `ERROR SUMMARY`).
- One bad kernel access cascades into extra `CUDA_ERROR_LAUNCH_FAILED
  (error 719)` lines on later API calls (`cuStreamSynchronize`, `cuEventCreate`,
  `cuMemFreeAsync`); these count as errors but are symptoms.
- A test can **pass** while memcheck reports errors (out-of-bounds threads
  that happen to alias valid elements). Don't trust green output alone.
- Race hazard counts are *pairs of conflicting accesses*, not threads, and vary
  by interleaving.
- Hazard severity: ERROR (likely race), WARNING (may be intentional, e.g.
  warp-synchronous code), INFO; filter with `--print-level`.

### Known harmless noise with Mojo

At the start of sanitizer output you may see `close: Bad file descriptor`, a
stack dump and `intermediate process terminated by signal 11`. This is the
sanitizer's injection libraries conflicting with Mojo's process init; GPU
analysis still completes. Judge by the summary line and `Invalid`/`Race` lines.

## Useful options

| Option | Purpose |
| --- | --- |
| `--tool memcheck\|racecheck\|synccheck\|initcheck` | Pick the tool |
| `--leak-check full` | Report device memory leaks (off by default) |
| `--racecheck-report hazard\|analysis\|all` | Raw hazards vs analysis (default `analysis`) |
| `--show-backtrace yes\|host\|device\|no` | Host/device backtraces |
| `--error-exitcode N` | Non-zero exit when errors found (default 0, so CI never fails without this) |
| `--print-limit N` | Stop printing after N errors (default 100, 0 = unlimited) |
| `--log-file F` | Write report to a file (`--save` / `--xml` for machine-readable) |
| `--padding N` | Pad allocations to catch off-by-few out-of-bounds |
| `--launch-skip N --launch-count M` | Check only some kernel launches |
| `--kernel-name regex:...` / `--kernel-name-exclude` | Filter kernels |
| `--target-processes application-only` | Skip child processes (the `mojo` driver forks) |

Compile with line info (`-g`, or `-debug-level=line-tables`) to get source
lines in reports.

## VS Code task (reusable)

`.vscode/tasks.json` entry that prompts for tool and file:

```json
{
  "label": "Run cuda compute-sanitizer",
  "type": "shell",
  "command": "pixi run compute-sanitizer --tool ${input:sanitizerTool} mojo ${input:mojoFile}",
  "options": {
    "env": {
      "MODULAR_DEVICE_CONTEXT_MEMORY_MANAGER_SIZE_PERCENT": "0",
      "MODULAR_DEBUG": "stack-trace-on-error"
    }
  }
}
```

with `inputs`: `mojoFile` (`promptString`) and `sanitizerTool` (`pickString`,
options `memcheck`, `racecheck`, `synccheck`, default `memcheck`). Add
`initcheck` to the options if wanted. Program flags go after the file in the
`mojoFile` input (e.g. `problems/p10/p10.mojo --race-condition`).

## Worked example (Puzzle 10)

Program: `p10.mojo` takes exactly one flag.

```bash
# 1. Bounds bug: 3x3 threads over a 2x2 tensor, no guard. Test passes, memcheck finds 4 OOB reads + 3 cascade errors.
MODULAR_DEVICE_CONTEXT_MEMORY_MANAGER_SIZE_PERCENT=0 pixi run compute-sanitizer --tool memcheck mojo problems/p10/p10.mojo --memory-bug

# 2. Race bug: unsynchronized `shared_sum[0] += ...` (read-modify-write). Test fails with 0.0 instead of 6.0.
pixi run compute-sanitizer --tool racecheck mojo problems/p10/p10.mojo --race-condition
# synccheck on the same program: 0 errors -> it is a data race, not a barrier bug.
pixi run compute-sanitizer --tool synccheck mojo problems/p10/p10.mojo --race-condition
```

Fixes: guard `row < size and col < size` before global access; for the race,
a `barrier()` does **not** fix a concurrent read-modify-write — restructure so
one thread accumulates, or use atomics/reduction.

## Scripting over many files

Pattern from `solutions/sanitizer.sh` (parse both summary formats):

```bash
count=$(printf '%s\n' "$output" \
  | sed -n 's/.*RACECHECK SUMMARY: [0-9][0-9]* hazards* displayed (\([0-9][0-9]*\) error.*/\1/p' | head -n1)
[ -z "$count" ] && count=$(printf '%s\n' "$output" \
  | sed -n 's/.*ERROR SUMMARY: \([0-9][0-9]*\) error.*/\1/p' | head -n1)
```

Only trusting `ERROR SUMMARY` makes racecheck always look clean.

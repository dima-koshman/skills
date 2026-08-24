---
name: macos-kernel-task-cpu
description: >
  Use when kernel_task is eating CPU on macOS, or when the Mac is slow, beachballing,
  fans are loud, or Activity Monitor shows a huge kernel_task. kernel_task is never the
  root cause — it is a symptom of either thermal throttling or virtual-memory thrashing.
  This skill separates the two, then identifies which processes are driving it. All
  diagnostic commands are read-only and SafeToAutoRun; remediation kills apps or
  containers and requires explicit user approval.
---

# Diagnosing kernel_task CPU on macOS

## The one thing to understand first

`kernel_task` is not a process that "uses" CPU in the normal sense. High `kernel_task`
CPU means the kernel is doing one of two jobs, and they have opposite fixes:

| Cause | Mechanism | Fix direction |
| --- | --- | --- |
| **Thermal throttling** | The kernel deliberately parks cycles in `kernel_task` to make the CPU idle and cool down | Reduce heat: unplug hot chargers, improve airflow, find the process generating load |
| **VM thrashing** | The kernel is compressing, decompressing, and paging memory to and from swap | Reduce memory demand: kill or restart the memory hogs |

**Always determine which one before recommending anything.** They look identical in
Activity Monitor and the remedies do not overlap.

## Step 1 — Rule thermal in or out

```bash
pmset -g therm
```

`No thermal warning level has been recorded` and `No performance warning level has been
recorded` mean thermal is **not** the cause. Go to Step 2.

Non-zero `CPU_Scheduler_Limit` (below 100) or a recorded warning level means the machine
**is** throttling — investigate heat and the user-space process generating the load.

> **Do not run `pmset -g thermlog`.** It is a continuous sampler that never exits and
> will hang the tool call until it times out. `pmset -g therm` returns immediately.

## Step 2 — Check memory pressure and swap

```bash
sysctl vm.swapusage
memory_pressure | tail -12
top -l 1 -n 0 | head -8
```

Read three numbers from `top`'s header:

- `PhysMem: ... unused` — anything under a few hundred MB is exhaustion
- `PhysMem: ... compressor` — pages compressed to fit in RAM; multiple GB means severe pressure
- `vm.swapusage` `free` — approaching zero means swap is about to run out too

## Step 3 — Prove it is actively thrashing

Static numbers show pressure; only a delta proves ongoing churn. Counters in `vm_stat`
are cumulative since boot, so they must be sampled twice:

```bash
.agents/skills/macos-kernel-task-cpu/scripts/pagerate.sh 10
```

Sustained tens of MB/s in **both** directions is thrashing — the kernel is evicting pages
it immediately needs back. That read/write churn *is* the `kernel_task` CPU.

A near-zero rate means memory is tight but stable, and something else is the problem.

## Step 4 — Find what is consuming the memory

Resident size alone is misleading under pressure: `ps` RSS excludes compressed and
swapped-out pages, so a process holding 6 GB can report a few hundred MB. Use `top`'s
`MEM` column, which reflects the fuller footprint.

```bash
# Top consumers by real footprint
top -l 1 -n 15 -o mem -stats pid,command,mem,cpu

# Roll up by application group
.agents/skills/macos-kernel-task-cpu/scripts/footprint.sh Devin OrbStack claude
```

Electron apps fragment across dozens of helper processes, so count them:

```bash
pgrep -f Devin | wc -l
```

> **`ps -r` sorts by CPU, not memory** — use `ps -m` for memory.
> **`pgrep -c` does not exist on macOS** (BSD pgrep) — pipe to `wc -l`.
> The group rollup **double-counts shared memory** across Electron helpers, so treat it
> as a ranking, not an absolute total.

## Step 5 — Check containers separately

Container memory is charged to the VM helper process (OrbStack/Docker), so it appears as
one large opaque process. Break it down:

```bash
orbctl status
docker stats --no-stream --format 'table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.CPUPerc}}'
docker ps --format '{{.Names}}\t{{.Status}}\t{{.Image}}'
```

Long `Status` uptimes on stacks the user is not actively using are prime reclaim targets.

## Remediation — requires explicit approval

Never kill an editor or a long-running container without asking. Order by reclaim per
unit of disruption:

```bash
# 1. Restart the leaking app — usually the biggest win, cheapest to do
#    An Electron editor at 10+ GB across 80 processes after days of uptime is a leak,
#    not a working set. Quit and reopen it.

# 2. Stop container stacks not in use today
orb stop                              # whole VM, reclaims everything at once
docker compose -f <stack> down        # or one stack, keeping the rest up

# 3. Reboot — the only way to reclaim a swap file that has already ballooned
```

Swap does not shrink when memory is freed. After freeing memory, `vm.swapusage` `used`
stays high; what matters is that the paging **rate** from Step 3 drops to near zero.

## Verifying the fix

Re-run Step 3. The claim "resolved" requires the paging rate at or near zero and
`kernel_task` CPU back to single digits — not just an app having been closed.

## Findings on this machine — 2026-08-19

Diagnosis only; **no remediation was executed** (user approval was still pending).

MacBook Pro M1 Pro (`MacBookPro18,1`), 16 GB RAM, 13 days uptime.

| Signal | Value |
| --- | --- |
| `kernel_task` CPU | 209% |
| Load average | 12.8 (57% sys, 24% idle) |
| Free RAM | 66 MB |
| Compressor | 7.5 GB |
| Swap | 21.4 GB used of 22.5 GB — 1.1 GB free |
| Live paging | ~59 MB/s in, ~52 MB/s out, sustained |
| Thermal | no warning recorded — **ruled out** |

Demand, roughly 30 GB on a 16 GB machine:

| Source | Footprint | Notes |
| --- | --- | --- |
| Devin (VS Code fork) | ~16.3 GB | 80 processes — dominant consumer |
| OrbStack | ~6.5 GB | 8 containers, up 5–7 days |
| Microsoft Teams | ~1.6 GB | |
| Safari / WebKit | ~1.1 GB | |
| WindowServer | ~1.0 GB | inflated by the paging itself |
| claude CLI | ~0.9 GB | 3 instances |

Containers: full self-hosted Langfuse stack (web, worker, clickhouse, postgres, redis,
minio) plus LiteLLM and its pgvector postgres. `langfuse-clickhouse-1` was independently
burning ~80% CPU — a separate user-space issue worth checking on its own.

Recommended order was: restart Devin, then `orb stop` if the stacks were not needed.

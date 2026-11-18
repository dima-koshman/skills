---
type: Concept
title: OS CPU Scheduling
aliases:
- Fair-Share Scheduling
- Fair Scheduling
description: How an OS shares CPU time, through preemption, fair shares and priorities, and how weights differ from
  limits, using Linux as the example.
tags:
- software-engineering
- infrastructure
- operating-systems
parent: /software-engineering/infrastructure.md
related:
- /ai-engineering/compute/gpu-sharing/gpu-scheduling.md
- /ai-engineering/compute/gpu-sharing/mps.md
- /ai-engineering/compute/gpu-sharing/accelerator-sharing.md
sources:
- id: linux-sched-man
  resource: https://man7.org/linux/man-pages/man7/sched.7.html
  title: sched(7), Linux manual page
  author: Linux man-pages project
- id: linux-cfs
  resource: https://docs.kernel.org/scheduler/sched-design-CFS.html
  title: CFS Scheduler
  author: Linux kernel documentation
- id: linux-eevdf
  resource: https://docs.kernel.org/scheduler/sched-eevdf.html
  title: EEVDF Scheduler
  author: Linux kernel documentation
- id: linux-nice
  resource: https://docs.kernel.org/scheduler/sched-nice-design.html
  title: Scheduler Nice Design
  author: Linux kernel documentation
- id: linux-cgroup-v2
  resource: https://docs.kernel.org/admin-guide/cgroup-v2.html
  title: Control Group v2
  author: Linux kernel documentation
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-05T15:56:39+04:00'
---

An OS scheduler decides which runnable thread gets a CPU next. On Linux it does this preemptively: a running thread
can be stopped without its consent.[^linux-sched-man]

## Fair share

**Fair share** means each runnable task gets a proportional share of CPU time, not a fixed turn. CFS models an ideal
CPU where two tasks each run at 50% at the same moment, and approximates that on real hardware by always running
the task with the least virtual runtime so far.[^linux-cfs]

EEVDF, which Linux began moving to in version 6.6, keeps the idea and adds a "lag" value. Positive lag means a task
is owed CPU time, and negative means it has used more than its portion.[^linux-eevdf]

Shares only apply among tasks that want the CPU. A sleeping task takes nothing, and the others use its time.

## How priority relates to it

"Priority" means two different things on Linux, and only one of them works through fair share.

| | Nice value | Real-time priority |
| --- | --- | --- |
| Applies to | Normal tasks (`SCHED_OTHER`, `SCHED_BATCH`)[^linux-sched-man] | `SCHED_FIFO`, `SCHED_RR`[^linux-sched-man] |
| Range | -20 to 19 | 1 to 99[^linux-sched-man] |
| Effect | Changes a task's **share** | Decides **who runs**, strictly |
| Low-priority task | Still makes progress | Waits while higher ones are runnable |

So nice is a weight. Each step changes the scheduler's favor by a factor of 1.25,[^linux-sched-man] and one level
apart gives about a 55% to 45% split at any starting level.[^linux-nice] Five levels apart is about 3:1, or 75% to
25% (our arithmetic, 1.25^5).

Real-time priority sits above all of this. Real-time threads always beat normal threads, and a higher static
priority preempts a running thread immediately.[^linux-sched-man] Fair share only decides among normal tasks at
static priority 0.

## Weights versus limits

Cgroups show the same split for groups of tasks.[^linux-cgroup-v2]

- **`cpu.weight`** divides CPU among active children by ratio. It is work-conserving: an idle group's share goes to
  the others.
- **`cpu.max`** is a limit: at most `$MAX` in each `$PERIOD`, even if the CPU is otherwise idle.

This distinction carries over to GPUs. [MPS](/ai-engineering/compute/gpu-sharing/mps.md) thread percentages are limits. Its
weighted timeslicing looks like a weight but only sets slice length between servers, and NVIDIA says it does not
guarantee a share of utilization.

[^linux-sched-man]: sched(7), scheduling policies and the nice value.
[^linux-cfs]: Linux kernel docs, CFS Scheduler.
[^linux-eevdf]: Linux kernel docs, EEVDF Scheduler.
[^linux-nice]: Linux kernel docs, Scheduler Nice Design.
[^linux-cgroup-v2]: Linux kernel docs, Control Group v2.

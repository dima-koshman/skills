---
type: Concept
title: Why GPU Scheduling Differs from CPU Scheduling
aliases:
- GPU Scheduling
- GPU Context Switching
- Compute Preemption
description: GPUs switch between threads constantly but between programs rarely, because they keep tens of MB of
  thread state on-chip; data transfer is not the reason.
tags:
- ai-engineering
- compute
- gpu
parent: /ai-engineering/compute/gpu-sharing.md
related:
- /ai-engineering/compute/simd-simt.md
- /ai-engineering/compute/gpu-sharing/mps.md
- /software-engineering/infrastructure/cpu-scheduling.md
- /ai-engineering/compute/performance-regimes.md
- /ai-engineering/compute/unified-memory.md
sources:
- id: cuda-hw-multithreading
  resource: https://docs.nvidia.com/cuda/archive/12.2.0/cuda-c-programming-guide/index.html#hardware-multithreading
  title: CUDA C++ Programming Guide 12.2, section 4.2 Hardware Multithreading
  author: NVIDIA
- id: hopper-tuning
  resource: https://docs.nvidia.com/cuda/hopper-tuning-guide/index.html
  title: NVIDIA Hopper Tuning Guide
  author: NVIDIA
- id: hopper-in-depth
  resource: https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/
  title: NVIDIA Hopper Architecture In-Depth
  author: NVIDIA
- id: pascal-whitepaper
  resource: https://images.nvidia.com/content/pdf/tesla/whitepaper/pascal-architecture-whitepaper.pdf
  title: NVIDIA Tesla P100 whitepaper (WP-08019-001)
  author: NVIDIA
- id: linux-xstate
  resource: https://docs.kernel.org/arch/x86/xstate.html
  title: Using XSTATE features in user space applications
  author: Linux kernel documentation
- id: mps-architecture
  resource: https://docs.nvidia.com/deploy/mps/latest/architecture.html
  title: Multi-Process Service, Architecture
  author: NVIDIA
- id: mps-v3-interface
  resource: https://docs.nvidia.com/deploy/mps/latest/mpsv3-interface.html
  title: MPS v3 Interface
  author: NVIDIA
- id: chimera
  resource: https://cccp.eecs.umich.edu/papers/jasonjk-asplos15.pdf
  title: 'Chimera: Collaborative Preemption for Multitasking on a Shared GPU'
  author: Jason Jong Kyu Park, Yongjun Park, Scott Mahlke (ASPLOS 2015)
  last_modified: '2015-03-14T00:00:00Z'
- id: reef
  resource: https://www.usenix.org/conference/osdi22/presentation/han
  title: Microsecond-scale Preemption for Concurrent GPU-accelerated DNN Inferences
  author: Mingcong Han, Hanze Zhang, Rong Chen, Haibo Chen (OSDI 2022)
  last_modified: '2022-07-11T00:00:00Z'
- id: ptask
  resource: https://www.cs.utexas.edu/users/witchel/pubs/sosp11rossbach-ptask.pdf
  title: 'PTask: Operating System Abstractions To Manage GPUs as Compute Devices'
  author: Christopher Rossbach, Jon Currey, Mark Silberstein, Baishakhi Ray, Emmett Witchel (SOSP 2011)
  last_modified: '2011-10-23T00:00:00Z'
- id: hsa-sysarch
  resource: https://dci.dci-gitlab.cines.fr/webextranet/_downloads/8dc8354f3d5b601d7d668192ba92ffc3/HSA-SysArch-1.2.pdf
  title: HSA Platform System Architecture Specification 1.2
  author: HSA Foundation
  last_modified: '2018-05-02T00:00:00Z'
- id: mi300a
  resource: https://instinct.docs.amd.com/projects/amdgpu-docs/en/latest/gpu-partitioning/mi300a/overview.html
  title: AMD Instinct MI300A APU Overview
  author: AMD
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-11T09:28:41+04:00'
---

Both are compute units, but they keep different amounts of state and are built for different goals. A CPU is built to
switch between programs cheaply. A GPU is built to switch between thousands of threads of one workload for free, which
makes switching between programs expensive.

## It is not about loading data

GPU memory is not time-sliced. Each process's allocations stay in GPU memory while other processes take turns, so a
context switch does not reload data over PCIe. ([MPS](/ai-engineering/compute/gpu-sharing/mps.md) covers this sharing.) Data
transfer is a real cost for GPU programs, but it is paid when data moves in, not at each switch.

The cost that matters is **on-chip state**: registers and shared memory, which must be saved to switch away from
running work.

## How much state there is

| | CPU thread | H100 SXM5 GPU |
| --- | --- | --- |
| Registers | Kilobytes; even 2KB is too small once AMX is used[^linux-xstate] | 64K 32-bit registers per SM[^hopper-tuning], which is 256KB |
| Fast local memory | Caches, not saved on a switch | Up to 228KB shared memory per SM[^hopper-tuning] |
| Units | One core | 132 SMs[^hopper-in-depth] |
| Total to save | Kilobytes | About 33MB of registers plus up to 30MB of shared memory when full |

The GPU totals are our arithmetic (132 × 256KB and 132 × 228KB). That is roughly ten thousand times a CPU thread's
state, and saving it takes real time.

## GPUs schedule all the time, just not programs

GPUs do schedule constantly, within whatever is resident. Every warp's program counter and registers stay on-chip for
the warp's whole life, so "switching from one execution context to another has no cost", and a warp scheduler picks a
ready warp at every instruction issue.[^cuda-hw-multithreading] This is how a GPU hides memory latency: while one warp
waits, another runs. ([SIMD and SIMT](/ai-engineering/compute/simd-simt.md) covers warps.)

So the two processors put their cheap switching in different places:

| | Cheap switching | Expensive switching |
| --- | --- | --- |
| CPU | Between programs, by the OS | Rare: the core runs one thread, two with SMT |
| GPU | Between resident warps, every instruction | Between programs: evicting resident state |

## Preemption came late

GPUs could not stop running work mid-way until Pascal (2016). Kepler and Maxwell preempted only at thread block
granularity, so all threads of a block had to finish before the GPU could switch contexts. Pascal added preemption at
instruction-level granularity.[^pascal-whitepaper]

Before that, sharing was effectively cooperative in the OS sense. Long kernels could make the display unresponsive
until they timed out, so programmers had to split work into small pieces themselves.[^pascal-whitepaper]

Even now, process-level slices are long. The MPS v3 base timeslices are 10, 20 and 50 ms,[^mps-v3-interface] and the
GPU's time-sliced scheduler still cannot run work from different contexts at the same time.[^mps-architecture]

## Who runs the scheduler

A CPU's OS scheduler runs on the CPU itself. A GPU does not run an OS. The driver feeds it queues of commands, and
schedulers in the GPU pick from those queues: a concurrent scheduler within one context and a time-sliced one between
contexts.[^mps-architecture] The policy lives in hardware and firmware, not in a kernel you can tune, which is why GPU
sharing controls are coarse.

## The root cause is how each hides latency

Expensive switching is a consequence, not the root. Memory takes hundreds of cycles to answer, and each processor
deals with that differently. (This section is our reasoning.)

- **A CPU shortens the wait** for one thread, with caches, prediction and out-of-order execution. Each thread needs
  little state, so switching between threads is cheap.
- **A GPU fills the wait** with other threads. To keep the units busy, it needs enough threads in flight to cover the
  latency, which is Little's law: work in flight equals latency times throughput. All those threads' state has to
  live on-chip, and that is the state that makes switching expensive.

So the large state is the mechanism a GPU uses to be fast, not overhead it carries.

## Could a scheduler account for the cost?

Yes, and research schedulers do. The toolbox is the same as a CPU's; the costs change which tool wins.

- **Chimera** (ASPLOS 2015) starts from the point that CPU-style context switching "incurs substantial overhead due
  to the large context in GPUs". It picks, per SM, between context switching, draining (letting blocks finish) and
  flushing (dropping idempotent work to rerun later). It met a 15 µs preemption target for all but 0.2% of
  requests.[^chimera]
- **REEF** (OSDI 2022) notes that DNN inference kernels are mostly idempotent, so it kills and restarts best-effort
  kernels instead of saving their state, and launches a real-time kernel in a few microseconds.[^reef]

These tricks use knowledge of the workload: work that is safe to rerun is cheap to preempt. That is why they live
in research systems and serving engines rather than in a general driver.

CPUs hit the same problem when their state grows. Linux does not allocate the large XSTATE buffers that AMX needs
by default, and traps the first AMX instruction to set them up.[^linux-xstate] That is a CPU scheduler accounting
for GPU-like state.

At a high level the scheduling can converge: both machines time-share and space-share, with weights and caps. What
differs is the mix. With 132 SMs and expensive switches, dividing space is cheaper than dividing time, so GPUs lean
on partitions ([MIG](/ai-engineering/compute/gpu-sharing/mig.md), static SM partitions) where CPUs lean on time slices.

## Would co-design make them alike?

It removes the accidental differences, but not the fundamental one.

| Difference | Kind | Status |
| --- | --- | --- |
| OS treats the GPU as an I/O device | Circumstantial | PTask (2011) argued OSes should manage GPUs as compute devices, since they cannot guarantee fairness otherwise[^ptask] |
| Separate memory and address spaces | Circumstantial | HSA requires shared virtual memory[^hsa-sysarch]; MI300A CPU and GPU share one address space and HBM[^mi300a]; see [unified memory](/ai-engineering/compute/unified-memory.md) |
| Dispatch through a driver | Circumstantial | HSA requires user-mode queues[^hsa-sysarch] |
| Progress across many workloads | Circumstantial | HSA requires agents to progress multiple queues at once, possibly by context switching to time-share[^hsa-sysarch] |
| No preemption | Circumstantial | Fixed in Pascal (2016)[^pascal-whitepaper] |
| Latency strategy and on-chip state | Fundamental | Unchanged |

The strongest evidence is what co-designed chips look like. The MI300A was designed as one package with shared
memory, and it still contains 24 Zen 4 CPU cores and 228 GPU compute units as separate kinds of units.[^mi300a]
Co-design produced two kinds of processor that share everything around them, not one merged processor.

## In short

The difference comes from the design goal, not from the data path. CPUs optimize latency for many unrelated programs.
GPUs optimize throughput for one massively parallel workload, and keeping that workload's state on-chip is what makes
switching away from it expensive. (This framing is ours.)

[^cuda-hw-multithreading]: CUDA C++ Programming Guide 12.2, section 4.2.
[^hopper-tuning]: NVIDIA Hopper Tuning Guide, Occupancy.
[^hopper-in-depth]: NVIDIA developer blog, Hopper Architecture In-Depth.
[^pascal-whitepaper]: Tesla P100 whitepaper, Compute Preemption.
[^chimera]: Park et al., ASPLOS 2015, abstract and introduction.
[^reef]: Han et al., OSDI 2022, introduction.
[^ptask]: Rossbach et al., SOSP 2011, sections 1 and 2.3.
[^hsa-sysarch]: HSA Platform System Architecture Specification 1.2, sections 2.1, 2.8 and 2.9.
[^mi300a]: AMD GPU Driver documentation, MI300A APU Overview.
[^linux-xstate]: Linux kernel docs, x86 XSTATE.
[^mps-architecture]: NVIDIA MPS documentation, Architecture.
[^mps-v3-interface]: NVIDIA MPS documentation, MPS v3 Interface, Weighted Timeslicing.

---
type: Concept
title: NVIDIA Multi-Process Service (MPS)
aliases:
- MPS
- CUDA MPS
description: A CUDA runtime service that lets kernels from different processes run on a GPU at the same time,
  where native multi-process sharing only takes turns on the whole GPU.
tags:
- ai-engineering
- compute
- gpu
parent: /ai-engineering/compute/gpu-sharing.md
related:
- /ai-engineering/compute/gpu-sharing/gpu-scheduling.md
- /ai-engineering/compute/software-stack/cuda.md
- /ai-engineering/compute/simd-simt.md
- /ai-engineering/compute/performance-regimes.md
- /ai-engineering/compute/serving/parallelism.md
- /ai-engineering/compute/gpu-sharing/mig.md
- /ai-engineering/compute/gpu-sharing/accelerator-sharing.md
- /software-engineering/infrastructure/cpu-scheduling.md
- /ai-engineering/compute/gpu-sharing/run-ai.md
- /ai-engineering/compute/serving/triton-inference-server.md
- /ai-engineering/compute/serving/vllm.md
sources:
- id: cuda-5-5-notes
  resource: https://developer.download.nvidia.com/compute/cuda/5_5/rel/docs/CUDA_Toolkit_Release_Notes.pdf
  title: NVIDIA CUDA Toolkit v5.5 Release Notes
  author: NVIDIA
  last_modified: '2013-07-12T21:25:36-07:00'
- id: mig-concepts
  resource: https://docs.nvidia.com/datacenter/tesla/mig-user-guide/latest/concepts.html
  title: MIG User Guide, Concepts
  author: NVIDIA
- id: cuda-device-attrs
  resource: https://docs.nvidia.com/cuda/cuda-runtime-api/group__CUDART__TYPES.html
  title: CUDA Runtime API, Data types
  author: NVIDIA
- id: linux-sched-man
  resource: https://man7.org/linux/man-pages/man7/sched.7.html
  title: sched(7), Linux manual page
  author: Linux man-pages project
- id: k8s-device-plugin
  resource: https://github.com/NVIDIA/k8s-device-plugin
  title: NVIDIA device plugin for Kubernetes
  author: NVIDIA
- id: mps-v3-interface
  resource: https://docs.nvidia.com/deploy/mps/latest/mpsv3-interface.html
  title: MPS v3 Interface
  author: NVIDIA
- id: mps-v3-memory
  resource: https://docs.nvidia.com/deploy/mps/latest/mpsv3-memory-partitioning.html
  title: MPS v3 Memory Partitioning
  author: NVIDIA
- id: mps-v3-namespaces
  resource: https://docs.nvidia.com/deploy/mps/latest/mpsv3-namespaces.html
  title: MPS v3 Namespaces
  author: NVIDIA
- id: mps-architecture
  resource: https://docs.nvidia.com/deploy/mps/latest/architecture.html
  title: Multi-Process Service, Architecture
  author: NVIDIA
- id: mps-when-to-use
  resource: https://docs.nvidia.com/deploy/mps/latest/when-to-use-mps.html
  title: Multi-Process Service, When to Use MPS
  author: NVIDIA
- id: mps-common-tasks
  resource: https://docs.nvidia.com/deploy/mps/latest/common-tasks.html
  title: Multi-Process Service, Common Tasks
  author: NVIDIA
- id: mps-env-vars
  resource: https://docs.nvidia.com/deploy/mps/latest/appendix-environment-variables.html
  title: Multi-Process Service, Environment Variables
  author: NVIDIA
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-05T15:56:39+04:00'
---

Several processes can use one GPU without MPS. They just cannot run compute kernels at the same moment.
MPS removes that limit: "the GPU will allow kernel launches from different processes to run
concurrently".[^mps-when-to-use]

| | Native multi-process | With MPS |
| --- | --- | --- |
| Compute kernels from different processes | Take turns: each gets a time slice on the whole GPU | Can run concurrently |
| Scheduling across processes | Time-sliced between CUDA contexts | Concurrent within a server; time-sliced between servers |
| A process that fills 20% of the GPU | Still holds the whole GPU during its slice | Leaves the rest for other clients |
| `nvidia-smi` shows | Each process | The MPS server, not the clients |
| Fatal GPU fault | Sources conflict, see below | Reaches every client sharing that GPU[^mps-when-to-use] |

NVIDIA's own docs disagree on native fault behavior. The MIG guide lists fault isolation as a property of a GPU
context,[^mig-concepts] while the Kubernetes device plugin says time-sliced workloads share a fault domain, so "if
one workload crashes, they all do".[^k8s-device-plugin] The second is the safer assumption.

## Why native sharing wastes capacity

The GPU has a time-sliced scheduler for work from different CUDA contexts, and each process normally has
its own context. Work queues from different contexts cannot run on the compute engine concurrently, which
"can cause underutilization of the GPU's compute resources".[^mps-architecture] Inside one context,
Hyper-Q schedules work concurrently.[^mps-architecture]

The CPU comparison is where the intuition goes wrong. An OS can place processes on different cores at the
same instant. A GPU without MPS is closer to a machine that gives all its cores to one process, then all
of them to the next. (This analogy is ours, not NVIDIA's.) NVIDIA's wording is that each process gets "a
serially scheduled time-slice on the whole GPU".[^mps-architecture]

This still works well for a shared class or lab GPU. Memory is not time-sliced, so every process's allocations
stay in place and memory capacity is the hard limit. Compute only collides when several jobs are busy at the
same moment, and bursty work rarely does. (Our reasoning, not a doc claim.)

## History

MPS shipped as a new feature in CUDA 5.5 in July 2013, aimed at letting several MPI processes run concurrently
on one GPU.[^cuda-5-5-notes] So it is much older than AI serving: it came from HPC, where one job is split into
many cooperating processes. Volta later moved the server out of the critical execution path.[^mps-architecture]

## How MPS works

- **Client runtime:** built into `libcuda.so`, so applications need no code change.[^mps-architecture]
- **Control daemon** (`nvidia-cuda-mps-control`): starts and stops the server and connects clients to it.
  Legacy v2, still the default protocol, runs one server per UID and serializes users; v3 supports multiple named
  servers at once.[^mps-v3-interface]
- **Server** (`nvidia-cuda-mps-server`): the clients' shared connection to the GPU and the owner of its
  scheduling resources.[^mps-architecture]

MPS is not a dispatcher on the hot path. Clients submit work directly to the GPU, and on Volta the server
"stays out of the critical execution path".[^mps-architecture] Client address spaces stay fully
isolated.[^mps-when-to-use]

## When it helps

NVIDIA's test: MPS is "useful when each application process does not generate enough work to saturate
the GPU". Examples are small grids and strong scaling, where each process has too little work to fill the
GPU.[^mps-when-to-use]

It follows that MPS adds little when one process already saturates the GPU, as a busy serving engine
holding the whole device would. Running several small model replicas on one GPU is the kind of case it
fits. Both are our inference from NVIDIA's test; the docs have no "when not to use" section.

## What is shared and what is isolated

MPS shares compute more than it isolates it. By default, clients are separated by address space and little else.

| Resource | Under MPS | Can it be separated? |
| --- | --- | --- |
| GPU address space | Each client has its own, fully isolated[^mps-when-to-use] | Already is |
| Memory capacity | One shared pool[^mig-concepts] | Yes, with limits |
| Memory bandwidth and caches | Shared[^mig-concepts] | No |
| SMs | Every client can use all of them by default, and kernels from different clients may run on the same SM[^mps-when-to-use] | Yes, with static partitions |
| Scheduling hardware | Shared[^mig-concepts] | No |
| Fatal faults | Reach all clients sharing that GPU[^mps-when-to-use] | Partly, with static partitions[^mps-common-tasks] |

So processes share the physical memory pool but cannot read each other's data. Sharing data takes explicit CUDA
IPC.[^mig-concepts]

## Resource limits

| Control | Enforces | Does not do |
| --- | --- | --- |
| `CUDA_MPS_ACTIVE_THREAD_PERCENTAGE` | Caps a client's share of threads, and concentrates its work on fewer SMs[^mps-when-to-use] | Reserve anything; other clients can still land on those SMs[^mps-when-to-use] |
| `CUDA_MPS_PINNED_DEVICE_MEM_LIMIT` | Hard cap on allocations, per GPU; over it returns out of memory[^mps-when-to-use] | Limit bandwidth; clients can only lower it further[^mps-when-to-use] |
| v3 memory partitioning | Soft and hard limits per cgroup, covering all device memory[^mps-v3-memory] | Run on MIG; needs CUDA 13.4+ and cgroup v2[^mps-v3-memory] |
| Static SM partitions (Ampere+) | Exclusive SMs, in chunks of 8 on Hopper+[^mps-common-tasks] | Lend idle SMs, unless v3 load balancing is on[^mps-common-tasks] |
| `CUDA_MPS_CLIENT_PRIORITY` | A performance hint[^mps-env-vars] | Guarantee execution order[^mps-env-vars] |

Under v3 memory partitioning, staying below the soft limit is guaranteed. Above it, allocations still succeed by
borrowing from others, but the client can be evicted or killed under real contention.[^mps-v3-memory] MPS v3
namespaces apply these settings to groups of clients on one server.[^mps-v3-namespaces]

Thread percentage also has a side benefit: each client's context storage scales with its available threads, so a
lower limit reduces memory footprint.[^mps-when-to-use]

Memory bandwidth has no limit here. That is the main gap against [MIG](/ai-engineering/compute/gpu-sharing/mig.md), which gives
each instance its own memory path, so a noisy neighbor under MPS can still slow you down.[^mig-concepts]

## Is it like CPU scheduling?

Only partly. Placing work from several processes on the hardware at once resembles an OS using many cores. But a
[CPU scheduler](/software-engineering/infrastructure/cpu-scheduling.md) is a fairness and protection layer, and MPS
adds little of that:

| | OS on a CPU | MPS on a GPU |
| --- | --- | --- |
| Who decides placement | OS scheduler | GPU hardware, by load balancing[^mps-when-to-use] |
| Fair shares | Enforced | None between clients of a server; caps only[^mps-when-to-use] |
| Pausing a running task | Yes, all scheduling is preemptive[^linux-sched-man] | Between servers by time-slicing; not documented between clients of one server |
| Priority | Enforced levels | Two levels, and only a hint[^mps-env-vars] |
| One process crashes | Others keep running | Clients on that GPU are told to exit[^mps-when-to-use] |

MPS behaves less like an OS running strangers' programs and more like threads of one trusted application, with
separate address spaces. (The comparison is ours.)

### What "co-operative" means

NVIDIA's word describes the applications, not the scheduling. It means processes that work together and trust
each other, commonly MPI jobs.[^mig-concepts] It is not cooperative scheduling, where a program must yield the
processor. MPS clients never yield anything: they submit kernels and the GPU hardware places them.

What applications are responsible for is behaving well, not yielding. Clients must exit after a fatal fault ("it is
the responsibility of the affected clients") and must not be killed with outstanding work.[^mps-when-to-use]

### Does MPS schedule at all?

Not per kernel. On Volta and later, a client's kernels do not go through MPS: clients submit directly, and the GPU
hardware schedules them. The server's job is to "mediate the remaining shared resources required to ensure
simultaneous scheduling".[^mps-architecture] So MPS sets up the conditions for concurrency and enforces limits,
then stays out of the way. Limits apply at set points, such as memory allocation and context creation, rather than
as a broker answering each request.[^mps-when-to-use]

### How MPS and time-slicing fit together

They work at two levels. MPS removes time-slicing between clients of one server, and the time-sliced scheduler still
runs between whatever remains.

| Who is sharing the GPU | What happens |
| --- | --- |
| Clients of one MPS server | Run concurrently, no time-slicing[^mps-when-to-use] |
| Two v3 servers on one GPU | Time-sliced, with configurable slice length[^mps-v3-interface] |
| Users under legacy v2 | Queued: the daemon runs one user's server at a time[^mps-architecture] |
| An MPS server and a non-MPS process | Time-sliced (our inference); NVIDIA recommends preventing this[^mps-when-to-use] |

NVIDIA recommends `EXCLUSIVE_PROCESS` mode so that the MPS server is "the single point of arbitration between all
CUDA processes for that GPU".[^mps-when-to-use]

**Weighted timeslicing** (v3, driver r620+) controls the between-servers level. `compute-policy` sets the base
duration: short 10 ms, medium 20 ms or long 50 ms. Each server's `timeslice-pct` scales it, so long at 50 gives
25 ms. `timeslice-yield-level` controls how aggressively the GPU switches. The percentage sets slice length and
"does not guarantee a percentage of GPU utilization".[^mps-v3-interface] Both base settings are fixed once any
server exists, and `timeslice-pct` cannot change while clients are attached.

### Can MPS pause a client?

Between servers, yes in effect: time-slicing switches the GPU between them. Between clients of one server, the docs
we read describe no way to. The tools there are caps, a priority hint and terminating a client. NVIDIA GPUs do have
compute preemption as a device feature,[^cuda-device-attrs] so the hardware is not the obstacle in principle. We found
no official statement on what happens to a long kernel from one client inside a server. Our reasoning is that SMs free up as a
kernel's blocks finish, so a long kernel crowds others out rather than locking them out, which is what thread
limits and static partitions are there to prevent.

## Costs and limits

- **Shared fate:** a fatal fault is reported to all clients on the affected GPUs, without naming the
  culprit, and new clients are rejected until those clients exit.[^mps-when-to-use] Under
  `-multiuser-server`, a fault can take down another user's client.[^mps-architecture] Static partitioning on driver r610+ gives partial
  isolation, not a guarantee.[^mps-common-tasks]
- **Clean exit required:** Ctrl-C or signals on a client are unsupported and can force a restart of the
  server and all clients. Use the control command to terminate a client.[^mps-when-to-use]
- **Tooling:** `cuda-gdb` works only without MPS; `compute-sanitizer` and CUPTI profilers work.[^mps-when-to-use]
- **Limits:** up to 60 client contexts per device at default settings, 64-bit
  applications only, Linux or QNX only, and no dynamic parallelism.[^mps-when-to-use]

## Not yet covered

Which GPUs MPS supports: the pages read do not list them. [MIG](/ai-engineering/compute/gpu-sharing/mig.md) compares the two and
covers running MPS on top of MIG; its docs give a client limit of 48, where the MPS docs say 60.

[^cuda-5-5-notes]: NVIDIA CUDA Toolkit v5.5 Release Notes, July 2013, section 1.7.1.
[^mig-concepts]: NVIDIA MIG User Guide, Concepts.
[^cuda-device-attrs]: CUDA Runtime API, `cudaDevAttrComputePreemptionSupported`.
[^linux-sched-man]: sched(7), scheduling policies.
[^k8s-device-plugin]: NVIDIA Kubernetes device plugin README, Shared Access to GPUs.
[^mps-v3-interface]: NVIDIA MPS documentation, MPS v3 Interface.
[^mps-v3-memory]: NVIDIA MPS documentation, MPS v3 Memory Partitioning.
[^mps-v3-namespaces]: NVIDIA MPS documentation, MPS v3 Namespaces.
[^mps-architecture]: NVIDIA MPS documentation, Architecture.
[^mps-when-to-use]: NVIDIA MPS documentation, When to Use MPS.
[^mps-common-tasks]: NVIDIA MPS documentation, Common Tasks.
[^mps-env-vars]: NVIDIA MPS documentation, Appendix: Environment Variables.

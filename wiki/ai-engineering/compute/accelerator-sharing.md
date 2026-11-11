---
type: Concept
title: Sharing Accelerators Across Vendors
aliases:
- GPU Sharing
- GPU Partitioning
description: How NVIDIA, AMD, Apple and Google TPUs let several workloads use one chip, from hardware partitions to
  time-slicing to exclusive allocation.
tags:
- ai-engineering
- compute
- gpu
parent: /ai-engineering/compute.md
related:
- /ai-engineering/compute/mps.md
- /ai-engineering/compute/mig.md
- /ai-engineering/compute/run-ai.md
- /ai-engineering/compute/npu.md
- /ai-engineering/compute/unified-memory.md
sources:
- id: amd-kernel-params
  resource: https://docs.kernel.org/gpu/amdgpu/module-parameters.html
  title: amdgpu module parameters
  author: Linux kernel documentation
- id: amd-oversubscription
  resource: https://instinct.docs.amd.com/projects/amdgpu-docs/en/latest/conceptual/oversubscription.html
  title: Oversubscription of hardware resources in AMD Instinct GPUs
  author: AMD
- id: amd-env-vars
  resource: https://rocm.docs.amd.com/en/latest/reference/env-variables.html
  title: ROCm environment variables
  author: AMD
- id: amd-partitioning
  resource: https://instinct.docs.amd.com/projects/amdgpu-docs/en/latest/gpu-partitioning/mi300x/overview.html
  title: AMD Instinct MI300X GPU Partitioning Overview
  author: AMD
- id: amd-modes-blog
  resource: https://rocm.blogs.amd.com/software-tools-optimization/compute-memory-modes/README.html
  title: Deep dive into the MI300 compute and memory partition modes
  author: AMD
- id: amd-virt-partitioning
  resource: https://instinct.docs.amd.com/projects/virt-drv/en/latest/userguides/GPU_partitioning.html
  title: GPU Partitioning, AMD Instinct Virtualization Driver
  author: AMD
- id: apple-cb-errors
  resource: https://developer.apple.com/documentation/metal/mtlcommandbuffererror-swift.struct/code
  title: MTLCommandBufferError.Code
  author: Apple
- id: apple-working-set
  resource: https://developer.apple.com/documentation/metal/mtldevice/recommendedmaxworkingsetsize
  title: recommendedMaxWorkingSetSize
  author: Apple
- id: asahi-m1-gpu
  resource: https://asahilinux.org/2022/11/tales-of-the-m1-gpu/
  title: Tales of the M1 GPU
  author: Asahi Linux
- id: gke-tpus
  resource: https://docs.cloud.google.com/kubernetes-engine/docs/concepts/tpus
  title: About TPUs in GKE
  author: Google Cloud
- id: compute-tpu-machines
  resource: https://docs.cloud.google.com/compute/docs/tpus/tpu-machines
  title: TPU machines in accelerator-optimized machine family
  author: Google Cloud
- id: dataflow-tpus
  resource: https://docs.cloud.google.com/dataflow/docs/tpu/use-tpus
  title: Run a pipeline with TPUs
  author: Google Cloud
- id: jax-libtpu-issue
  resource: https://github.com/jax-ml/jax/issues/10192
  title: libtpu.so already in use but actually not used
  author: JAX project issue
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-05T15:42:16+04:00'
---

MPS and MIG are NVIDIA products, but the problem is general. Sharing one chip comes in four forms, and vendors
differ mostly in which ones they offer and how the partition lines fall.

| Approach | NVIDIA | AMD | Apple | Google TPU |
| --- | --- | --- | --- | --- |
| Hardware partitions | [MIG](/ai-engineering/compute/mig.md) | SPX, DPX, CPX with NPS memory modes | None public | Slices, across chips rather than within one |
| Processes running concurrently | [MPS](/ai-engineering/compute/mps.md) | Built into the hardware scheduler, up to limits | Not documented | No: one process per device |
| Time-slicing | Default between contexts | Oversubscription; V710 between VFs | OS-managed, details private | Not found |
| Per-client caps | Thread percentage, memory limits | CU masks | None found | Not applicable |

## AMD

AMD is the closest match, and its native behavior differs from NVIDIA's.

**Multi-process concurrency.** The driver's default is hardware scheduling, with a setting for the "maximum number
of processes that HWS can schedule concurrently".[^amd-kernel-params] Current Instinct GPUs have 11 virtual memory
context slots and 24 hardware queues. Go past either and the GPU is oversubscribed: the scheduler falls back to
round-robin, and idle queues can block it for milliseconds.[^amd-oversubscription] So AMD seems not to need a
separate MPS-style service below those limits. That is our reading; AMD's docs don't compare the two.

**Caps.** `ROC_GLOBAL_CU_MASK` and `HSA_CU_MASK` restrict which compute units a process's queues use, close to MPS
thread limits.[^amd-env-vars]

**Hardware partitions.** The MI300X divides along its chiplets. SPX is one device with 304 CUs and 192GB, DPX is two,
and CPX is eight with 38 CUs and 24GB each. This needs no VM or hypervisor.[^amd-partitioning] Memory has separate
NPS modes. SR-IOV adds isolation between virtual functions for VMs.[^amd-modes-blog]

**Not everything is spatial.** The monolithic Radeon PRO V710 time-slices the whole GPU between virtual
functions.[^amd-virt-partitioning]

We found no AMD statement on error isolation between compute partitions, so don't assume it matches MIG's.

## Apple

We found no public equivalent of MIG or MPS. Metal has no documented way to partition a GPU or cap a process's share
of it. Apple's stack is designed for one person's machine, not tenants.

- The OS still polices processes. Metal reports per-command-buffer failures such as `timeout` and `pageFault`, and
  `accessRevoked` when a process causes too many timeouts or hangs.[^apple-cb-errors]
- Memory guidance is advisory: `recommendedMaxWorkingSetSize` is an approximation of what fits without hurting
  performance.[^apple-working-set]
- Scheduling is private. Reverse engineering by Asahi Linux found a firmware coprocessor manages the GPU, and the
  macOS driver talks to it rather than to the hardware.[^asahi-m1-gpu] Whether two processes' kernels run at the same
  moment is not publicly documented.
- The CPU and GPU share one memory pool, but the GPU is still a separate device with its own firmware; see
  [unified memory](/ai-engineering/compute/unified-memory.md).

## Google TPU

TPUs take the opposite approach: exclusive allocation rather than sharing.

- Only one container in a Pod can use TPUs, and a container requesting TPUs must take all the chips on its
  node.[^gke-tpus]
- A slice is a partition of a TPU Pod allotted to run a single workload.[^compute-tpu-machines]
- Only one process may compute on a TPU device.[^dataflow-tpus] In practice, a second process gets "libtpu.so already
  in use" and JAX falls back to CPU.[^jax-libtpu-issue]

We found no fractional chip option. TPUs scale out through slices instead, so the slice boundary does the job of a
partition, but across many chips. Google's pages could not be fetched directly during this research, so these
points come from search excerpts of them. Failure behavior across a slice remains unverified.

## Why the models differ

This reading is ours. Sharing pays off when a chip is larger than one job needs. NVIDIA and AMD sell big chips to
many tenants, so they built partitions. Apple serves one user. TPUs are rented whole for jobs that fill them, so
sharing a chip matters less.

[^amd-kernel-params]: Linux kernel docs, amdgpu module parameters.
[^amd-oversubscription]: AMD GPU Driver docs, oversubscription.
[^amd-env-vars]: ROCm docs, environment variables.
[^amd-partitioning]: AMD GPU Driver docs, MI300X partitioning overview.
[^amd-modes-blog]: ROCm blog, compute and memory partition modes.
[^amd-virt-partitioning]: AMD Instinct Virtualization Driver docs, GPU Partitioning.
[^apple-cb-errors]: Apple Metal documentation, MTLCommandBufferError.Code.
[^apple-working-set]: Apple Metal documentation, recommendedMaxWorkingSetSize.
[^asahi-m1-gpu]: Asahi Linux, reverse engineering write-up, 2022.
[^gke-tpus]: Google Cloud, About TPUs in GKE.
[^compute-tpu-machines]: Google Cloud, TPU machines.
[^dataflow-tpus]: Google Cloud, Run a pipeline with TPUs.
[^jax-libtpu-issue]: JAX GitHub issue 10192.

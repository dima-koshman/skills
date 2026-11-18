---
type: Concept
title: NVIDIA Multi-Instance GPU (MIG)
aliases:
- MIG
description: Hardware partitioning of one GPU into up to seven isolated instances, each with its own compute,
  cache and memory path, on Ampere and newer data center GPUs.
tags:
- ai-engineering
- compute
- gpu
parent: /ai-engineering/compute/gpu-sharing.md
related:
- /ai-engineering/compute/gpu-sharing/mps.md
- /ai-engineering/compute/gpu-sharing/run-ai.md
- /ai-engineering/compute/software-stack/cuda.md
- /ai-engineering/compute/gpu-sharing/accelerator-sharing.md
sources:
- id: mig-intro
  resource: https://docs.nvidia.com/datacenter/tesla/mig-user-guide/latest/introduction.html
  title: MIG User Guide, Introduction
  author: NVIDIA
- id: mig-concepts
  resource: https://docs.nvidia.com/datacenter/tesla/mig-user-guide/latest/concepts.html
  title: MIG User Guide, Concepts
  author: NVIDIA
- id: mig-gpus
  resource: https://docs.nvidia.com/datacenter/tesla/mig-user-guide/latest/supported-gpus.html
  title: MIG User Guide, Supported GPUs
  author: NVIDIA
- id: mig-considerations
  resource: https://docs.nvidia.com/datacenter/tesla/mig-user-guide/latest/deployment-considerations.html
  title: MIG User Guide, Deployment Considerations
  author: NVIDIA
- id: gpu-mem-containment
  resource: https://docs.nvidia.com/deploy/a100-gpu-mem-error-mgmt/error-containment.html
  title: NVIDIA GPU Memory Error Management, Error Containment
  author: NVIDIA
- id: gpu-mem-response
  resource: https://docs.nvidia.com/deploy/a100-gpu-mem-error-mgmt/response-to-uncorrectable-contained-ecc-errors.html
  title: NVIDIA GPU Memory Error Management, Response to Uncorrectable Contained ECC Errors
  author: NVIDIA
- id: gpu-mem-recovery
  resource: https://docs.nvidia.com/deploy/a100-gpu-mem-error-mgmt/error-recovery-and-response-flags.html
  title: NVIDIA GPU Memory Error Management, Error Recovery and Response Flags
  author: NVIDIA
- id: mps-common-tasks
  resource: https://docs.nvidia.com/deploy/mps/latest/common-tasks.html
  title: Multi-Process Service, Common Tasks
  author: NVIDIA
- id: k8s-device-plugin
  resource: https://github.com/NVIDIA/k8s-device-plugin
  title: NVIDIA device plugin for Kubernetes
  author: NVIDIA
- id: mps-v3-memory
  resource: https://docs.nvidia.com/deploy/mps/latest/mpsv3-memory-partitioning.html
  title: MPS v3 Memory Partitioning
  author: NVIDIA
- id: runai-fractions
  resource: https://run-ai-docs.nvidia.com/self-hosted/platform-management/runai-scheduler/resource-optimization/fractions
  title: NVIDIA Run:ai GPU Fractions
  author: NVIDIA
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-05T15:42:16+04:00'
---

MIG splits one physical GPU into up to seven GPU instances that software treats like separate
GPUs.[^mig-intro] Yes, this is the hardware-side option: [MPS](/ai-engineering/compute/gpu-sharing/mps.md) shares one
GPU's scheduling hardware between processes, while MIG divides the hardware itself.

## Compared with streams and MPS

NVIDIA's own comparison:[^mig-concepts]

| | CUDA streams | MPS | MIG |
| --- | --- | --- | --- |
| Partition type | Single process | Logical | Physical |
| Max partitions | Unlimited | 48 | 7 |
| SM performance isolation | No | By percentage, not partitioning | Yes |
| Memory protection | No | Yes | Yes |
| Memory bandwidth QoS | No | No | Yes |
| Error isolation | No | No | Yes |
| Reconfigure | Dynamic | At process launch | When idle |

The MPS docs give a different client limit, 60 contexts per device. Static SM partitioning has since narrowed
the MPS gap, but NVIDIA calls its error isolation partial.[^mps-common-tasks]

## What gets partitioned

Each instance has its own path through the memory system: crossbar ports, L2 cache banks, memory controllers
and DRAM address buses. A neighbor thrashing its cache or saturating DRAM should not change your throughput or
latency.[^mig-intro] Each memory slice is 1/8 of GPU memory and each SM slice is 1/7 of the SMs.[^mig-concepts]

A **GPU instance** can be split further into **compute instances**. Those get dedicated SMs but share the
instance's memory and engines, so the strong isolation is at the GPU instance level.[^mig-concepts]

## How complete the error isolation is

Strong for normal faults, but not absolute.

NVIDIA says MIG provides fault isolation between clients and that one client cannot impact another's work or
scheduling.[^mig-intro] The limits come from NVIDIA's memory error docs, which cover the GPU generally rather
than MIG specifically, so applying them to MIG is our reading:

- **Contained errors stay local.** From Ampere on, an uncorrectable memory error is usually limited to the
  application that hit it, and others keep running.[^gpu-mem-containment] That application is terminated and
  the bad page is taken out of use.[^gpu-mem-response]
- **Uncontained errors can spread.** In rare cases they "might impact all the workloads being processed in the
  GPU".[^gpu-mem-containment]
- **A reset is GPU-wide.** When a fault needs a GPU reset, NVIDIA's procedure is to terminate all GPU processes
  and then run `nvidia-smi -r`.[^gpu-mem-recovery] Some faults call for a node reboot instead.[^gpu-mem-recovery]

All instances also share one physical device, so anything that takes the device down takes them all down. NVIDIA's
Xid guide pages we checked say nothing specific about MIG, so per-instance error reporting is still unverified.

## Costs and limits

- **Fixed sizes:** you pick from set profiles, such as `1g.5gb` to `7g.40gb` on an A100 40GB, and positions
  matter, so creating and destroying instances can fragment the GPU.[^mig-concepts]
- **Hardware:** Ampere and newer with compute capability 8.0 or above, such as A100, H100 and B200. Some
  products allow only 2 or 4 instances.[^mig-gpus]
- **Application limits:** bare-metal MIG is Linux only, graphics APIs work only on specific `+gfx` profiles, CUDA
  IPC across GPU instances is unsupported, and shared-resource profiling is unsupported.[^mig-considerations]
- **Mixing:** Run:ai GPU fractions and MIG cannot be used on the same node.[^runai-fractions]

## MPS on top of MIG

This is a sensible layered design: MIG draws the hard line between tenants, and MPS lets one tenant's processes run
together inside a slice. Our reasoning on the result: faults stay within the slice, but clients in that slice share
them, and spare capacity in one slice cannot help another.

NVIDIA's MIG guide supports it, with the client limit reduced in proportion to the compute
instance.[^mig-considerations] Support elsewhere is narrower:

- The Kubernetes device plugin does not support MPS on MIG devices, and treats its MPS support as
  experimental.[^k8s-device-plugin]
- MPS v3 memory partitioning explicitly does not work on MIG.[^mps-v3-memory]

So on Kubernetes with the standard plugin, you cannot get this combination out of the box.

## Debugging

Unlike MPS, `cuda-gdb` and `compute-sanitizer` are supported under MIG.[^mig-considerations]

[^mig-intro]: NVIDIA MIG User Guide, Introduction.
[^mig-concepts]: NVIDIA MIG User Guide, Concepts.
[^mig-gpus]: NVIDIA MIG User Guide, Supported GPUs.
[^mig-considerations]: NVIDIA MIG User Guide, Deployment Considerations.
[^gpu-mem-containment]: NVIDIA GPU Memory Error Management, Error Containment.
[^gpu-mem-response]: NVIDIA GPU Memory Error Management, Response to Uncorrectable Contained ECC Errors.
[^gpu-mem-recovery]: NVIDIA GPU Memory Error Management, Error Recovery and Response Flags.
[^mps-common-tasks]: NVIDIA MPS documentation, Common Tasks.
[^k8s-device-plugin]: NVIDIA Kubernetes device plugin README, Shared Access to GPUs.
[^mps-v3-memory]: NVIDIA MPS documentation, MPS v3 Memory Partitioning.
[^runai-fractions]: NVIDIA Run:ai documentation, GPU Fractions.

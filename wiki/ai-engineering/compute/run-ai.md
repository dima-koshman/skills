---
type: Tool
title: NVIDIA Run:ai
aliases:
- Run:ai
- RunAI
description: A Kubernetes platform for GPU scheduling, quotas and fractional GPU sharing across teams, open source
  since October 2026, with KAI Scheduler as its scheduling engine.
resource: https://run-ai-docs.nvidia.com/
tags:
- ai-engineering
- compute
- gpu
- kubernetes
parent: /ai-engineering/compute.md
related:
- /ai-engineering/compute/mps.md
- /ai-engineering/compute/mig.md
- /ai-engineering/compute/serving/triton-inference-server.md
- /software-engineering/infrastructure.md
sources:
- id: runai-acquisition
  resource: https://blogs.nvidia.com/blog/runai/
  title: NVIDIA to Acquire GPU Orchestration Software Provider Run:ai
  author: Alexis Bjorlin (NVIDIA)
  last_modified: '2024-04-24T00:00:00Z'
- id: kai-open-source
  resource: https://developer.nvidia.com/blog/nvidia-open-sources-runai-scheduler-to-foster-community-collaboration/
  title: NVIDIA Open Sources Run:ai Scheduler to Foster Community Collaboration
  author: Ronen Dar, Ekin Karabulut (NVIDIA)
  last_modified: '2025-04-01T00:00:00Z'
- id: runai-open-source
  resource: https://developer.nvidia.com/blog/nvidia-runai-is-now-open-source-as-part-of-nvidia-dsx-ai-factory-platform/
  title: NVIDIA Run:ai Is Now Open Source as Part of NVIDIA DSX AI Factory Platform
  author: Ekin Karabulut, Sam Heywood (NVIDIA)
  last_modified: '2026-10-13T00:00:00Z'
- id: runai-get-started
  resource: https://www.nvidia.com/en-us/data-center/nvidia-run-ai/get-started/
  title: Get Started With NVIDIA Run:ai for AI Workloads
  author: NVIDIA
- id: runai-fractions
  resource: https://run-ai-docs.nvidia.com/self-hosted/platform-management/runai-scheduler/resource-optimization/fractions
  title: NVIDIA Run:ai GPU Fractions (self-hosted v2.26)
  author: NVIDIA
- id: runai-time-slicing
  resource: https://run-ai-docs.nvidia.com/self-hosted/platform-management/runai-scheduler/resource-optimization/time-slicing
  title: NVIDIA Run:ai GPU Time-Slicing (self-hosted v2.26)
  author: NVIDIA
- id: kai-gpu-sharing
  resource: https://github.com/kai-scheduler/KAI-Scheduler/blob/main/docs/gpu-sharing/README.md
  title: KAI Scheduler, GPU Sharing
  author: KAI Scheduler project
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-05T14:58:40+04:00'
---

Run:ai sits above the serving stack: it decides which workload gets which GPU in a Kubernetes cluster, and how
much of it. Plain Kubernetes usually asks for a whole number of GPUs,[^runai-fractions] which wastes capacity on
notebooks and small inference jobs. Run:ai adds fractional GPUs, quotas per team and fair-share scheduling.

## History and pieces

- **2024-04:** NVIDIA announced an agreement to acquire Run:ai, an Israeli startup.[^runai-acquisition]
- **2025-04:** NVIDIA released the scheduler as KAI Scheduler under Apache 2.0.[^kai-open-source] It has since
  been contributed to the CNCF as a Sandbox project.[^runai-open-source]
- **2026-10:** NVIDIA released the full platform as open source.[^runai-open-source]

That release has four components that can be adopted separately: KAI Scheduler, GPU Fractioning Operator, KAI
Resource Management for quotas and hierarchy, and Workload Map.[^runai-open-source] The self-hosted Community
Product on NGC needs no paid subscription, but downloading it means accepting NVIDIA's license
terms.[^runai-open-source]

## How GPU fractions work

A fraction is a scheduling and memory construct, not a hardware partition.

- **Memory:** the scheduler picks a node, and logic on that node enforces the requested memory so no workload can
  use more than it asked for.[^runai-fractions]
- **Compute:** by default fractions use NVIDIA's time-slicing, which splits compute evenly between workloads
  whatever fraction they requested. Two workloads get 50% each even if one asked for 25%.[^runai-time-slicing]
- **Run:ai time-slicing:** this gives a workload exclusive use of the full GPU for a lease inside a repeating cycle,
  so a 25% request gets 25% of compute time. **Strict** mode caps it there; **Fair** mode lets it use time
  others leave idle.[^runai-time-slicing]

So a fraction shares the GPU the same way native
[multi-process sharing](/ai-engineering/compute/mps.md) does, by taking turns on the whole device, with memory and
time accounting added. It does not make kernels from different workloads run at once. The fraction docs we read
claim memory enforcement but no fault isolation, so assume workloads share a GPU's failures.

| | Run:ai fraction | [MIG](/ai-engineering/compute/mig.md) slice |
| --- | --- | --- |
| Boundary | Software | Hardware |
| Sizes | Flexible memory chunks[^runai-fractions] | Fixed profiles |
| Admin work | Low[^runai-fractions] | Configure each slice[^runai-fractions] |

The two cannot be used on the same node.[^runai-fractions]

## KAI Scheduler alone

Using KAI without the platform changes the guarantees. Its default sharing mode, `NonMemoryEnforced`, does not
enforce memory limits, so containers may use more than they requested. `HamiCore` and `NvFractions` modes add
enforcement.[^kai-gpu-sharing]

The Run:ai pages cited are the self-hosted v2.26 docs, while the open-source release is Run:ai 3.0,[^runai-get-started] so
check behavior against the current version.

[^runai-acquisition]: NVIDIA blog, 2024-04-24.
[^kai-open-source]: NVIDIA developer blog, 2025-04-01.
[^runai-open-source]: NVIDIA developer blog, 2026-10-13.
[^runai-get-started]: NVIDIA Run:ai get-started page, FAQ.
[^runai-fractions]: NVIDIA Run:ai documentation, GPU Fractions.
[^runai-time-slicing]: NVIDIA Run:ai documentation, GPU Time-Slicing.
[^kai-gpu-sharing]: KAI Scheduler repository, GPU Sharing.

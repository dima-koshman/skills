---
type: Concept
title: Unified CPU-GPU Memory
aliases:
- Unified Memory
- Unified Memory Architecture
- UMA
- Shared CPU-GPU Memory
description: Why a CPU and GPU can share one memory pool, why the GPU is still a separate device to the OS, and what
  the design trades away, from Apple silicon to MI300A and Grace Hopper.
tags:
- ai-engineering
- compute
- gpu
parent: /ai-engineering/compute.md
related:
- /ai-engineering/compute/gpu-scheduling.md
- /ai-engineering/compute/accelerator-sharing.md
- /ai-engineering/compute/performance-regimes.md
- /ai-engineering/compute/mps.md
sources:
- id: apple-storage-modes
  resource: https://developer.apple.com/documentation/metal/choosing-a-resource-storage-mode-for-apple-gpus
  title: Choosing a resource storage mode for Apple GPUs
  author: Apple
- id: apple-has-unified-memory
  resource: https://developer.apple.com/documentation/metal/mtldevice/hasunifiedmemory
  title: hasUnifiedMemory
  author: Apple
- id: apple-storage-shared
  resource: https://developer.apple.com/documentation/metal/mtlstoragemode/shared
  title: MTLStorageMode.shared
  author: Apple
- id: apple-storage-private
  resource: https://developer.apple.com/documentation/metal/mtlstoragemode/private
  title: MTLStorageMode.private
  author: Apple
- id: asahi-m1-gpu
  resource: https://asahilinux.org/2022/11/tales-of-the-m1-gpu/
  title: Tales of the M1 GPU
  author: Asahi Linux
- id: m3-ultra-news
  resource: https://www.apple.com/newsroom/2025/03/apple-reveals-m3-ultra-taking-apple-silicon-to-a-new-extreme/
  title: Apple reveals M3 Ultra, taking Apple silicon to a new extreme
  author: Apple Newsroom
  last_modified: '2025-03-05T00:00:00Z'
- id: mac-studio-specs
  resource: https://support.apple.com/en-us/122211
  title: Mac Studio (2025) technical specifications
  author: Apple
- id: dgx-spark-hw
  resource: https://docs.nvidia.com/dgx/dgx-spark/hardware.html
  title: DGX Spark User Guide, Hardware Overview
  author: NVIDIA
- id: grace-hopper
  resource: https://developer.nvidia.com/blog/nvidia-grace-hopper-superchip-architecture-in-depth/
  title: NVIDIA Grace Hopper Superchip Architecture In-Depth
  author: NVIDIA
- id: grace-tuning
  resource: https://docs.nvidia.com/dccpu/grace-perf-tuning-guide/index.html
  title: NVIDIA Grace Performance Tuning Guide
  author: NVIDIA
- id: gh200-measured
  resource: https://arxiv.org/abs/2407.07850
  title: Harnessing Integrated CPU-GPU System Memory for HPC, a first look into Grace Hopper
  author: Gabin Schieffer et al. (arXiv 2407.07850)
- id: mi300a
  resource: https://instinct.docs.amd.com/projects/amdgpu-docs/en/latest/gpu-partitioning/mi300a/overview.html
  title: AMD Instinct MI300A APU Overview
  author: AMD
- id: mi300a-datasheet
  resource: https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300a-data-sheet.pdf
  title: AMD Instinct MI300A data sheet
  author: AMD
- id: hopper-in-depth
  resource: https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/
  title: NVIDIA Hopper Architecture In-Depth
  author: NVIDIA
- id: ptask
  resource: https://www.cs.utexas.edu/users/witchel/pubs/sosp11rossbach-ptask.pdf
  title: 'PTask: Operating System Abstractions To Manage GPUs as Compute Devices'
  author: Christopher Rossbach, Jon Currey, Mark Silberstein, Baishakhi Ray, Emmett Witchel (SOSP 2011)
  last_modified: '2011-10-23T00:00:00Z'
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-11T10:05:00+04:00'
---

On Apple silicon the CPU and GPU sit in one chip and read the same physical memory. "Apple GPUs have a unified
memory model in which the CPU and the GPU share system memory."[^apple-storage-modes] A discrete GPU, by contrast,
has its own memory on its own board, and data crosses PCIe to reach it.

## Shared memory does not make it one device

Sharing memory removes copies. It does not merge the processors.

- The GPU still runs its own command queues and scheduler. On M1, a firmware coprocessor manages the GPU, and the
  macOS driver talks to that firmware rather than to the GPU hardware.[^asahi-m1-gpu]
- The OS still sees a device with a driver. What it no longer manages is a separate memory.
- Programs still choose how each buffer is used. Apple's storage modes are **shared** (CPU and GPU, the default on
  Apple silicon), **private** (GPU only) and **memoryless** (on-chip tile memory only).[^apple-storage-modes]

So the "GPU as an I/O device" problem from [GPU scheduling](/ai-engineering/compute/gpu-scheduling.md) is mostly
about OS abstractions, not where memory lives. PTask argued that OSes cannot guarantee fairness while they treat
the GPU as a device behind a driver.[^ptask] Unified memory fixes the data path and leaves that part as it was.
(This reading is ours.)

## What "shared" still requires

- **Synchronization is your job.** With shared storage, "you're responsible for synchronizing access" between CPU
  and GPU.[^apple-storage-shared] One memory does not mean the two see each other's writes at the right moment.
- **GPU-only is still faster.** "Metal may apply additional optimizations to private resources."[^apple-storage-private]
- **The best memory is still on-chip.** Memoryless tile memory has "higher bandwidth, lower latency, and consumes
  less power than system memory".[^apple-storage-modes]

## It is not unique to Apple

Apple's own docs describe a GPU with unified memory as "typically an integrated GPU".[^apple-has-unified-memory]
Laptop and phone GPUs have long shared system memory this way. What is newer is doing it at large sizes and for AI.

| System | Memory | How it is shared | Bandwidth |
| --- | --- | --- | --- |
| Apple M3 Ultra | Up to 512GB LPDDR at launch[^m3-ultra-news]; the current spec page lists up to 256GB[^mac-studio-specs] | One pool | 819GB/s[^mac-studio-specs] |
| NVIDIA DGX Spark (GB10) | 128GB LPDDR5x | "Coherent unified system memory"[^dgx-spark-hw] | 273GB/s[^dgx-spark-hw] |
| AMD MI300A | 128GB HBM3, no DDR at all[^mi300a] | "Single shared address space"[^mi300a-datasheet] | 5.3TB/s[^mi300a-datasheet] |
| NVIDIA Grace Hopper | Up to 512GB LPDDR5X on the CPU plus 96GB HBM3 on the GPU | Two memories made coherent over a 900GB/s link[^grace-hopper] | 546GB/s and 3TB/s[^grace-hopper] |
| NVIDIA H100 SXM5, for scale | 80GB HBM3, GPU only | Separate, over PCIe or NVLink | Over 3TB/s[^hopper-in-depth] |

Grace Hopper is unified in a looser sense. CPU and GPU threads can access both memories without explicit
copies,[^grace-hopper] but the OS sees two NUMA nodes,[^grace-tuning] and locality still matters. One measurement
found the CPU reads the GPU's HBM at about 140GB/s, while the GPU reads it at about 3.6TB/s. That figure comes from a
search excerpt of the paper, not the full text.[^gh200-measured]

## Pros

- **No copies.** Data the CPU loaded is already where the GPU can read it.
- **A large GPU-visible pool.** Apple pitches the M3 Ultra for LLMs "with over 600 billion parameters" on one
  desktop, more memory than workstation graphics cards offer.[^m3-ultra-news] For memory-bound LLM decoding, fitting
  the model at all matters before bandwidth does.
- **Power.** Data does not cross a board-level bus, and one memory system serves both processors. (Our reasoning.)
- **Simpler code.** No staging buffers or explicit transfers in the common case.

## Cons

- **Bandwidth.** LPDDR pools give 273 to 819GB/s, a quarter or less of an H100's HBM. LLM decode speed is usually
  limited by memory bandwidth ([performance regimes](/ai-engineering/compute/performance-regimes.md)), so a Mac can
  fit a model an H100 cannot, yet generate tokens more slowly. (Our inference from the table above.)
- **Contention.** CPU and GPU draw on the same memory bandwidth, so heavy CPU work slows the GPU. (Our reasoning.)
- **Fixed capacity.** Memory sits on the package. You choose it at purchase and cannot add more. (Our reasoning from
  the configurable options on the spec page.)
- **Still needs synchronization**, as above.

## Can big GPUs be built this way?

They already are, in two styles, and each picks a different trade between capacity and bandwidth.

1. **One pool of fast memory: MI300A.** CPU cores and GPU compute units share HBM in one package. All system memory
   is the 128GB of HBM, which gives HBM bandwidth to both but caps capacity at 128GB.[^mi300a]
2. **Two memories made coherent: Grace Hopper.** The CPU keeps large, cheaper LPDDR and the GPU keeps fast HBM, and a
   coherent link lets each use the other's.[^grace-hopper] You get capacity and bandwidth, but not uniformly: data
   should still live near the processor that uses it.

The underlying constraint, our reading: HBM is fast but expensive and limited in size; LPDDR and DDR are large and
cheap but slow. Unified memory does not remove that trade. It lets the designer pick a point on it, and removes the
explicit copies either way. The benefit is largest for workloads that move data back and forth between CPU and GPU,
or that do not fit in GPU memory alone. A model that already fits in HBM and stays on the GPU gains little.

[^apple-storage-modes]: Apple Metal documentation, Choosing a resource storage mode for Apple GPUs.
[^apple-has-unified-memory]: Apple Metal documentation, `MTLDevice.hasUnifiedMemory`.
[^apple-storage-shared]: Apple Metal documentation, `MTLStorageMode.shared`.
[^apple-storage-private]: Apple Metal documentation, `MTLStorageMode.private`.
[^asahi-m1-gpu]: Asahi Linux, reverse engineering write-up, 2022.
[^m3-ultra-news]: Apple Newsroom, M3 Ultra announcement, March 2025.
[^mac-studio-specs]: Apple Support, Mac Studio (2025) technical specifications, checked 2026-11-11.
[^dgx-spark-hw]: NVIDIA DGX Spark User Guide, Hardware Overview.
[^grace-hopper]: NVIDIA developer blog, Grace Hopper Superchip Architecture In-Depth.
[^grace-tuning]: NVIDIA Grace Performance Tuning Guide.
[^gh200-measured]: Schieffer et al., arXiv 2407.07850, via search excerpt.
[^mi300a]: AMD GPU Driver documentation, MI300A APU Overview.
[^mi300a-datasheet]: AMD Instinct MI300A data sheet.
[^hopper-in-depth]: NVIDIA developer blog, Hopper Architecture In-Depth.
[^ptask]: Rossbach et al., SOSP 2011, sections 1 and 2.3.

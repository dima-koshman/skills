---
type: Tool
title: NVIDIA Triton Inference Server
aliases:
- Dynamo Triton
- NVIDIA Dynamo Triton
- Triton Server
description: NVIDIA's general-purpose model server, which hosts many models and frameworks behind one API and
  handles batching, concurrency and backends. Not the Triton GPU kernel language.
resource: https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/index.html
tags:
- ai-engineering
- compute
- inference
- serving
parent: /ai-engineering/compute/serving.md
related:
- /ai-engineering/compute/serving/vllm.md
- /ai-engineering/compute/mps.md
- /ai-engineering/compute/mig.md
- /ai-engineering/compute/run-ai.md
- /ai-engineering/compute/max.md
sources:
- id: triton-overview
  resource: https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/index.html
  title: NVIDIA Triton Inference Server, Overview
  author: NVIDIA
- id: triton-model-execution
  resource: https://github.com/triton-inference-server/server/blob/main/docs/user_guide/model_execution.md
  title: Concurrent Model Execution
  author: NVIDIA
- id: triton-python-backend
  resource: https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/python_backend/README.html
  title: Python Backend
  author: NVIDIA
- id: triton-vllm-backend
  resource: https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/vllm_backend/README.html
  title: vLLM Backend
  author: NVIDIA
- id: triton-dynamo-rename
  resource: https://developer.nvidia.com/blog/fast-and-scalable-ai-model-deployment-with-nvidia-triton-inference-server/
  title: Fast and Scalable AI Model Deployment with NVIDIA Triton Inference Server
  author: NVIDIA
- id: mig-concepts
  resource: https://docs.nvidia.com/datacenter/tesla/mig-user-guide/latest/concepts.html
  title: MIG User Guide, Concepts
  author: NVIDIA
- id: mps-architecture
  resource: https://docs.nvidia.com/deploy/mps/latest/architecture.html
  title: Multi-Process Service, Architecture
  author: NVIDIA
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-05T14:58:40+04:00'
---

Triton Inference Server is a general model server. It hosts models from several frameworks at once and adds
dynamic batching, model management and HTTP or gRPC APIs around them.[^triton-overview] As of March 18, 2025
NVIDIA calls it NVIDIA Dynamo Triton, part of the Dynamo Platform; the docs still use the old
name.[^triton-dynamo-rename]

Do not confuse it with the Triton language, a Python DSL for GPU kernels, mentioned in
[CUDA Ecosystem](/ai-engineering/compute/cuda.md) and [Kernel Fusion](/ai-engineering/compute/serving/kernel-fusion.md).
They are unrelated projects.

## Where it sits

Triton is one layer above an inference engine. Its job is the server around execution, and a backend does the
execution. With the [vLLM](/ai-engineering/compute/serving/vllm.md) backend, requests go straight to vLLM's
engine, which handles in-flight batching and paged attention itself.[^triton-vllm-backend] So Triton has two
schedulers worth separating:

- Triton schedules requests to model instances and can batch them. It is model-agnostic.
- An LLM engine under it schedules tokens and KV memory. Triton does not do that for vLLM.

## Do models on one GPU get time-sliced?

It depends on the backend, because time-slicing applies between CUDA contexts, and normally a process has one
([MPS](/ai-engineering/compute/mps.md)).

| Backend | Runs as | Without MPS |
| --- | --- | --- |
| PyTorch, ONNX Runtime, TensorFlow | Threads in the Triton process[^triton-python-backend] | Can overlap on the GPU |
| Python backend | A separate process per model instance[^triton-python-backend] | Time-sliced (our inference) |
| vLLM backend | Python-based[^triton-vllm-backend] | Time-sliced (our inference) |

NVIDIA's general description is that two models arrive, "the GPU's hardware scheduler begins working on both
computations in parallel".[^triton-model-execution] That fits the threaded backends. For process-based backends,
the MPS docs say each process gets "a serially scheduled time-slice on the whole GPU".[^mps-architecture] The
Triton docs we read don't address this, and they don't mention MPS, so the last two rows combine the two sources.
We also did not confirm that each framework shares one CUDA context per process.

A Triton **execution context** is Triton's own term for a model instance's worker. It is not a CUDA context.

The threaded path has its own cost. Streams inside one process share an address space, and "any errors affect
all the streams and the whole process",[^mig-concepts] so one fatal GPU error can take out every threaded model
in that server.

## Concurrency defaults

Each model gets one instance by default, so requests to the same model run one at a time while requests to
different models can overlap. `instance_group` raises the count.[^triton-model-execution]
For vLLM, watch memory: it takes up to 90% of GPU memory by default, so co-located models need a lower
`gpu_memory_utilization`.[^triton-vllm-backend]

[^triton-overview]: NVIDIA Triton Inference Server documentation, Overview.
[^triton-model-execution]: Triton server repository, Concurrent Model Execution.
[^triton-python-backend]: NVIDIA Triton Inference Server documentation, Python Backend.
[^triton-vllm-backend]: NVIDIA Triton Inference Server documentation, vLLM Backend.
[^triton-dynamo-rename]: NVIDIA developer blog, note at the top of the post.
[^mig-concepts]: NVIDIA MIG User Guide, Concepts.
[^mps-architecture]: NVIDIA MPS documentation, Architecture.

---
okf_version: "0.2"
---

* [AI Engineering](/ai-engineering.md) `[Knowledge Area]` _(draft)_ - Personal knowledge base for AI engineering concepts.
* [Software Engineering](/software-engineering.md) `[Knowledge Area]` - Personal knowledge base for general software development and distributed-systems concepts.

# ai-engineering

* [Agent Harness](/ai-engineering/harness.md) `[Knowledge Area]` _(draft)_ - The runtime scaffolding around the model loop: tool dispatch, state, sandboxing, and loop control, with Claude Code, Codex, Antigravity, OpenCode and Deep Agents as implementations.
* [Agent Security](/ai-engineering/security.md) `[Knowledge Area]` _(draft)_ - How enterprise agent platforms are attacked: the OWASP Agentic Top 10 risks in one table, with pointers to the platform controls that contain them.
* [Agent-Readable Knowledge](/ai-engineering/knowledge.md) `[Knowledge Area]` _(draft)_ - Formats and tools for knowledge bases that agents read: OKF, its visualizers and OpenWiki.
* [AI Compute](/ai-engineering/compute.md) `[Knowledge Area]` - How AI workloads run on hardware — inference and serving techniques, GPU and NPU programming models, performance limits, compilers, CUDA, Mojo and MAX.
* [AI Development](/ai-engineering/development.md) `[Knowledge Area]` - Artifact-driven software development and telemetry-led diagnosis with AI agents.
* [AI Platform](/ai-engineering/platform.md) `[Knowledge Area]` _(draft)_ - The enterprise control layer around agents: gateways for model and tool traffic, guardrails and personal-data masking.
* [Context](/ai-engineering/context.md) `[Knowledge Area]` - What goes into the model's context window and how to manage it: context engineering, memory, retrieval, prompt caching, tool result offloading and skills.
* [Models](/ai-engineering/models.md) `[Knowledge Area]` - Language-model architecture, typed decision models, provider pricing and caching, and how to read leaderboards.
* [Multi-Agent Systems](/ai-engineering/multi-agent.md) `[Knowledge Area]` _(draft)_ - How agents work with other agents: subagents under a parent, code-driven subagents, peers without a parent, and the A2A protocol.
* [Observability and Evaluation](/ai-engineering/observability.md) `[Knowledge Area]` _(draft)_ - Tracing, monitoring and evaluation platforms for LLM apps and agents: LangSmith, managed and with evals and an in-product agent, and Langfuse, open source and self-hostable.

## compute

* [AI Software Stack](/ai-engineering/compute/software-stack.md) `[Knowledge Area]` _(draft)_ - The software between models and chips: CUDA, LLVM and MLIR, Mojo and MAX.
* [Compute, Memory and Overhead Bound](/ai-engineering/compute/performance-regimes.md) `[Concept]` - A slow model is limited by one of three things — math throughput, memory bandwidth, or host-side overhead — and each needs a different fix.
* [GPU Sharing and Scheduling](/ai-engineering/compute/gpu-sharing.md) `[Knowledge Area]` _(draft)_ - How several workloads share one accelerator: GPU scheduling, MPS, MIG, Run:ai and other vendors' options.
* [LLM Inference and Serving](/ai-engineering/compute/serving.md) `[Knowledge Area]` - A map of autoregressive inference phases, KV memory, scheduling, attention kernels, precision and distributed serving trade-offs.
* [Neural Processing Unit (NPU)](/ai-engineering/compute/npu.md) `[Concept]` - A hardware accelerator built specifically for neural-network math, usually low-precision and power-efficient, programmed with explicit memory movement rather than the GPU's thread model; Google's TPU is one, and GPU Tensor Cores are the same idea as a unit inside a GPU.
* [SIMD and SIMT](/ai-engineering/compute/simd-simt.md) `[Concept]` - Two ways to run one instruction over many data elements — explicit vector instructions (SIMD) vs NVIDIA's per-thread model on top of vector hardware (SIMT) — and why the difference matters for portable kernels.
* [Unified CPU-GPU Memory](/ai-engineering/compute/unified-memory.md) `[Concept]` - Why a CPU and GPU can share one memory pool, why the GPU is still a separate device to the OS, and what the design trades away, from Apple silicon to MI300A and Grace Hopper.

### gpu-sharing

* [NVIDIA Multi-Instance GPU (MIG)](/ai-engineering/compute/gpu-sharing/mig.md) `[Concept]` - Hardware partitioning of one GPU into up to seven isolated instances, each with its own compute, cache and memory path, on Ampere and newer data center GPUs.
* [NVIDIA Multi-Process Service (MPS)](/ai-engineering/compute/gpu-sharing/mps.md) `[Concept]` - A CUDA runtime service that lets kernels from different processes run on a GPU at the same time, where native multi-process sharing only takes turns on the whole GPU.
* [NVIDIA Run:ai](/ai-engineering/compute/gpu-sharing/run-ai.md) `[Tool]` - A Kubernetes platform for GPU scheduling, quotas and fractional GPU sharing across teams, open source since October 2026, with KAI Scheduler as its scheduling engine.
* [Sharing Accelerators Across Vendors](/ai-engineering/compute/gpu-sharing/accelerator-sharing.md) `[Concept]` - How NVIDIA, AMD, Apple and Google TPUs let several workloads use one chip, from hardware partitions to time-slicing to exclusive allocation.
* [Why GPU Scheduling Differs from CPU Scheduling](/ai-engineering/compute/gpu-sharing/gpu-scheduling.md) `[Concept]` - GPUs switch between threads constantly but between programs rarely, because they keep tens of MB of thread state on-chip; data transfer is not the reason.

### serving

* [Batching and Scheduling](/ai-engineering/compute/serving/batching-and-scheduling.md) `[Concept]` _(draft)_ - How a server decides what runs next: batch membership between iterations, chunked prompts, separate prefill and decode workers, and choosing a worker for each request.
* [Faster Kernels and Decoding](/ai-engineering/compute/serving/kernels-and-decoding.md) `[Concept]` _(draft)_ - Ways to make each generated token cheaper: attention and fused kernels that move less memory, CUDA graphs that cut launch overhead, speculative decoding and quantization.
* [Inference Parallelism](/ai-engineering/compute/serving/parallelism.md) `[Concept]` _(draft)_ - Five ways to spread one model's serving work across GPUs, each splitting something different: tensors, layers, requests, experts or the sequence.
* [LLM Serving Metrics](/ai-engineering/compute/serving/serving-metrics.md) `[Concept]` - Latency, throughput and goodput measure different serving goals and must be compared under a specified workload and load.
* [NVIDIA Triton Inference Server](/ai-engineering/compute/serving/triton-inference-server.md) `[Tool]` - NVIDIA's general-purpose model server, which hosts many models and frameworks behind one API and handles batching, concurrency and backends. Not the Triton GPU kernel language.
* [Prefill, Decode and the KV Cache](/ai-engineering/compute/serving/prefill-decode-and-kv-cache.md) `[Concept]` _(draft)_ - What happens during one request and where its attention state lives: the two inference phases, the KV cache they build, and how that cache is paged, reused across requests and offloaded.
* [vLLM](/ai-engineering/compute/serving/vllm.md) `[Tool]` - An open-source LLM inference and serving library built around KV cache management, which runs on its own or as a backend under a general model server such as Triton.

### software-stack

* [CUDA Ecosystem](/ai-engineering/compute/software-stack/cuda.md) `[Concept]` - Why NVIDIA's CUDA became the default AI software stack, why chip companies struggle to match it, and the main attempts to break the lock-in — compilers, Python DSLs, Mojo, and NVIDIA's own CUDA Rust.
* [LLVM and MLIR](/ai-engineering/compute/software-stack/compilers.md) `[Concept]` - The compiler infrastructure under Mojo — LLVM's shared intermediate representation that decouples languages from chips, and MLIR's many-level IRs (dialects) that keep AI operations meaningful until late in compilation.
* [MAX](/ai-engineering/compute/software-stack/max.md) `[Tool]` - Modular's AI serving and modeling framework — OpenAI-compatible model serving, a PyTorch-like Python modeling API, and Mojo kernels for CPUs, GPUs and ASICs without depending on CUDA or ROCm.
* [Mojo](/ai-engineering/compute/software-stack/mojo.md) `[Tool]` - Modular's Python-like systems language for CPUs, GPUs and other accelerators, built on MLIR; 1.0 and open source (Apache 2.0) since August 2026, owned by Qualcomm.

## context

* [Agent Skills](/ai-engineering/context/skills.md) `[Concept]` - Packaged instruction files an agent loads on demand — most useful as behavior control, and a context tax when installed indiscriminately.
* [Context Engineering](/ai-engineering/context/context-engineering.md) `[Concept]` _(draft)_ - Deliberately assembling what goes into the model's context window — instructions, tools, retrieved data, memory, and history.
* [Prompt Caching](/ai-engineering/context/prompt-caching.md) `[Concept]` - Reusing cached prefix tokens across LLM requests to minimize latency and token costs, and how to design agent harnesses around cache preservation.
* [Tool Result Offloading](/ai-engineering/context/tool-result-offloading.md) `[Practice]` - Store a large tool result outside the context window and keep only a path and preview, so the model can fetch the rest when it needs it.

## development

* [Agent Verification and Self-Improvement](/ai-engineering/development/agent-self-improvement.md) `[Concept]` - Agents can only be trusted, delegated to, or left to improve themselves as far as something independent can check their work, so verification sets the limit on supervision and on self-improvement.
* [AI Productivity Evidence](/ai-engineering/development/ai-productivity-evidence.md) `[Reference]` - What controlled trials and surveys show about AI's effect on software development speed, and what they don't measure.
* [AI-Native SDLC](/ai-engineering/development/ai-native-sdlc.md) `[Practice]` - A software lifecycle rebuilt as a loop of committed artifacts, with agents doing the work between gates and humans owning every judgment call.
* [Observability-Driven AI-Assisted Development](/ai-engineering/development/observability-driven-development.md) `[Practice]` - A development loop where AI agents use real runtime telemetry as evidence for diagnosis, remediation, and verification.

## harness

* [Advisor Tool](/ai-engineering/harness/advisor.md) `[Concept]` _(draft)_ - A cheaper executor model consults a stronger advisor model mid-task through a server-side tool; the advisor reads the whole transcript, not a question, and returns only advice text.
* [Agent Sandboxes](/ai-engineering/harness/sandboxes.md) `[Practice]` - Run the harness outside the sandbox and call the sandbox as a tool, keeping session state in a durable store, so harness, sandbox and session can each fail or be replaced on their own ("cattle, not pets").
* [Agents as Tools](/ai-engineering/harness/agents-as-tools.md) `[Concept]` _(draft)_ - Wrapping a scoped agent behind a tool call, so the parent gets one distilled answer back while the noisy reading, searching and retries stay in the agent's own context.
* [LLM Browser Use](/ai-engineering/harness/llm-browser-use.md) `[Concept]` - How LLMs operate real web browsers — the browser driver, the page representation the model reads, the control style and the hosting, with Playwright, Stagehand and Browserbase as examples.
* [Model Context Protocol (MCP)](/ai-engineering/harness/mcp.md) `[Protocol]` - Open protocol standardizing how LLM apps expose and consume tools, resources, and prompts.
* [Model Routing](/ai-engineering/harness/model-routing.md) `[Practice]` - Choosing a cheaper or stronger model per task belongs in the harness, which knows the task, and should happen once per thread, because switching models mid-conversation throws away the prompt cache.
* [Programmatic Tool Calling](/ai-engineering/harness/programmatic-tool-calling.md) `[Concept]` - Code mode and programmatic tool calling move tool or subagent orchestration into generated code, keeping intermediate results outside the main model context.
* [Tool Search](/ai-engineering/harness/tool-search.md) `[Concept]` _(draft)_ - The harness or API keeps most tool definitions out of the context window and lets the model search a catalog and load only the tools it needs, so hundreds of MCP tools cost little context.
* [Tools](/ai-engineering/harness/tools.md) `[Concept]` _(draft)_ - The primitive that turns an LLM into an agent: functions the model can call to act on and read from its environment, by where they run (backend, frontend, provider-side).

## knowledge

* [OKF Visualizers](/ai-engineering/knowledge/okf-visualizers.md) `[Concept]` - Comparison of the upstream static HTML viewer with our custom graph-and-reader renderer, including adoption instructions and compatibility limits.
* [Open Knowledge Format (OKF)](/ai-engineering/knowledge/okf.md) `[Knowledge Format]` - Google's vendor-neutral markdown-plus-frontmatter standard for agent-readable knowledge.
* [OpenWiki](/ai-engineering/knowledge/openwiki.md) `[Tool]` - LangChain's early-stage CLI for generating and maintaining agent-facing Markdown wikis from local knowledge sources.

## models

* [Contrastive Language Models (CLM)](/ai-engineering/models/clm.md) `[Decision Model]` - Open-source state-action scoring models with a TypeSafe-compatible API for typed decisions and candidate ranking.
* [Jev](/ai-engineering/models/jev.md) `[Decision Model]` - TypeSafe's System One model for fast typed decisions with probabilities, composed into software workflows.
* [LLM Architecture](/ai-engineering/models/llm-architecture.md) `[Concept]` _(draft)_ - Design choices inside modern open-weight LLMs — sparsity, attention efficiency, and the empirical tweaks — and the two main ways to make them multimodal.
* [LLM Leaderboards](/ai-engineering/models/leaderboards.md) `[Reference]` _(draft)_ - A curated bookmark set and benchmark map for choosing reliable, independent LLM evaluation sources across capabilities, plus how far to trust them (Artificial Analysis method limits, benchmaxxing evidence).
* [Model Providers](/ai-engineering/models/providers.md) `[Knowledge Area]` - Provider-specific API pricing and caching notes for Claude, Gemini and GPT.
* [ScaleDown](/ai-engineering/models/scaledown.md) `[Decision Model]` - Hosted constrained decoding models (CDMs) for summarizing, compressing, extracting and classifying agent context — small task-specific models that return only answers the task allows.

### providers

* [Claude](/ai-engineering/models/providers/claude.md) `[Model Provider]` - Anthropic Claude API token pricing and prompt-caching mechanics — cache multipliers, TTLs, and cost-optimization guidance.
* [Gemini](/ai-engineering/models/providers/gemini.md) `[Model Provider]` - Google Gemini API token pricing plus implicit and explicit context caching, with break-even guidance.
* [GPT](/ai-engineering/models/providers/gpt.md) `[Model Provider]` - OpenAI GPT API token pricing and prompt caching — the 272K long-context cliff, cache-write fees, and keep-alive economics.

## multi-agent

* [Agent2Agent](/ai-engineering/multi-agent/a2a.md) `[Protocol]` - A protocol designed by Google enabling communication and interoperability between opaque agentic applications.
* [Dynamic Subagents](/ai-engineering/multi-agent/dynamic-subagents.md) `[Concept]` - An agent writes code that dispatches subagents, branches on their results, and controls what returns to the coordinating model.
* [Peer Agents](/ai-engineering/multi-agent/peer-agents.md) `[Concept]` - Independently governed agents that own goals and coordinate as peers rather than through a permanent parent.
* [Subagents](/ai-engineering/multi-agent/subagents.md) `[Concept]` - Delegating focused subtasks to separate agent instances, and orchestrating multiple agents together.

## platform

* [AI Gateways](/ai-engineering/platform/ai-gateways.md) `[Concept]` _(draft)_ - The control points between AI clients and what they call: the LLM gateway in front of models and the MCP gateway in front of tools, centralizing auth, permissions, routing, policy and audit.
* [Guardrails and PII Masking](/ai-engineering/platform/guardrails-and-masking.md) `[Security Control]` _(draft)_ - Controls around model and tool calls: guardrails keep behavior inside a policy envelope, and PII masking keeps personal data from reaching models, logs or third parties in the clear.

# software-engineering

* [Architecture and Communication](/software-engineering/architecture.md) `[Knowledge Area]` _(draft)_ - Component boundaries, communication styles and dependency trade-offs, and the service contracts that implement them: Protocol Buffers and gRPC.
* [Distributed Systems](/software-engineering/distributed-systems.md) `[Knowledge Area]` _(draft)_ - A reading map of classic papers and books on storage, replication, consensus and large-scale data processing, with notes on each, plus case studies of production storage systems.
* [Frontend Engineering](/software-engineering/frontend.md) `[Knowledge Area]` _(draft)_ - Server-rendered interactivity and the trade-offs of the hypermedia approach, with htmx as the example.
* [Infrastructure](/software-engineering/infrastructure.md) `[Knowledge Area]` _(draft)_ - The layers around applications: service meshes, data, control and management planes, OS CPU scheduling, and network ports.
* [Learning Resources](/software-engineering/learning.md) `[Knowledge Area]` _(draft)_ - Practical labs and structured training for Linux, Kubernetes and software infrastructure: LabEx and Linux Foundation Training.
* [Planning and Delivery](/software-engineering/planning.md) `[Knowledge Area]` _(draft)_ - How software work is shaped, sized, committed to and shipped, such as appetites versus estimates.
* [Reliability Engineering](/software-engineering/reliability.md) `[Knowledge Area]` - Reliability targets, simplicity, and toil reduction as software engineering practices.
* [Source Control](/software-engineering/source-control.md) `[Knowledge Area]` _(draft)_ - Repository strategy at scale: monorepo vs polyrepo, with Google's, Meta's and Anthropic's scaling stories and the case against.

## architecture

* [Architectural Patterns](/software-engineering/architecture/architectural-patterns.md) `[Concept]` - Choose component boundaries, communication styles, and dependency directions according to the forces acting on a system.
* [gRPC](/software-engineering/architecture/grpc.md) `[Protocol]` - RPC framework using Protocol Buffers as its IDL to generate client and server stubs — a service-to-service alternative to REST.
* [Protocol Buffers](/software-engineering/architecture/protobuf.md) `[Knowledge Format]` - Language-neutral binary serialization for small structured records — schema-first `.proto` definitions compiled into native bindings.

## distributed-systems

* [Cosmos DB Partitioning](/software-engineering/distributed-systems/cosmos-db-partitioning.md) `[Concept]` - How Azure Cosmos DB maps many logical partitions (one per partition-key value) onto few physical partitions, why per-key limits are ceilings rather than guarantees, and why partitioning alone does not isolate tenants.
* [OpenAI Habitat](/software-engineering/distributed-systems/openai-habitat.md) `[Reference]` - How OpenAI scaled its online storage layer to 70M+ requests per second for 1B+ weekly users — a library turned Python service turned Rust service with a deliberately narrow API in front of Azure Cosmos DB, and a round trip from shared to dedicated and back to shared database containers.
* [TAO](/software-engineering/distributed-systems/tao.md) `[Reference]` - Facebook's read-optimized, geographically distributed graph store — a fixed objects-and-associations API served by a two-tier cache over sharded MySQL, replacing client-side memcache logic.

## infrastructure

* [Data, Control & Management Planes](/software-engineering/infrastructure/planes.md) `[Concept]` - The decomposition of a distributed system into traffic-carrying, policy-distributing, and operator-facing layers.
* [OS CPU Scheduling](/software-engineering/infrastructure/cpu-scheduling.md) `[Concept]` - How an OS shares CPU time, through preemption, fair shares and priorities, and how weights differ from limits, using Linux as the example.
* [Service Mesh](/software-engineering/infrastructure/service-mesh.md) `[Concept]` - A dedicated infrastructure layer handling service-to-service routing, security, reliability, and observability outside application code.
* [Well-Known Ports (22, 80, 443)](/software-engineering/infrastructure/network-ports.md) `[Concept]` _(draft)_ - Why ports 22, 80 and 443 matter beyond convention. Covers privileged ports, client defaults, browser port blocking, firewalls, and protocols that need a fixed port, plus what this means for a Runpod Pod.

## planning

* [Responding to Raw Ideas](/software-engineering/planning/responding-to-raw-ideas.md) `[Practice]` _(draft)_ - How to answer a new idea calmly, without promising what you can't guarantee or criticizing what you can't back up, based on Shape Up's "Interesting. Maybe some day."
* [Shape Up](/software-engineering/planning/shape-up.md) `[Reference]` _(draft)_ - Ryan Singer's book on Basecamp's product process; its core idea is the appetite, a fixed time budget with variable scope, set before the solution is designed.
* [Shaping Work Before the Pitch](/software-engineering/planning/shaping.md) `[Practice]` _(draft)_ - The steps that turn a raw idea into a pitch, following Shape Up. Narrow the problem, set an appetite, rough out the solution, find rabbit holes, then check it with experts while it is still easy to change.

## reliability

* [Metastable Failures](/software-engineering/reliability/metastable-failures.md) `[Concept]` - Outages that persist after their trigger is gone, because the degraded system does extra work (retries, cache misses) that keeps it overloaded — fixed by attacking the feedback loop, not the trigger.
* [Site Reliability Engineering](/software-engineering/reliability/sre.md) `[Practice]` _(draft)_ - Google's discipline of running production with software engineering: explicit reliability targets, an error budget that balances them against change, and automation in place of manual operations.
* [Toil](/software-engineering/reliability/toil.md) `[Practice]` - Manual, repetitive operational work that scales with the service — capped and engineered away so a team's effort grows sublinearly with what it runs.

# _types

* [Concept](/_types/concept.md) `[Concept Type]` - A conceptual explanation of an agent or software-system mechanism.
* [Decision Model](/_types/decision-model.md) `[Concept Type]` - A model that scores supplied actions or returns typed decisions.
* [Knowledge Area](/_types/knowledge-area.md) `[Concept Type]` - A subject overview that shares a sidebar section and graph node with its same-named directory.
* [Knowledge Format](/_types/knowledge-format.md) `[Concept Type]` - A format for expressing knowledge or structured data.
* [Model Provider](/_types/model-provider.md) `[Concept Type]` - A dated provider API pricing and caching note, rather than a live price feed.
* [Practice](/_types/practice.md) `[Concept Type]` - An engineering workflow, operating practice, or reliability principle.
* [Protocol](/_types/protocol.md) `[Concept Type]` - An interaction contract between applications, agents, tools, or services.
* [Reference](/_types/reference.md) `[Concept Type]` - A reading note, resource collection, or learning resource.
* [Security Control](/_types/security-control.md) `[Concept Type]` - A control applied around model or tool interactions.
* [Security Risk](/_types/security-risk.md) `[Concept Type]` - An agent attack surface described by the source security notes.
* [Tool](/_types/tool.md) `[Concept Type]` - A concrete agent, framework, library, or platform described in the maintained notes.

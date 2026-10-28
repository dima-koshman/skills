---
okf_version: "0.2"
---

* [AI Engineering](/ai-engineering.md) `[Knowledge Area]` - Personal knowledge base for AI engineering concepts.
* [Software Engineering](/software-engineering.md) `[Knowledge Area]` - Personal knowledge base for general software development and distributed-systems concepts.

# ai-engineering

* [Agent Harness](/ai-engineering/harness.md) `[Knowledge Area]` - The runtime scaffolding around the model loop: tool dispatch, state, sandboxing, and loop control.
* [Agent Security](/ai-engineering/security.md) `[Knowledge Area]` - How enterprise agent platforms are attacked and defended — the OWASP Agentic Top 10 risks and the mitigations that contain them.
* [Agents](/ai-engineering/agents.md) `[Knowledge Area]` - Agent architectures, coding-agent implementations, and protocols for delegation and peer coordination.
* [AI Compute](/ai-engineering/compute.md) `[Knowledge Area]` - How AI workloads run on hardware — inference and serving techniques, GPU and NPU programming models, performance limits, compilers, CUDA, Mojo and MAX.
* [AI Development](/ai-engineering/development.md) `[Knowledge Area]` - Artifact-driven software development and telemetry-led diagnosis with AI agents.
* [Context and Knowledge](/ai-engineering/context.md) `[Knowledge Area]` - Context assembly, memory, retrieval, skills, and portable knowledge formats for agents.
* [Enterprise Gateways](/ai-engineering/enterprise.md) `[Knowledge Area]` - Model-side and tool-side gateways that centralize access, policy, routing, and audit.
* [Model Providers and Evaluation](/ai-engineering/providers.md) `[Knowledge Area]` - Provider-specific API pricing and caching notes alongside independent model evaluation resources.
* [Models](/ai-engineering/models.md) `[Knowledge Area]` - Language-model architecture and typed decision models used inside agent workflows.
* [Observability and Evaluation](/ai-engineering/observability.md) `[Knowledge Area]` - Tracing, datasets, and evaluators used to inspect and improve agent behavior.

## agents

* [Agent](/ai-engineering/agents/agent.md) `[Concept]` - The loop, planning, subagents, tools, and memory that turn an LLM into a task-completing agent.
* [Agent Client Protocol](/ai-engineering/agents/ACP.md) `[Protocol]` - ACP standardizes communication between code editors/IDEs and coding agents.
* [Agent2Agent](/ai-engineering/agents/A2A.md) `[Protocol]` - An protocol designed by Google enabling communication and interoperability between opaque agentic applications.
* [Antigravity](/ai-engineering/agents/antigravity.md) `[Tool]` - Google's agent-first development platform built on Gemini — an IDE, desktop app, and CLI sharing one agent harness.
* [Claude Code](/ai-engineering/agents/claude-code.md) `[Tool]` - Anthropic's coding agent — Claude in a loop with file, shell, and code tools, available as CLI, IDE extension, and SDK.
* [Codex](/ai-engineering/agents/codex.md) `[Tool]` - OpenAI's coding agent — an open-source terminal CLI plus cloud environments, powered by OpenAI's coding models.
* [Deep Agents](/ai-engineering/agents/deep-agents.md) `[Tool]` - Opinionated LangChain package for high level agent patterns.
* [Devin](/ai-engineering/agents/devin.md) `[Tool]` - Cognition's autonomous AI software engineer — a cloud agent that executes coding tasks end-to-end in its own sandbox.
* [OpenCode](/ai-engineering/agents/opencode.md) `[Tool]` - Open-source, terminal-native, model-agnostic coding agent — a vendor-neutral alternative to Claude Code.
* [Peer Agents](/ai-engineering/agents/peer-agents.md) `[Concept]` - Independently governed agents that own goals and coordinate as peers rather than through a permanent parent.

## compute

* [Compute, Memory and Overhead Bound](/ai-engineering/compute/performance-regimes.md) `[Concept]` - A slow model is limited by one of three things — math throughput, memory bandwidth, or host-side overhead — and each needs a different fix.
* [CUDA Ecosystem](/ai-engineering/compute/cuda.md) `[Concept]` - Why NVIDIA's CUDA became the default AI software stack, why chip companies struggle to match it, and the main attempts to break the lock-in — compilers, Python DSLs, Mojo, and NVIDIA's own CUDA Rust.
* [LLM Inference and Serving](/ai-engineering/compute/serving.md) `[Knowledge Area]` - A map of autoregressive inference phases, KV memory, scheduling, attention kernels, precision and distributed serving trade-offs.
* [LLVM and MLIR](/ai-engineering/compute/compilers.md) `[Concept]` - The compiler infrastructure under Mojo — LLVM's shared intermediate representation that decouples languages from chips, and MLIR's many-level IRs (dialects) that keep AI operations meaningful until late in compilation.
* [MAX](/ai-engineering/compute/max.md) `[Tool]` - Modular's AI serving and modeling framework — OpenAI-compatible model serving, a PyTorch-like Python modeling API, and Mojo kernels for CPUs, GPUs and ASICs without depending on CUDA or ROCm.
* [Mojo](/ai-engineering/compute/mojo.md) `[Tool]` - Modular's Python-like systems language for CPUs, GPUs and other accelerators, built on MLIR; 1.0 and open source (Apache 2.0) since August 2026, owned by Qualcomm.
* [Neural Processing Unit (NPU)](/ai-engineering/compute/npu.md) `[Concept]` - A hardware accelerator built specifically for neural-network math, usually low-precision and power-efficient, programmed with explicit memory movement rather than the GPU's thread model; Google's TPU is one, and GPU Tensor Cores are the same idea as a unit inside a GPU.
* [SIMD and SIMT](/ai-engineering/compute/simd-simt.md) `[Concept]` - Two ways to run one instruction over many data elements — explicit vector instructions (SIMD) vs NVIDIA's per-thread model on top of vector hardware (SIMT) — and why the difference matters for portable kernels.

### serving

* [Cache-aware Inference Routing](/ai-engineering/compute/serving/inference-routing.md) `[Concept]` - Choose serving workers using prefix locality, queueing and KV pressure rather than only request counts.
* [Chunked Prefill](/ai-engineering/compute/serving/chunked-prefill.md) `[Concept]` - Splitting prompt processing into bounded chunks lets a scheduler interleave new prompts with ongoing decode work.
* [Context Parallelism](/ai-engineering/compute/serving/context-parallelism.md) `[Concept]` - Distribute one request's sequence-related attention work or KV state across devices to handle long contexts and reduce per-device pressure.
* [Continuous Batching](/ai-engineering/compute/serving/continuous-batching.md) `[Concept]` - The server updates the active request batch between generation iterations so completed requests leave and new work can enter.
* [CUDA Graphs](/ai-engineering/compute/serving/cuda-graphs.md) `[Concept]` - Capture and replay a compatible sequence of GPU operations to reduce repeated host dispatch and kernel-launch overhead.
* [Expert Parallelism](/ai-engineering/compute/serving/expert-parallelism.md) `[Concept]` - Place different mixture-of-experts networks on different GPUs and route token activations to the devices that own selected experts.
* [FlashAttention](/ai-engineering/compute/serving/flash-attention.md) `[Concept]` - Tiled attention keeps intermediates on chip and avoids materializing the full attention-score matrix in GPU memory.
* [Grouped-Query Attention](/ai-engineering/compute/serving/grouped-query-attention.md) `[Concept]` - Multiple query heads share fewer key/value heads, reducing KV state and decode bandwidth through a model architecture choice.
* [Inference Data Parallelism](/ai-engineering/compute/serving/data-parallelism.md) `[Concept]` - Replicate model capacity across workers and route independent requests to different replicas to scale aggregate serving throughput.
* [Kernel Fusion](/ai-engineering/compute/serving/kernel-fusion.md) `[Concept]` - Execute multiple operations inside one GPU kernel to reduce launch overhead and avoid writing intermediate tensors to global memory.
* [KV Cache](/ai-engineering/compute/serving/kv-cache.md) `[Concept]` - Cached attention keys and values avoid recomputing earlier tokens while making sequence length and concurrency consume serving memory.
* [KV Cache Offloading](/ai-engineering/compute/serving/kv-cache-offloading.md) `[Concept]` - Moving KV state to CPU memory or storage trades GPU residency for transfer work and potentially avoids later recomputation.
* [LLM Quantization](/ai-engineering/compute/serving/quantization.md) `[Concept]` - Represent weights, activations or KV state with fewer bits to reduce memory and potentially accelerate supported inference kernels.
* [LLM Serving Metrics](/ai-engineering/compute/serving/serving-metrics.md) `[Concept]` - Latency, throughput and goodput measure different serving goals and must be compared under a specified workload and load.
* [PagedAttention](/ai-engineering/compute/serving/paged-attention.md) `[Concept]` - A block table maps logical token positions to noncontiguous KV blocks, reducing allocation waste and enabling flexible sharing.
* [Pipeline Parallelism](/ai-engineering/compute/serving/pipeline-parallelism.md) `[Concept]` - Place successive groups of model layers on different devices and pipeline requests or microbatches through the stages.
* [Prefill and Decode](/ai-engineering/compute/serving/prefill-decode.md) `[Concept]` - The two inference phases process a known prompt in parallel, then generate a dependent output sequence token by token.
* [Prefill–Decode Disaggregation](/ai-engineering/compute/serving/prefill-decode-disaggregation.md) `[Concept]` - Separate worker pools perform prompt processing and token generation, transferring KV state between independently tuned phases.
* [Prefix Caching](/ai-engineering/compute/serving/prefix-caching.md) `[Concept]` - Reuse stored KV state for a matching prompt prefix to skip repeated prefill computation across requests.
* [Speculative Decoding](/ai-engineering/compute/serving/speculative-decoding.md) `[Concept]` - A cheap proposer drafts multiple tokens and a target model verifies them together to reduce serial target-model passes.
* [Tensor Parallelism](/ai-engineering/compute/serving/tensor-parallelism.md) `[Concept]` - Split tensors and layer computation across GPUs so a model replica can use their combined memory and compute.

## context

* [Agent Skills](/ai-engineering/context/skills.md) `[Concept]` - Packaged instruction files an agent loads on demand — most useful as behavior control, and a context tax when installed indiscriminately.
* [Context Engineering](/ai-engineering/context/context-engineering.md) `[Concept]` - Deliberately assembling what goes into the model's context window — instructions, tools, retrieved data, memory, and history.
* [Memory](/ai-engineering/context/memory.md) `[Concept]` - How an agent carries state across steps and sessions — short-term context plus durable long-term stores.
* [Model Context Protocol (MCP)](/ai-engineering/context/mcp.md) `[Protocol]` - Open protocol standardizing how LLM apps expose and consume tools, resources, and prompts.
* [OKF Visualizers](/ai-engineering/context/okf-visualizers.md) `[Concept]` - Comparison of the upstream static HTML viewer with our custom graph-and-reader renderer, including adoption instructions and compatibility limits.
* [Open Knowledge Format (OKF)](/ai-engineering/context/okf.md) `[Knowledge Format]` - Google's vendor-neutral markdown-plus-frontmatter standard for agent-readable knowledge.
* [OpenWiki](/ai-engineering/context/openwiki.md) `[Tool]` - LangChain's early-stage CLI for generating and maintaining agent-facing Markdown wikis from local knowledge sources.
* [Prompt Caching](/ai-engineering/context/prompt-caching.md) `[Concept]` - Reusing cached prefix tokens across LLM requests to minimize latency and token costs, and how to design agent harnesses around cache preservation.
* [RAG](/ai-engineering/context/rag.md) `[Concept]` - Retrieval-augmented generation — fetching relevant documents at query time and adding them to the model's context.

## development

* [AI-Native SDLC](/ai-engineering/development/ai-native-sdlc.md) `[Practice]` - A software lifecycle rebuilt as a loop of committed artifacts, with agents doing the work between gates and humans owning every judgment call.
* [Observability-Driven AI-Assisted Development](/ai-engineering/development/observability-driven-development.md) `[Practice]` - A development loop where AI agents use real runtime telemetry as evidence for diagnosis, remediation, and verification.

## enterprise

* [LLM Gateway](/ai-engineering/enterprise/llm-gateway.md) `[Concept]` - A control plane sitting between AI clients and models/tools for auth, routing, policy, and observability.
* [MCP Gateway](/ai-engineering/enterprise/mcp-gateway.md) `[Concept]` - An enterprise gateway multiplexing MCP servers behind auth, permissions, secrets, and audit.

## harness

* [Agent Sandboxes](/ai-engineering/harness/sandboxes.md) `[Practice]` - Run the harness outside the sandbox and call the sandbox as a tool, keeping session state in a durable store, so harness, sandbox and session can each fail or be replaced on their own ("cattle, not pets").
* [Dynamic Subagents](/ai-engineering/harness/dynamic-subagents.md) `[Concept]` - An agent writes code that dispatches subagents, branches on their results, and controls what returns to the coordinating model.
* [Frontend Tools](/ai-engineering/harness/frontend-tools.md) `[Concept]` - Client-side tools executed in the frontend, typically for UI interactions — a newer, less standardized category.
* [Model Routing](/ai-engineering/harness/model-routing.md) `[Practice]` - Choosing a cheaper or stronger model per task belongs in the harness, which knows the task, and should happen once per thread, because switching models mid-conversation throws away the prompt cache.
* [Programmatic Tool Calling](/ai-engineering/harness/programmatic-tool-calling.md) `[Concept]` - Code mode and programmatic tool calling move tool or subagent orchestration into generated code, keeping intermediate results outside the main model context.
* [Provider-Side Tools](/ai-engineering/harness/provider-tools.md) `[Concept]` - Tools defined and executed by the model provider — built-in web search, code execution — that clients just enable.
* [Subagents](/ai-engineering/harness/subagents.md) `[Concept]` - Delegating focused subtasks to separate agent instances, and orchestrating multiple agents together.
* [Tools](/ai-engineering/harness/tools.md) `[Concept]` - The primitive that turns an LLM into an agent — functions the model can call to act on and read from its environment.

## models

* [Contrastive Language Models (CLM)](/ai-engineering/models/clm.md) `[Decision Model]` - Open-source state-action scoring models with a TypeSafe-compatible API for typed decisions and candidate ranking.
* [Jev](/ai-engineering/models/jev.md) `[Decision Model]` - TypeSafe's System One model for fast typed decisions with probabilities, composed into software workflows.
* [LLM Architecture](/ai-engineering/models/llm-architecture.md) `[Concept]` - Design choices inside modern open-weight LLMs — sparsity, attention efficiency, and the empirical tweaks — and the two main ways to make them multimodal.
* [ScaleDown](/ai-engineering/models/scaledown.md) `[Decision Model]` - Hosted constrained decoding models (CDMs) for summarizing, compressing, extracting and classifying agent context — small task-specific models that return only answers the task allows.

## observability

* [Langfuse](/ai-engineering/observability/langfuse.md) `[Tool]` - Open-source LLM observability and tracing, OpenTelemetry-friendly.
* [LangSmith](/ai-engineering/observability/langsmith.md) `[Tool]` - LangChain's tracing and evaluation platform for LLM/agent observability.
* [LangSmith Evals](/ai-engineering/observability/langsmith-evals.md) `[Tool]` - Dataset and evaluator tooling in LangSmith for offline and online agent evaluation.

## providers

* [Claude](/ai-engineering/providers/claude.md) `[Model Provider]` - Anthropic Claude API token pricing and prompt-caching mechanics — cache multipliers, TTLs, and cost-optimization guidance.
* [Gemini](/ai-engineering/providers/gemini.md) `[Model Provider]` - Google Gemini API token pricing plus implicit and explicit context caching, with break-even guidance.
* [GPT](/ai-engineering/providers/gpt.md) `[Model Provider]` - OpenAI GPT API token pricing and prompt caching — the 272K long-context cliff, cache-write fees, and keep-alive economics.
* [LLM Leaderboards](/ai-engineering/providers/leaderboards.md) `[Reference]` - A curated bookmark set and benchmark map for choosing reliable, independent LLM evaluation sources across capabilities.

## security

* [Agentic Security Risks](/ai-engineering/security/risks.md) `[Knowledge Area]` - The ten agentic attack surfaces described in the existing OWASP reference notes.
* [Security Controls](/ai-engineering/security/mitigations.md) `[Knowledge Area]` - Guardrails and personal-data masking controls around model and tool interactions.

### mitigations

* [Guardrails](/ai-engineering/security/mitigations/guardrails.md) `[Security Control]` - Input/output controls that constrain LLM behavior to a safe, policy-compliant envelope.
* [PII Masking & Anonymization](/ai-engineering/security/mitigations/pii-masking.md) `[Security Control]` - Detecting and redacting or tokenizing personal data in LLM inputs/outputs, reversibly where needed.

### risks

* [Agent Goal Hijack](/ai-engineering/security/risks/agent-goal-hijack.md) `[Security Risk]` - Adversarial input redirects the agent's plan or objective — OWASP's #1 agentic risk, prompt injection being the primary mechanism.
* [Agent Identity & Privilege Abuse](/ai-engineering/security/risks/identity-privilege-abuse.md) `[Security Risk]` - The agent's identity or permissions are misused, impersonated, or escalated.
* [Agentic Supply Chain Compromise](/ai-engineering/security/risks/supply-chain-compromise.md) `[Security Risk]` - Malicious or compromised components — tools, MCP servers, models, dependencies — enter the agent supply chain.
* [Cascading Agent Failures](/ai-engineering/security/risks/cascading-agent-failures.md) `[Security Risk]` - A local failure or compromise propagates across agents and tools into a systemic failure.
* [Human-Agent Trust Exploitation](/ai-engineering/security/risks/human-agent-trust-exploitation.md) `[Security Risk]` - The agent is used to manipulate the human, or humans over-trust the agent's output.
* [Insecure Inter-Agent Communication](/ai-engineering/security/risks/insecure-inter-agent-communication.md) `[Security Risk]` - Trust, spoofing, or tampering weaknesses in messaging between agents.
* [Memory & Context Poisoning](/ai-engineering/security/risks/memory-context-poisoning.md) `[Security Risk]` - Malicious content persists in the agent's memory or context and influences later decisions.
* [Rogue Agents](/ai-engineering/security/risks/rogue-agents.md) `[Security Risk]` - Unauthorized or compromised agents operating outside governance and oversight.
* [Tool Misuse & Exploitation](/ai-engineering/security/risks/tool-misuse.md) `[Security Risk]` - The agent invokes tools in ways they were not intended or authorized for.
* [Unexpected Code Execution](/ai-engineering/security/risks/unexpected-code-execution.md) `[Security Risk]` - The agent executes attacker-influenced code, e.g. via a code interpreter or a tool with an RCE path.

# software-engineering

* [Distributed Systems](/software-engineering/distributed-systems.md) `[Knowledge Area]` - Reading notes on storage, replication, consensus, and large-scale data processing.
* [Frontend Engineering](/software-engineering/frontend.md) `[Knowledge Area]` - Server-rendered interactivity and the trade-offs of the hypermedia approach.
* [Learning Resources](/software-engineering/learning.md) `[Knowledge Area]` - Practical labs and structured training for Linux, Kubernetes, and software infrastructure.
* [Reliability Engineering](/software-engineering/reliability.md) `[Knowledge Area]` - Reliability targets, simplicity, and toil reduction as software engineering practices.
* [Service Communication](/software-engineering/communication.md) `[Knowledge Area]` - Protocol Buffers schemas and gRPC contracts for communication between services.
* [Service Infrastructure](/software-engineering/infrastructure.md) `[Knowledge Area]` - Service meshes and data, control, and management planes around distributed applications.
* [Software Architecture](/software-engineering/architecture.md) `[Knowledge Area]` - Component boundaries, communication styles, and dependency trade-offs in software design.
* [Source Control](/software-engineering/source-control.md) `[Knowledge Area]` - How code is stored, versioned, and shared across projects — repository strategy and version-control systems at scale.

## architecture

* [Architectural Patterns](/software-engineering/architecture/architectural-patterns.md) `[Concept]` - Choose component boundaries, communication styles, and dependency directions according to the forces acting on a system.

## communication

* [gRPC](/software-engineering/communication/grpc.md) `[Protocol]` - RPC framework using Protocol Buffers as its IDL to generate client and server stubs — a service-to-service alternative to REST.
* [Protocol Buffers](/software-engineering/communication/protobuf.md) `[Knowledge Format]` - Language-neutral binary serialization for small structured records — schema-first `.proto` definitions compiled into native bindings.

## distributed-systems

* [Bigtable](/software-engineering/distributed-systems/bigtable.md) `[Reference]` - A distributed sorted store whose data layout is part of the application design.
* [Cosmos DB Partitioning](/software-engineering/distributed-systems/cosmos-db-partitioning.md) `[Concept]` - How Azure Cosmos DB maps many logical partitions (one per partition-key value) onto few physical partitions, why per-key limits are ceilings rather than guarantees, and why partitioning alone does not isolate tenants.
* [Designing Data-Intensive Applications](/software-engineering/distributed-systems/designing_data_intensive_applications.md) `[Reference]` - Martin Kleppmann's guide to the trade-offs behind reliable storage and data processing.
* [Dynamo](/software-engineering/distributed-systems/dynamo.md) `[Reference]` - An availability-oriented key-value store that exposes conflict resolution to applications.
* [Google File System](/software-engineering/distributed-systems/google_file_system.md) `[Reference]` - A filesystem designed around large data workloads and routine hardware failure.
* [MapReduce](/software-engineering/distributed-systems/map_reduce.md) `[Reference]` - A programming model and runtime for fault-tolerant parallel batch processing.
* [OpenAI Habitat](/software-engineering/distributed-systems/openai-habitat.md) `[Reference]` - How OpenAI scaled its online storage layer to 70M+ requests per second for 1B+ weekly users — a library turned Python service turned Rust service with a deliberately narrow API in front of Azure Cosmos DB, and a round trip from shared to dedicated and back to shared database containers.
* [Raft](/software-engineering/distributed-systems/raft.md) `[Reference]` - Consensus for a replicated log, organized around leader election, replication, and safety.
* [Spanner](/software-engineering/distributed-systems/spanner.md) `[Reference]` - A globally replicated database combining transactions with explicit clock uncertainty.
* [TAO](/software-engineering/distributed-systems/tao.md) `[Reference]` - Facebook's read-optimized, geographically distributed graph store — a fixed objects-and-associations API served by a two-tier cache over sharded MySQL, replacing client-side memcache logic.

## frontend

* [htmx](/software-engineering/frontend/htmx.md) `[Tool]` - Small, dependency-free JavaScript library that lets any HTML element issue HTTP requests and swap the returned HTML into the page — interactivity without a frontend framework.

## infrastructure

* [Data, Control & Management Planes](/software-engineering/infrastructure/planes.md) `[Concept]` - The decomposition of a distributed system into traffic-carrying, policy-distributing, and operator-facing layers.
* [Service Mesh](/software-engineering/infrastructure/service-mesh.md) `[Concept]` - A dedicated infrastructure layer handling service-to-service routing, security, reliability, and observability outside application code.

## learning

* [LabEx](/software-engineering/learning/labex.md) `[Reference]` - Browser-based hands-on labs and structured skill trees for Linux, DevOps, cybersecurity, and programming.
* [Linux Foundation Training](/software-engineering/learning/linux-foundation.md) `[Reference]` - Structured open-source training, including Introduction to Kubernetes (LFS158) and its hands-on exercises.

## reliability

* [Metastable Failures](/software-engineering/reliability/metastable-failures.md) `[Concept]` - Outages that persist after their trigger is gone, because the degraded system does extra work (retries, cache misses) that keeps it overloaded — fixed by attacking the feedback loop, not the trigger.
* [Simplicity](/software-engineering/reliability/simplicity.md) `[Practice]` - Reduce accidental complexity to make production systems easier to understand, change, and operate reliably.
* [Site Reliability Engineering](/software-engineering/reliability/sre.md) `[Practice]` - Google's discipline of running production with software engineering: explicit reliability targets, an error budget that balances them against change, and automation in place of manual operations.
* [Toil](/software-engineering/reliability/toil.md) `[Practice]` - Manual, repetitive operational work that scales with the service — capped and engineered away so a team's effort grows sublinearly with what it runs.

## source-control

* [Monorepo vs Polyrepo](/software-engineering/source-control/monorepo.md) `[Practice]` - Keep many projects in one version-controlled repository, or give each its own — a trade between atomic, globally consistent change and independent, loosely coupled ownership.

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

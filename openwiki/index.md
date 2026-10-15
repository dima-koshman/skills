---
okf_version: "0.2"
---

* [Quickstart](/quickstart.md) `[navigation concept]` - A compact task-routing map for the AI-agent ecosystem, model, development, security, and software-engineering foundations pages. Use it to choose a subject route, then follow the cross-cutting path and verify consequential conclusions against primary evidence.

# architecture

* [Agent Ecosystem and Coordination](/architecture/agent-ecosystem.md) `[architecture overview]` - Defines the boundary between agent architectures, harnesses, subagents, and independently governed peers, then compares the coordination protocols and concrete coding agents described in the source notes.
* [Agent Systems Architecture](/architecture/agent-systems.md) `[architecture concept]` - Explains how model-driven agents become executing systems through a harness, model loop, tools, context, state, subagents, workflows, and gateways. Defines ownership boundaries, lifecycle invariants, failure behavior, security controls, and safe extension points.

# concepts

* [Agent Skills and Tooling](/concepts/skills-and-tooling.md) `[conceptual guide]` - Explains the boundary between procedural skills, client and provider tools, frontend execution, workflows, and parent-controlled subagents. Covers progressive disclosure, invocation and scope, execution ownership, lifecycle, trust, and operational tests.
* [Context, Memory, and Knowledge Retrieval](/concepts/context-and-knowledge.md) `[conceptual guide]` - A practical boundary model for assembling agent context and choosing among working state, memory, query-time retrieval, MCP resources, and durable knowledge. Explains freshness, authority, provenance, security, and verification decisions.
* [Knowledge Formats and Visualization](/concepts/knowledge-format-and-visualization.md) `[format and tooling concept]` - Explains OKF's one-concept-per-Markdown-file model, metadata and provenance boundaries, version compatibility, indexing, and the limits of local and upstream visualizer projections.
* [Model Architecture and Selection](/concepts/model-landscape.md) `[concept guide]` - A practical map of decoder-model architecture, decision-model intent, provider integration trade-offs, and evaluation strategy. Use it to separate capability and serving constraints from harness policy, gateway controls, and task-specific validation.

# integrations

* [Model Providers and Agent Protocols](/integrations/models-and-protocols.md) `[integration concept]` - Compares model-provider integration and evaluation with agent-to-agent, tool/resource, and enterprise gateway boundaries. Explains how providers, protocols, and gateways connect to an agent harness without conflating their responsibilities.

# operations

* [Agent Security, Observability, and Evaluation](/operations/security-and-observability.md) `[operational security guide]` - A threat-to-control and signal-to-action guide for operating agent systems. Connects gateways, least privilege, privacy boundaries, tracing, bounded investigation, evaluation, and evidence-driven change.
* [Knowledge Maintenance and Provenance](/operations/maintenance-and-provenance.md) `[maintenance guide]` - Operational guidance for refreshing connector snapshots, manifests, source-specific synthesis, citations, freshness, version pins, and generated pages without confusing source notes with derived knowledge. Defines authority boundaries, lifecycle states, compatibility checks, and evidence gaps.

# software-engineering

* [Distributed Communication and Service Infrastructure](/software-engineering/distributed-systems.md) `[architecture concept]` - How Protocol Buffers and gRPC define typed service contracts, and how control planes, data planes, and service meshes govern traffic, policy, security, and operations. Use this page to choose boundaries, understand request flow, and reason about compatibility and failure behavior.
* [Software Architecture and Development Practice](/software-engineering/architecture-and-development.md) `[architecture and development guide]` - A boundary-focused guide to selecting architectural structures, communication styles, and change strategies. It connects pattern trade-offs with contracts, failure handling, operability, testing, and incremental delivery.
* [Software Reliability and Learning Practice](/software-engineering/reliability-and-learning.md) `[engineering practice]` - A practical reliability practice that connects simplicity, bounded observability, causal verification, and structured learning across AI and distributed systems. It distinguishes runtime clues and generated summaries from authoritative source, test, and review evidence.

## distributed-systems

* [Distributed Systems Foundations and Designs](/software-engineering/distributed-systems/foundations.md) `[concept guide]` - A reading-oriented synthesis of distributed-systems failure, consistency, replication, storage, coordination, and batch-processing trade-offs. It compares landmark designs and points to the source notes and primary papers for deeper study.

## frontend

* [HTMX and Server-Rendered Interactivity](/software-engineering/frontend/htmx.md) `[frontend architecture concept]` - Explains how htmx adds browser interactions through HTML attributes and server-rendered HTML fragments, without making a frontend framework the application UI. Covers the request/response contract, suitable use cases, framework boundary, operational setup, and trade-offs.

# workflows

* [AI-Native Development Workflow](/workflows/ai-native-development.md) `[workflow concept]` - A source-noted workflow for AI-assisted software development from intent and planning through implementation, testing, review, deployment, observability, and learning. It defines what agents can accelerate, which controls must be deterministic, and where engineers retain accountability.

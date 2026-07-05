---
okf_version: "0.1"
---

# Architecture Pattern

* [Agent Architecture](/agents/agent.md) - The loop, planning, subagents, tools, and memory that turn an LLM into a task-completing agent.
* [Agent Harness](/agents/harness.md) - The runtime scaffolding around the model loop: tool dispatch, state, sandboxing, and loop control.
* [LLM Gateway](/enterprise/llm-gateway.md) - A control plane sitting between AI clients and models/tools for auth, routing, policy, and observability.
* [MCP Gateway](/enterprise/mcp-gateway.md) - An enterprise gateway multiplexing MCP servers behind auth, permissions, secrets, and audit.
* [Subagents & Multi-Agent](/agents/subagents.md) - Delegating focused subtasks to separate agent instances, and orchestrating multiple agents together.

# Concept

* [Frontend Tools](/tools/frontend-tools.md) - Client-side tools executed in the frontend, typically for UI interactions — a newer, less standardized category.
* [Memory](/agents/memory.md) - How an agent carries state across steps and sessions — short-term context plus durable long-term stores.
* [Provider-Side Tools](/tools/provider-tools.md) - Tools defined and executed by the model provider — built-in web search, code execution — that clients just enable.
* [Tools](/tools/tools.md) - The primitive that turns an LLM into an agent — functions the model can call to act on and read from its environment.

# Control

* [Guardrails](/security/controls/guardrails.md) - Input/output controls that constrain LLM behavior to a safe, policy-compliant envelope.
* [PII Masking & Anonymization](/security/controls/pii-masking.md) - Detecting and redacting or tokenizing personal data in LLM inputs/outputs, reversibly where needed.

# Framework

* [deepagents](/agents/deepagents.md) - Opinionated LangChain package for high level agent patterns.

# Knowledge Format

* [Open Knowledge Format (OKF)](/context/okf.md) - Google's vendor-neutral markdown-plus-frontmatter standard for agent-readable knowledge.

# Overview

* [AI Engineering](/ai-engineering.md) - Personal knowledge base for AI engineering concepts.
* [Security](/security/security.md) - How enterprise agent platforms are attacked and defended — the OWASP Agentic Top 10 threats and the controls that contain them.

# Protocol

* [Model Context Protocol (MCP)](/context/mcp.md) - Open protocol standardizing how LLM apps expose and consume tools, resources, and prompts.

# Technique

* [Context Engineering](/context/context-engineering.md) - Deliberately assembling what goes into the model's context window — instructions, tools, retrieved data, memory, and history.
* [RAG](/context/rag.md) - Retrieval-augmented generation — fetching relevant documents at query time and adding them to the model's context.
* [Workflows](/agents/workflows.md) - Workflows let an agent orchestrate its tool calls programmatically — scripted tool use for lower token cost and long-running tasks.

# Threat

* [Agent Goal Hijack](/security/threats/agent-goal-hijack.md) - Adversarial input redirects the agent's plan or objective — OWASP's #1 agentic risk, prompt injection being the primary mechanism.
* [Agent Identity & Privilege Abuse](/security/threats/identity-privilege-abuse.md) - The agent's identity or permissions are misused, impersonated, or escalated.
* [Agentic Supply Chain Compromise](/security/threats/supply-chain-compromise.md) - Malicious or compromised components — tools, MCP servers, models, dependencies — enter the agent supply chain.
* [Cascading Agent Failures](/security/threats/cascading-agent-failures.md) - A local failure or compromise propagates across agents and tools into a systemic failure.
* [Human-Agent Trust Exploitation](/security/threats/human-agent-trust-exploitation.md) - The agent is used to manipulate the human, or humans over-trust the agent's output.
* [Insecure Inter-Agent Communication](/security/threats/insecure-inter-agent-communication.md) - Trust, spoofing, or tampering weaknesses in messaging between agents.
* [Memory & Context Poisoning](/security/threats/memory-context-poisoning.md) - Malicious content persists in the agent's memory or context and influences later decisions.
* [Rogue Agents](/security/threats/rogue-agents.md) - Unauthorized or compromised agents operating outside governance and oversight.
* [Tool Misuse & Exploitation](/security/threats/tool-misuse.md) - The agent invokes tools in ways they were not intended or authorized for.
* [Unexpected Code Execution](/security/threats/unexpected-code-execution.md) - The agent executes attacker-influenced code, e.g. via a code interpreter or a tool with an RCE path.

# Tool

* [Langfuse](/observability/langfuse.md) - Open-source LLM observability and tracing, OpenTelemetry-friendly.
* [LangSmith](/observability/langsmith.md) - LangChain's tracing and evaluation platform for LLM/agent observability.
* [LangSmith Evals](/observability/langsmith-evals.md) - Dataset and evaluator tooling in LangSmith for offline and online agent evaluation.

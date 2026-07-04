---
okf_version: "0.1"
---

# Architecture Pattern

* [Agent Architecture](/agents/agent-architecture.md) - The loop, planning, subagents, tools, and memory that turn an LLM into a task-completing agent.
* [Agent Harness](/agents/harness.md) - The runtime scaffolding around the model loop: tool dispatch, state, sandboxing, and loop control.
* [LLM Gateway](/enterprise/llm-gateway.md) - A control plane sitting between AI clients and models/tools for auth, routing, policy, and observability.
* [MCP Gateway](/enterprise/mcp-gateway.md) - An enterprise gateway multiplexing MCP servers behind auth, permissions, secrets, and audit.

# Control

* [Guardrails](/security/controls/guardrails.md) - Input/output controls that constrain LLM behavior to a safe, policy-compliant envelope.
* [PII Masking & Anonymization](/security/controls/pii-masking.md) - Detecting and redacting or tokenizing personal data in LLM inputs/outputs, reversibly where needed.

# Framework

* [deepagents](/agents/deepagents.md) - LangChain library packaging planning, subagents, memory, and human-in-the-loop on LangGraph.

# Knowledge Format

* [Open Knowledge Format (OKF)](/context/okf.md) - Google's vendor-neutral markdown-plus-frontmatter standard for agent-readable knowledge.

# Overview

* [AI Engineering Knowledge Base](/README.md) - A vendor-neutral concept graph for building enterprise AI platforms — gateway, agents, security, and lifecycle.

# Practice

* [AI Observability & Tracing](/observability/observability.md) - Capturing traces, spans, and metrics of LLM/agent execution to debug, evaluate, and monitor in production.
* [Evals & LLM-as-Judge](/evaluation/evals.md) - Systematic measurement of LLM/agent quality offline and online, often using model-graded scoring.

# Protocol

* [Model Context Protocol (MCP)](/context/mcp.md) - Open protocol standardizing how LLM apps expose and consume tools, resources, and prompts.

# Technique

* [Programmatic Tools & Code Mode](/agents/programmatic-tools.md) - Letting agents write and run code — interpreters, dynamic workflows — instead of only fixed tool calls.

# Threat

* [ASI01: Agent Goal Hijack](/security/threats/asi01-agent-goal-hijack.md) - Adversarial input redirects the agent's plan or objective — OWASP's
* [ASI02: Tool Misuse & Exploitation](/security/threats/asi02-tool-misuse.md) - The agent invokes tools in ways they were not intended or authorized for.
* [ASI03: Agent Identity & Privilege Abuse](/security/threats/asi03-identity-privilege-abuse.md) - The agent's identity or permissions are misused, impersonated, or escalated.
* [ASI04: Agentic Supply Chain Compromise](/security/threats/asi04-supply-chain-compromise.md) - Malicious or compromised components — tools, MCP servers, models, dependencies — enter the agent supply chain.
* [ASI05: Unexpected Code Execution](/security/threats/asi05-unexpected-code-execution.md) - The agent executes attacker-influenced code, e.g. via a code interpreter or a tool with an RCE path.
* [ASI06: Memory & Context Poisoning](/security/threats/asi06-memory-context-poisoning.md) - Malicious content persists in the agent's memory or context and influences later decisions.
* [ASI07: Insecure Inter-Agent Communication](/security/threats/asi07-insecure-inter-agent-communication.md) - Trust, spoofing, or tampering weaknesses in messaging between agents.
* [ASI08: Cascading Agent Failures](/security/threats/asi08-cascading-agent-failures.md) - A local failure or compromise propagates across agents and tools into a systemic failure.
* [ASI09: Human-Agent Trust Exploitation](/security/threats/asi09-human-agent-trust-exploitation.md) - The agent is used to manipulate the human, or humans over-trust the agent's output.
* [ASI10: Rogue Agents](/security/threats/asi10-rogue-agents.md) - Unauthorized or compromised agents operating outside governance and oversight.

# Tool

* [Langfuse](/observability/langfuse.md) - Open-source LLM observability and tracing, OpenTelemetry-friendly.
* [LangSmith](/observability/langsmith.md) - LangChain's tracing and evaluation platform for LLM/agent observability.
* [LangSmith Evals](/evaluation/langsmith-evals.md) - Dataset and evaluator tooling in LangSmith for offline and online agent evaluation.

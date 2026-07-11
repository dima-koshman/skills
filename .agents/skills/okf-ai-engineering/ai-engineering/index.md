---
okf_version: "0.1"
---

* [AI Engineering](/ai-engineering.md) `[Overview]` - Personal knowledge base for AI engineering concepts.

# agents

* [Agent](/agents/agent.md) `[Overview]` - The loop, planning, subagents, tools, and memory that turn an LLM into a task-completing agent.
* [Agent Client Protocol](/agents/ACP.md) `[Standard]` - ACP standardizes communication between code editors/IDEs and coding agents.
* [Agent2Agent](/agents/A2A.md) `[Standard]` - An protocol designed by Google enabling communication and interoperability between opaque agentic applications.
* [Antigravity](/agents/antigravity.md) `[Product]` - Google's agent-first development platform built on Gemini — an IDE, desktop app, and CLI sharing one agent harness.
* [Claude Code](/agents/claude-code.md) `[Product]` - Anthropic's coding agent — Claude in a loop with file, shell, and code tools, available as CLI, IDE extension, and SDK.
* [Codex](/agents/codex.md) `[Product]` - OpenAI's coding agent — an open-source terminal CLI plus cloud environments, powered by OpenAI's coding models.
* [Deep Agents](/agents/deep-agents.md) `[Product]` - Opinionated LangChain package for high level agent patterns.
* [Devin](/agents/devin.md) `[Product]` - Cognition's autonomous AI software engineer — a cloud agent that executes coding tasks end-to-end in its own sandbox.
* [OpenCode](/agents/opencode.md) `[Product]` - Open-source, terminal-native, model-agnostic coding agent — a vendor-neutral alternative to Claude Code.
* [Peer Agents](/agents/peer-agents.md) `[Technique]` - Independently governed agents that own goals and coordinate as peers rather than through a permanent parent.

# context

* [Context Engineering](/context/context-engineering.md) `[Technique]` - Deliberately assembling what goes into the model's context window — instructions, tools, retrieved data, memory, and history.
* [Memory](/context/memory.md) `[Technique]` - How an agent carries state across steps and sessions — short-term context plus durable long-term stores.
* [Model Context Protocol (MCP)](/context/mcp.md) `[Standard]` - Open protocol standardizing how LLM apps expose and consume tools, resources, and prompts.
* [Open Knowledge Format (OKF)](/context/okf.md) `[Standard]` - Google's vendor-neutral markdown-plus-frontmatter standard for agent-readable knowledge.
* [RAG](/context/rag.md) `[Technique]` - Retrieval-augmented generation — fetching relevant documents at query time and adding them to the model's context.

# enterprise

* [LLM Gateway](/enterprise/llm-gateway.md) `[Technique]` - A control plane sitting between AI clients and models/tools for auth, routing, policy, and observability.
* [MCP Gateway](/enterprise/mcp-gateway.md) `[Technique]` - An enterprise gateway multiplexing MCP servers behind auth, permissions, secrets, and audit.

# harness

* [Agent Harness](/harness/harness.md) `[Overview]` - The runtime scaffolding around the model loop: tool dispatch, state, sandboxing, and loop control.
* [Frontend Tools](/harness/frontend-tools.md) `[Technique]` - Client-side tools executed in the frontend, typically for UI interactions — a newer, less standardized category.
* [Provider-Side Tools](/harness/provider-tools.md) `[Technique]` - Tools defined and executed by the model provider — built-in web search, code execution — that clients just enable.
* [Subagents](/harness/subagents.md) `[Technique]` - Delegating focused subtasks to separate agent instances, and orchestrating multiple agents together.
* [Tools](/harness/tools.md) `[Overview]` - The primitive that turns an LLM into an agent — functions the model can call to act on and read from its environment.
* [Workflows](/harness/workflows.md) `[Technique]` - Workflows let an agent orchestrate its tool calls programmatically — scripted tool use for lower token cost and long-running tasks.

# observability

* [Langfuse](/observability/langfuse.md) `[Product]` - Open-source LLM observability and tracing, OpenTelemetry-friendly.
* [LangSmith](/observability/langsmith.md) `[Product]` - LangChain's tracing and evaluation platform for LLM/agent observability.
* [LangSmith Evals](/observability/langsmith-evals.md) `[Product]` - Dataset and evaluator tooling in LangSmith for offline and online agent evaluation.

# providers

* [Claude](/providers/claude.md) `[Product]` - Anthropic Claude API token pricing and prompt-caching mechanics — cache multipliers, TTLs, and cost-optimization guidance.
* [Gemini](/providers/gemini.md) `[Product]` - Google Gemini API token pricing plus implicit and explicit context caching, with break-even guidance.
* [GPT](/providers/gpt.md) `[Product]` - OpenAI GPT API token pricing and prompt caching — the 272K long-context cliff, cache-write fees, and keep-alive economics.

# security

* [Security](/security/security.md) `[Overview]` - How enterprise agent platforms are attacked and defended — the OWASP Agentic Top 10 risks and the mitigations that contain them.

## mitigations

* [Guardrails](/security/mitigations/guardrails.md) `[Technique]` - Input/output controls that constrain LLM behavior to a safe, policy-compliant envelope.
* [PII Masking & Anonymization](/security/mitigations/pii-masking.md) `[Technique]` - Detecting and redacting or tokenizing personal data in LLM inputs/outputs, reversibly where needed.

## risks

* [Agent Goal Hijack](/security/risks/agent-goal-hijack.md) `[Security risk]` - Adversarial input redirects the agent's plan or objective — OWASP's #1 agentic risk, prompt injection being the primary mechanism.
* [Agent Identity & Privilege Abuse](/security/risks/identity-privilege-abuse.md) `[Security risk]` - The agent's identity or permissions are misused, impersonated, or escalated.
* [Agentic Supply Chain Compromise](/security/risks/supply-chain-compromise.md) `[Security risk]` - Malicious or compromised components — tools, MCP servers, models, dependencies — enter the agent supply chain.
* [Cascading Agent Failures](/security/risks/cascading-agent-failures.md) `[Security risk]` - A local failure or compromise propagates across agents and tools into a systemic failure.
* [Human-Agent Trust Exploitation](/security/risks/human-agent-trust-exploitation.md) `[Security risk]` - The agent is used to manipulate the human, or humans over-trust the agent's output.
* [Insecure Inter-Agent Communication](/security/risks/insecure-inter-agent-communication.md) `[Security risk]` - Trust, spoofing, or tampering weaknesses in messaging between agents.
* [Memory & Context Poisoning](/security/risks/memory-context-poisoning.md) `[Security risk]` - Malicious content persists in the agent's memory or context and influences later decisions.
* [Rogue Agents](/security/risks/rogue-agents.md) `[Security risk]` - Unauthorized or compromised agents operating outside governance and oversight.
* [Tool Misuse & Exploitation](/security/risks/tool-misuse.md) `[Security risk]` - The agent invokes tools in ways they were not intended or authorized for.
* [Unexpected Code Execution](/security/risks/unexpected-code-execution.md) `[Security risk]` - The agent executes attacker-influenced code, e.g. via a code interpreter or a tool with an RCE path.

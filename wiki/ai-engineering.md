---
type: Knowledge Area
title: AI Engineering
description: Personal knowledge base for AI engineering concepts.
tags:
- ai-engineering
related:
- /ai-engineering/models/llm-architecture.md
- /ai-engineering/models/jev.md
- /ai-engineering/models/clm.md
- /ai-engineering/harness/mcp.md
- /ai-engineering/knowledge/okf.md
- /ai-engineering/context/context-engineering.md
- /ai-engineering/harness/tools.md
- /ai-engineering/platform/ai-gateways.md
- /ai-engineering/multi-agent/peer-agents.md
- /ai-engineering/harness.md
- /ai-engineering/multi-agent/subagents.md
- /ai-engineering/harness/programmatic-tool-calling.md
- /ai-engineering/harness/sandboxes.md
- /ai-engineering/harness/model-routing.md
- /ai-engineering/compute.md
- /ai-engineering/compute/software-stack/mojo.md
- /ai-engineering/compute/software-stack/max.md
- /ai-engineering/development/ai-native-sdlc.md
- /ai-engineering/development/observability-driven-development.md
- /ai-engineering/observability.md
- /ai-engineering/security.md
sources:
- id: ref-1
  resource: https://cognition.com/blog
  title: Cognition blog
- id: ref-2
  resource: https://www.langchain.com/blog
  title: LangChain blog
- id: ref-3
  resource: https://www.anthropic.com/engineering
  title: Anthropic Engineering blog
- id: ref-4
  resource: https://gofastmcp.com
  title: FastMCP
- id: ref-5
  resource: https://www.youtube.com/playlist?list=PLfaIDFEXuae3UwB1QGEjsRAr8BzCQss7s
  title: LangChain's Max Agency podcast
- id: ref-6
  resource: https://www.langchain.com/resources/the-agentic-operating-model
  title: The Agentic Operating Model — LangChain
- id: langchain-agents
  resource: https://docs.langchain.com/oss/python/langchain/agents
  title: Agents
  author: LangChain
- id: acp
  resource: https://agentclientprotocol.com/
  title: Agent Client Protocol
status: draft
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-18T12:00:00+04:00'
topics:
- /ai-engineering/compute.md
- /ai-engineering/context.md
- /ai-engineering/development.md
- /ai-engineering/harness.md
- /ai-engineering/knowledge.md
- /ai-engineering/models.md
- /ai-engineering/multi-agent.md
- /ai-engineering/observability.md
- /ai-engineering/platform.md
- /ai-engineering/security.md
---

## Map

- **Models** — [LLM architecture](/ai-engineering/models/llm-architecture.md): MoE sparsity,
  KV-cache-driven attention variants, and multimodal designs. Decision models:
  [Jev](/ai-engineering/models/jev.md) for typed System One decisions,
  [CLM](/ai-engineering/models/clm.md) as an open-source alternative, and
  [ScaleDown](/ai-engineering/models/scaledown.md). [Provider](/ai-engineering/models/providers.md) pricing and caching,
  and how far to trust [leaderboards](/ai-engineering/models/leaderboards.md).
- **Context** — what goes into the context window: [context engineering](/ai-engineering/context/context-engineering.md)
  (with [memory](/ai-engineering/context/context-engineering.md#memory) and
  [RAG](/ai-engineering/context/context-engineering.md#retrieval-augmented-generation-rag)),
  [prompt caching](/ai-engineering/context/prompt-caching.md),
  [tool result offloading](/ai-engineering/context/tool-result-offloading.md) and [skills](/ai-engineering/context/skills.md).
- **Knowledge** — knowledge bases agents read: the [Open Knowledge Format](/ai-engineering/knowledge/okf.md),
  [its visualizers](/ai-engineering/knowledge/okf-visualizers.md) and [OpenWiki](/ai-engineering/knowledge/openwiki.md).
- **Harness** — the machinery that runs an [agent](/ai-engineering.md#agent): the [harness](/ai-engineering/harness.md)
  and its implementations ([Claude Code](/ai-engineering/harness.md#claude-code), [Codex](/ai-engineering/harness.md#codex),
  [Antigravity](/ai-engineering/harness.md#antigravity), [OpenCode](/ai-engineering/harness.md#opencode),
  [Deep Agents](/ai-engineering/harness.md#deep-agents)), the [tools](/ai-engineering/harness/tools.md) primitive
  (backend, [provider-side](/ai-engineering/harness/tools.md#provider-side-tools) and
  [frontend](/ai-engineering/harness/tools.md#frontend-tools)), [MCP](/ai-engineering/harness/mcp.md),
  [programmatic tool calling](/ai-engineering/harness/programmatic-tool-calling.md),
  [sandboxes](/ai-engineering/harness/sandboxes.md), [model routing](/ai-engineering/harness/model-routing.md),
  [the advisor tool](/ai-engineering/harness/advisor.md), [agents as tools](/ai-engineering/harness/agents-as-tools.md),
  [tool search](/ai-engineering/harness/tool-search.md) and
  [browser use](/ai-engineering/harness/llm-browser-use.md).
- **Multi-agent** — agents working with agents: [subagents](/ai-engineering/multi-agent/subagents.md),
  [dynamic subagents](/ai-engineering/multi-agent/dynamic-subagents.md),
  [peer agents](/ai-engineering/multi-agent/peer-agents.md) and the [A2A](/ai-engineering/multi-agent/a2a.md) protocol.
- **Compute** — what runs underneath: [AI compute](/ai-engineering/compute.md), from
  [performance regimes](/ai-engineering/compute/performance-regimes.md) and
  [SIMD/SIMT](/ai-engineering/compute/simd-simt.md) to [GPU sharing](/ai-engineering/compute/gpu-sharing.md), the
  [software stack](/ai-engineering/compute/software-stack.md) (CUDA, MLIR, [Mojo](/ai-engineering/compute/software-stack/mojo.md),
  [MAX](/ai-engineering/compute/software-stack/max.md)) and [LLM serving](/ai-engineering/compute/serving.md).
- **Development** — how software gets built with agents: the
  [AI-native SDLC](/ai-engineering/development/ai-native-sdlc.md),
  [observability-driven development](/ai-engineering/development/observability-driven-development.md),
  [verification and self-improvement](/ai-engineering/development/agent-self-improvement.md) and the
  [productivity evidence](/ai-engineering/development/ai-productivity-evidence.md).
- **Observability & evaluation** — tracing and evals with
  [LangSmith](/ai-engineering/observability.md#langsmith) (and its [evals](/ai-engineering/observability.md#langsmith-evals))
  and [Langfuse](/ai-engineering/observability.md#langfuse).
- **Platform** — the enterprise control plane: [AI gateways](/ai-engineering/platform/ai-gateways.md) for models
  and tools, and [guardrails and PII masking](/ai-engineering/platform/guardrails-and-masking.md).
- **Security** — [risks](/ai-engineering/security.md): the OWASP Agentic Top 10, contained by the platform's
  controls.

## Glossary

Short definitions of terms used across the AI engineering notes. A term moves back into its own concept when
it needs more than a definition.

### Agent

Agent is not a well-defined term, but in most cases it means an **LLM in a loop with tools**: the model picks
the next action, calls a [tool](/ai-engineering/harness/tools.md), observes the result, and repeats until the
task is done.[^langchain-agents] What distinguishes an agent from a fixed pipeline is that the *model*, not
hard-coded logic, directs the control flow; when the flow can be fixed instead, a fixed workflow is the leaner
option. The recurring ingredients are the loop, planning (decomposing a goal into steps), tool use,
[memory](/ai-engineering/context/context-engineering.md#memory) (carrying context across steps), and often
[subagents](/ai-engineering/multi-agent/subagents.md) for delegating focused subtasks. The loop is driven by an
[agent harness](/ai-engineering/harness.md); frameworks like [Deep Agents](/ai-engineering/harness.md#deep-agents)
package these patterns.

### Agent Client Protocol (ACP)

ACP standardizes communication between code editors or IDEs and coding agents.[^acp] Only useful for IDEs.

## Resources

For discovering new information:

- [Cognition blog](https://cognition.com/blog)
- [LangChain blog](https://www.langchain.com/blog)
- [Anthropic Engineering blog](https://www.anthropic.com/engineering)
- [FastMCP](https://gofastmcp.com)
- [LangChain's Max Agency podcast](https://www.youtube.com/playlist?list=PLfaIDFEXuae3UwB1QGEjsRAr8BzCQss7s)

Nice general resources:

- [The Agentic Operating Model — LangChain](https://www.langchain.com/resources/the-agentic-operating-model)

[^langchain-agents]: LangChain docs, "Agents".
[^acp]: agentclientprotocol.com.

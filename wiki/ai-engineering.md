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
- /ai-engineering/context/mcp.md
- /ai-engineering/context/okf.md
- /ai-engineering/context/rag.md
- /ai-engineering/context/context-engineering.md
- /ai-engineering/context/memory.md
- /ai-engineering/harness/tools.md
- /ai-engineering/harness/provider-tools.md
- /ai-engineering/harness/frontend-tools.md
- /ai-engineering/enterprise/llm-gateway.md
- /ai-engineering/enterprise/mcp-gateway.md
- /ai-engineering/agents/agent.md
- /ai-engineering/agents/peer-agents.md
- /ai-engineering/agents/deep-agents.md
- /ai-engineering/agents/claude-code.md
- /ai-engineering/agents/opencode.md
- /ai-engineering/agents/codex.md
- /ai-engineering/agents/devin.md
- /ai-engineering/agents/antigravity.md
- /ai-engineering/harness.md
- /ai-engineering/harness/subagents.md
- /ai-engineering/harness/workflows.md
- /ai-engineering/development/ai-native-sdlc.md
- /ai-engineering/development/observability-driven-development.md
- /ai-engineering/observability/langsmith.md
- /ai-engineering/observability/langfuse.md
- /ai-engineering/observability/langsmith-evals.md
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
generated:
  by: codex/gpt-6
  at: '2026-10-15T15:23:06+04:00'
topics:
- /ai-engineering/agents.md
- /ai-engineering/context.md
- /ai-engineering/development.md
- /ai-engineering/enterprise.md
- /ai-engineering/harness.md
- /ai-engineering/models.md
- /ai-engineering/observability.md
- /ai-engineering/providers.md
- /ai-engineering/security.md
---

## Map

- **Models** — [LLM architecture](/ai-engineering/models/llm-architecture.md): MoE sparsity,
  KV-cache-driven attention variants, and multimodal designs.
- **Decision models** — [Jev](/ai-engineering/models/jev.md) for typed System One decisions,
  and [CLM](/ai-engineering/models/clm.md) as an open-source alternative.
- **Context** — how the model gets its context: [MCP](/ai-engineering/context/mcp.md), the
  [Open Knowledge Format](/ai-engineering/context/okf.md), [RAG](/ai-engineering/context/rag.md),
  [context engineering](/ai-engineering/context/context-engineering.md), and
  [memory](/ai-engineering/context/memory.md).
- **Tools** — the [tools](/ai-engineering/harness/tools.md) primitive, plus
  [provider-side](/ai-engineering/harness/provider-tools.md) and [frontend](/ai-engineering/harness/frontend-tools.md) tools.
- **Enterprise** — the control plane: the [LLM Gateway](/ai-engineering/enterprise/llm-gateway.md)
  and the [MCP Gateway](/ai-engineering/enterprise/mcp-gateway.md).
- **Agents** — what an agent is ([agent architecture](/ai-engineering/agents/agent.md)) and the
  [peer-agent](/ai-engineering/agents/peer-agents.md) coordination model, plus the
  concrete ones: [deepagents](/ai-engineering/agents/deep-agents.md),
  [Claude Code](/ai-engineering/agents/claude-code.md), [opencode](/ai-engineering/agents/opencode.md),
  [Codex](/ai-engineering/agents/codex.md), [Devin](/ai-engineering/agents/devin.md), and
  [Antigravity](/ai-engineering/agents/antigravity.md).
- **Harness** — the machinery that runs them: the [harness](/ai-engineering/harness.md),
  [subagents](/ai-engineering/harness/subagents.md), and [workflows](/ai-engineering/harness/workflows.md).
- **Development** — how software gets built with agents: the
  [AI-native SDLC](/ai-engineering/development/ai-native-sdlc.md) and
  [observability-driven development](/ai-engineering/development/observability-driven-development.md).
- **Observability & evaluation** — tracing and evals with
  [LangSmith](/ai-engineering/observability/langsmith.md), [Langfuse](/ai-engineering/observability/langfuse.md),
  and [LangSmith Evals](/ai-engineering/observability/langsmith-evals.md).
- **Security** — [risks and mitigations](/ai-engineering/security.md): the OWASP Agentic
  Top 10 and the guardrails and masking that minimize them.

## Resources

For discovering new information:

- [Cognition blog](https://cognition.com/blog)
- [LangChain blog](https://www.langchain.com/blog)
- [Anthropic Engineering blog](https://www.anthropic.com/engineering)
- [FastMCP](https://gofastmcp.com)
- [LangChain's Max Agency podcast](https://www.youtube.com/playlist?list=PLfaIDFEXuae3UwB1QGEjsRAr8BzCQss7s)

Nice general resources:

- [The Agentic Operating Model — LangChain](https://www.langchain.com/resources/the-agentic-operating-model)

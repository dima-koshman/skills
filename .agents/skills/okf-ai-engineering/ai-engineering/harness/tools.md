---
type: Overview
title: Tools
description: The primitive that turns an LLM into an agent — functions the model can call to act on and read from its environment.
resource: https://docs.langchain.com/oss/python/deepagents/tools
---

Tools are the main thing needed to convert an LLM into a capable agent. Without
them, most agent actions would end after one turn; with them, agents can interact
with the environment, fetch new context to condition their output on, and perform
complex tasks. They are like control statements in programming languages.
Additionally, tools are generic and can be used for almost any use case — ranging
from direct actions like querying a database to meta operations like
[workflow](/harness/workflows.md) orchestration or recursive
[subagent](/harness/subagents.md) calling. Tools are exposed to models through
provider APIs and protocols like [MCP](/context/mcp.md).

# Where tools run

Tools for LLMs can be generally organized by where they execute:

- **Client-side tools** — executed by the client.
  - **Backend tools** — executed on the client's backend; the majority of tools
    fall into this category.
  - **[Frontend tools](/harness/frontend-tools.md)** — executed on the client's
    frontend, typically for UI interactions; a newer, less standardized category.
- **[Provider-side tools](/harness/provider-tools.md)** — defined and executed by the
  model provider (built-in web search, code execution, etc.); clients just enable
  them in API calls.

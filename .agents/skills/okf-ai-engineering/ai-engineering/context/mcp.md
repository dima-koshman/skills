---
type: Protocol
title: Model Context Protocol (MCP)
description: Open protocol standardizing how LLM apps expose and consume tools, resources, and prompts.
resource: https://modelcontextprotocol.io
tags: [mcp, protocol, platform, integration]
timestamp: 2026-07-04T00:00:00Z
---

MCP is a JSON-RPC-based protocol that standardizes the
boundary between an LLM client and external capabilities, mainly **tools** but also supports **resources** and **prompts**.

Its drawback is the stateful nature, but there is an initiative to make it stateless.

# Related

Consumed by [agent architectures](/agents/agent.md); secured and
multiplexed by an [LLM gateway](/enterprise/llm-gateway.md); distinct from
[OKF](/context/okf.md), which is static knowledge rather than live
tools.

# Resources

- [MCP specification](https://modelcontextprotocol.io)
- [FastMCP](https://gofastmcp.com)

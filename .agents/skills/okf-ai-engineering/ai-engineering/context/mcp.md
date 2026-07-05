---
type: Standard
title: Model Context Protocol (MCP)
description: Open protocol standardizing how LLM apps expose and consume tools, resources, and prompts.
resource: https://modelcontextprotocol.io
---

MCP is a JSON-RPC-based protocol that standardizes the boundary between an LLM
client and external capabilities — mainly **tools**, but it also supports
**resources** and **prompts**. Its [tools](/tools/tools.md) are consumed by
[agent architectures](/agents/agent.md) and, in production, fronted by an
[MCP gateway](/enterprise/mcp-gateway.md) that multiplexes and secures many
servers.

It was designed **stateful**: a session opens with an initialization handshake
that negotiates protocol version and capabilities once, over a persistent
connection the server can also push back on — sampling, elicitation, progress,
and resource/tool-list-change notifications. That bidirectional, session-oriented
model fit MCP's local-first origin, where a client launches a local server over
stdio and the connection is naturally long-lived.

That same statefulness is its main drawback for remote, at-scale deployments: the
handshake and per-session state force sticky sessions and complicate serverless
and horizontal scaling. A stateless-by-default redesign was requested in
[SEP-1442](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1442)
and accepted as
[SEP-2575](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2575)
(merged May 2026), targeting the 2026-07-28 spec revision — worth tracking as it
lands.

# Resources

- [MCP specification](https://modelcontextprotocol.io)
- [FastMCP](https://gofastmcp.com)
- [SEP-2575: Make MCP Stateless](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2575) (merged; targets the 2026-07-28 spec)

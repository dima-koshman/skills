---
type: Protocol
title: Model Context Protocol (MCP)
description: Open protocol standardizing how LLM apps expose and consume tools, resources, and prompts.
resource: https://modelcontextprotocol.io
tags: [mcp, protocol, platform, integration]
timestamp: 2026-07-04T00:00:00Z
---

MCP is a JSON-RPC-based protocol (over stdio or HTTP/SSE) that standardizes the
boundary between an LLM client and external capabilities: **tools** (callable
functions), **resources** (readable context), and **prompts** (templates). It
turns the N×M integration problem — every model against every system — into N+M.

## In an enterprise platform

MCP is the integration substrate for an enterprise AI platform. Standardizing on
it means any compliant client (Claude Desktop, Cursor, custom agents) reaches
internal systems through one contract, and new backends are added by composition
rather than bespoke glue. The gateway is where the protocol's neutrality meets
enterprise reality — auth, permissions, secrets, audit — see
[LLM gateway](/enterprise/llm-gateway.md).

## Design considerations

- **Transport** — stdio for local/desktop, streamable HTTP for multi-tenant
  services. HTTP is what a gateway needs.
- **Auth is underspecified for enterprise** — MCP's OAuth story assumes Dynamic
  Client Registration many enterprise IdPs lack; an OIDC-proxy pattern bridges
  the gap (as in [Bir MCP](https://gitlab.com/koshmandk/bir_mcp)).
- **Tool surface = attack surface** — exposed tools are a
  [prompt-injection](/security/threats/asi01-agent-goal-hijack.md) vector; gate them with
  per-user permissions and [guardrails](/security/controls/guardrails.md).
- **Framework** — FastMCP over the raw SDK for middleware, composition, and DX.

## Related

Consumed by [agent architectures](/agents/agent-architecture.md); secured and
multiplexed by an [LLM gateway](/enterprise/llm-gateway.md); distinct from
[OKF](/context/okf.md), which is static knowledge rather than live
tools.

# Citations

[1] [MCP specification](https://modelcontextprotocol.io)
[2] [FastMCP](https://gofastmcp.com)
[3] [Zero Trust for AI agents — Anthropic](https://claude.com/blog/zero-trust-for-ai-agents)

---
type: Technique
title: Peer Agents
description: Independently governed agents that own goals and coordinate as peers rather than through a permanent parent.
---

Peer agents are autonomous [agents](/agents/agent.md) that cooperate without one
permanently owning the others' goals, lifecycles, or authority. Unlike a
[parent with subagents](/harness/subagents.md), each peer can initiate work,
accept or reject requests, and continue operating independently.

# Control model

| Relationship | Goal and initiative | Authority |
|---|---|---|
| Parent–subagent | The parent delegates part of its goal | The parent controls the task and usually the subagent's lifecycle |
| Peer–peer | Either agent may initiate collaboration from its own goal | Neither agent can generally override or terminate the other |

The distinction is task-scoped rather than necessarily permanent. If agent A
delegates a bounded task to B, B acts as A's subagent for that task; in another
interaction B may delegate to A. They remain peers at the system level when
neither has standing authority over the other.

# Communication

Peer and subagent implementations often use the same machinery: an agent is
exposed as a callable endpoint or [tool](/harness/tools.md), messages carry task
context, and results arrive synchronously or asynchronously. Peers can also
coordinate indirectly through shared files, databases, repositories, queues, or
blackboards, provided ownership and concurrent updates are controlled.

[Agent2Agent](/agents/A2A.md) standardizes remote-agent discovery and the
exchange of messages, stateful tasks, status updates, and artifacts. It does not
make agents peers by itself: peerhood comes from independent goal and authority
ownership, not from the transport or message format.

# Reduction boundary

A central orchestrator can simulate the message trace of any finite peer
workflow, but making that orchestrator the agents' parent changes the
architecture when the agents are independently governed. For example, buyer
and supplier agents can negotiate while keeping their budgets, margins,
credentials, and approval policies private. Neither can command the other, and
an agreement requires both authorities to commit. A mediator may route their
messages, but it is not their parent.

# Design considerations

Peer coordination introduces distributed-systems concerns beyond ordinary
delegation: authenticated identities, task and ancestry IDs, idempotency,
concurrency control, distributed termination, and cycle detection when A calls
B and B calls A. Compromise or failure can propagate through
[inter-agent communication](/security/risks/insecure-inter-agent-communication.md)
and cause [cascading failures](/security/risks/cascading-agent-failures.md).

---
type: Standard
title: Agent2Agent
description: An protocol designed by Google enabling communication and interoperability between opaque agentic applications.
resource: https://a2a-protocol.org
---

A2A is a protocol for cross agent communication, a "REST API for agents". Though at the time or writing it has failed to gain traction on the open internet, mainly emerging inside enterprise platforms.

The ["Agents are not tools"](https://discuss.google.dev/t/agents-are-not-tools/) Google blog post argues that agents differ from tools in the way that they can handle imprecise, text formulated requests, and be a peer in the problem solving process, whereas tools are better suited for specific, well-defined tasks.

This [blog post](https://discuss.google.dev/t/a2a-protocol-demystifying-tasks-vs-messages/) compares the A2A protocol's Message and Task [data types](https://a2a-protocol.org/latest/specification/#4-protocol-data-model), which helps understand the problems the protocol was designed to solve.

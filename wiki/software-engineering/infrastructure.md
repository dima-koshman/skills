---
type: Knowledge Area
title: Infrastructure
description: "The layers around applications: service meshes, data, control and management planes, OS CPU scheduling, and network ports."
tags:
- software-engineering
- infrastructure
parent: /software-engineering.md
topics:
- /software-engineering/infrastructure/cpu-scheduling.md
- /software-engineering/infrastructure/network-ports.md
- /software-engineering/infrastructure/planes.md
- /software-engineering/infrastructure/service-mesh.md
status: draft
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-18T12:00:00+04:00'
---

## Topics

- [OS CPU Scheduling](/software-engineering/infrastructure/cpu-scheduling.md) — How an OS shares CPU time, through preemption, fair shares and priorities, and how weights differ from limits, using Linux as the example.
- [Well-Known Ports (22, 80, 443)](/software-engineering/infrastructure/network-ports.md) — Why ports 22, 80 and 443 matter beyond convention. Covers privileged ports, client defaults, browser port blocking, firewalls, and protocols that need a fixed port, plus what this means for a Runpod Pod.
- [Data, Control & Management Planes](/software-engineering/infrastructure/planes.md) — The decomposition of a distributed system into traffic-carrying, policy-distributing, and operator-facing layers.
- [Service Mesh](/software-engineering/infrastructure/service-mesh.md) — A dedicated infrastructure layer handling service-to-service routing, security, reliability, and observability outside application code.

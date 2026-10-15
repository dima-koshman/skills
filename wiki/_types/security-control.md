---
type: Concept Type
title: Security Control
description: A control applied around model or tool interactions.
primary_fields:
- parent
- mitigates
- related
generated:
  by: codex/gpt-6
  at: '2026-10-15T15:23:06+04:00'
---

# Security Control

A control applied around model or tool interactions.

## Attributes

| Field | Value | Meaning |
| --- | --- | --- |
| `parent` | concept path | The containing knowledge area; creates a labeled graph relationship. |
| `related` | concept paths | Related concepts linked by the original maintained note. |
| `mitigates` | concept paths | Risks explicitly addressed by a control in the source note. |
| `control_surface` | strings | The data or action boundaries at which a control applies. |

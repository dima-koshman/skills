---
type: Concept Type
title: Concept
description: A conceptual explanation of an agent or software-system mechanism.
primary_fields:
- parent
- uses
- related
generated:
  by: codex/gpt-6
  at: '2026-10-15T15:23:06+04:00'
---

# Concept

A conceptual explanation of an agent or software-system mechanism.

## Attributes

| Field | Value | Meaning |
| --- | --- | --- |
| `parent` | concept path | The containing knowledge area; creates a labeled graph relationship. |
| `related` | concept paths | Related concepts linked by the original maintained note. |
| `uses` | concept path | A format or architectural concept used by this concept. |
| `note_date` | date string | The original note snapshot date; converting to OKF is not factual re-verification. |
| `plane` | string | The architectural plane described in the source note. |
| `policy_surface` | string | The requests governed by a gateway. |
| `implementation_example` | string | An implementation named in the existing note. |
| `data_plane_modes` | strings | Data-plane deployment modes named in the source note. |

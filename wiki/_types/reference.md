---
type: Concept Type
title: Reference
description: A reading note, resource collection, or learning resource.
primary_fields:
- parent
- related
generated:
  by: codex/gpt-6
  at: '2026-10-15T15:23:06+04:00'
---

# Reference

A reading note, resource collection, or learning resource.

## Attributes

| Field | Value | Meaning |
| --- | --- | --- |
| `parent` | concept path | The containing knowledge area; creates a labeled graph relationship. |
| `related` | concept paths | Related concepts linked by the original maintained note. |
| `note_date` | date string | The original note snapshot date; converting to OKF is not factual re-verification. |
| `publication` | string | Publication and edition context retained from the source reading note. |

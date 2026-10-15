---
type: Concept Type
title: Decision Model
description: A model that scores supplied actions or returns typed decisions.
primary_fields:
- parent
- related
generated:
  by: codex/gpt-6
  at: '2026-10-15T15:23:06+04:00'
---

# Decision Model

A model that scores supplied actions or returns typed decisions.

## Attributes

| Field | Value | Meaning |
| --- | --- | --- |
| `parent` | concept path | The containing knowledge area; creates a labeled graph relationship. |
| `related` | concept paths | Related concepts linked by the original maintained note. |
| `decision_interface` | strings | Typed question primitives or ranking operations in the note. |
| `serving_model` | string | Hosted or self-hosted serving described by the source. |
| `encoder` | string | The encoder identified by the source note. |
| `api_routes` | strings | HTTP routes documented by the source note, not concept links. |
| `note_date` | date string | The original note snapshot date; converting to OKF is not factual re-verification. |

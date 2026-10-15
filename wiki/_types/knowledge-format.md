---
type: Concept Type
title: Knowledge Format
description: A format for expressing knowledge or structured data.
primary_fields:
- parent
- related
generated:
  by: codex/gpt-6
  at: '2026-10-15T15:23:06+04:00'
---

# Knowledge Format

A format for expressing knowledge or structured data.

## Attributes

| Field | Value | Meaning |
| --- | --- | --- |
| `parent` | concept path | The containing knowledge area; creates a labeled graph relationship. |
| `related` | concept paths | Related concepts linked by the original maintained note. |
| `schema_language` | string | The schema language used to describe the format. |
| `encoding` | string | The representation described by the format note. |
| `format_version` | string | The specification version used by the maintained local bundle. |
| `concept_encoding` | string | The file encoding convention for a knowledge concept. |
| `note_date` | date string | The original note snapshot date; converting to OKF is not factual re-verification. |

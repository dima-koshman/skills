---
type: Concept Type
title: Tool
description: A concrete agent, framework, library, or platform described in the maintained notes.
primary_fields:
- parent
- implements
- related
generated:
  by: codex/gpt-6
  at: '2026-10-15T15:23:06+04:00'
---

# Tool

A concrete agent, framework, library, or platform described in the maintained notes.

## Attributes

| Field | Value | Meaning |
| --- | --- | --- |
| `parent` | concept path | The containing knowledge area; creates a labeled graph relationship. |
| `related` | concept paths | Related concepts linked by the original maintained note. |
| `implements` | concept path | The architecture implemented by a concrete tool. |
| `provider` | concept path | The model provider used by a concrete agent implementation. |
| `execution_surface` | strings | Interfaces or execution environments named in the source note. |
| `provider_model` | string | Whether the tool is tied to a particular model provider. |
| `runtime_framework` | string | The runtime framework identified in the source note. |
| `note_date` | date string | The original note snapshot date; converting to OKF is not factual re-verification. |
| `input_bundle` | repository path | The maintained source OKF directory in this repository. |
| `output_bundle` | repository path | The separately generated OpenWiki OKF directory. |
| `role` | string | The intended local role of the tool in the maintained workflow. |

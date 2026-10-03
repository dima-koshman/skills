# Context Engineering

Deliberately assembling what goes into the model's context window — instructions, tools, retrieved data, memory, and history.

Reference: <https://docs.langchain.com/oss/python/deepagents/context-engineering>

Context engineering is the practice of deliberately assembling everything the
model sees for a given step — system instructions, [tool](../harness/tools.md)
definitions, [retrieved](rag.md) data, [memory](memory.md), and
conversation history — and managing the limited context window. It is the broader
successor discipline to prompt engineering.

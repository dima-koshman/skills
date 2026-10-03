# Langfuse

Open-source LLM observability and tracing, OpenTelemetry-friendly.

Reference: <https://langfuse.com>

Langfuse is an open-source LLM observability platform — self-hostable tracing, metrics, and evals, a vendor-neutral alternative to [LangSmith](langsmith.md) on the same OTel backbone.

Its LLM-as-a-judge evaluators can run online. They score incoming production observations that match filter rules and write the scores with reasoning back onto the traces, which makes them a continuous quality signal for agents to act on (see [toil](../../software-engineering/reliability/toil.md#agents-as-toil-automation)).

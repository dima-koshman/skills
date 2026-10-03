# LangSmith

LangChain's tracing and evaluation platform for LLM/agent observability.

Reference: <https://www.langchain.com/langsmith>

LangSmith is LangChain's managed platform for tracing, monitoring, and [evaluating](langsmith-evals.md) LLM apps and agents — the observability backend used across this work. [Langfuse](langfuse.md) is the open-source alternative.

[LangSmith Engine](https://docs.langchain.com/langsmith/engine-overview) is its in-product agent. It scans tracing projects on a schedule, groups recurring failures into issues, diagnoses them against connected source code, and proposes fixes as pull requests. See [toil](../../software-engineering/reliability/toil.md#agents-as-toil-automation) for where this fits.

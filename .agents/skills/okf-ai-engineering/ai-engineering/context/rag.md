---
type: Technique
title: RAG
description: Retrieval-augmented generation — fetching relevant documents at query time and adding them to the model's context.
---

While strictly speaking retrieval-augmented generation doesn't have to be based on vector embeddings and semantic similarity search, in practice that's what is usually implied when people mention RAG. Powerful technique, but doesn't suit all use cases - doesn't work well for structured or semi-structured data or data that changes frequently - embeddings are not directly linked to original text and require re-indexing. Additionally, it requires a lot of maintenance and complex setup - need to normalize text, deal with structured data, chunking, etc.

RAG is one of the techniques used in
[context engineering](/context/context-engineering.md).

Some discussions about RAG highlighting the need for custom approaches and complex data engineering pipelines, as well as retrieval techniques:

- > [retrieval is not a vector store](https://www.reddit.com/r/Rag/s/KDBqvK7pMb)

- > [metadata is everything](https://www.reddit.com/r/Rag/comments/1m890yk/i_made_60k_building_rag_projects_in_3_months/)

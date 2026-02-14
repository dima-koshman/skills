from datetime import UTC, datetime

import langchain_core.documents
import langchain_core.embeddings
import langchain_core.vectorstores
import langchain_text_splitters


class DirectoryStore:
    """
    Class for embedding an abstract directory files into a LangChain vector store.

    Backend-agnostic — works with any LangChain-compatible vector stores or embeddings.
    """

    def __init__(
        self,
        vector_store: langchain_core.vectorstores.VectorStore,
        embeddings: langchain_core.embeddings.Embeddings,
    ):
        self.vector_store = vector_store
        self.embeddings = embeddings
        self._markdown_splitter = langchain_text_splitters.MarkdownTextSplitter()
        self._recursive_splitter = langchain_text_splitters.RecursiveCharacterTextSplitter()

    async def delete_file(self, file_path: str):
        """Delete all documents in store for the given file path."""
        docs = self.vector_store.similarity_search("", k=10000, filter={"file_path": file_path})
        ids = [doc.id for doc in docs if doc.id]
        if ids:
            await self.vector_store.adelete(ids)

    async def embed_file(self, file_path: str, content: str, metadata: dict | None):
        await self.delete_file(file_path)

        if file_path.endswith(".md"):
            splitter = self._markdown_splitter
        else:
            splitter = self._recursive_splitter

        chunks = splitter.split_text(content)
        base_metadata = {"file_path": file_path, "created_at": datetime.now(UTC).isoformat()}
        if metadata:
            base_metadata.update(metadata)

        documents = [
            langchain_core.documents.Document(page_content=chunk, metadata=base_metadata.copy())
            for chunk in chunks
        ]
        await self.vector_store.aadd_documents(documents)

    async def search_documents(self, query: str) -> list[langchain_core.documents.Document]:
        return await self.vector_store.asimilarity_search(query)

    async def search_files(self, query: str) -> list[str]:
        docs = await self.search_documents(query)
        seen: set[str] = set()
        paths: list[str] = []
        for doc in docs:
            path = doc.metadata["file_path"]
            if path not in seen:
                seen.add(path)
                paths.append(path)
        return paths

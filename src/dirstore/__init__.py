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

    def embed_file(self, file_path: str, content: str, metadata: dict | None):
        # First, delete the existing documents in store for this file path.
        # Then split the file content into chunks, embed and store resulting documents with
        # metadata + file_path, creation time
        ...

    def search_documents(self, query: str):
        # Search the vector store for documents matching the query.
        ...

    def search_files(self, query: str) -> list[str]:
        # Search the vector store for files matching the query, returning unique file paths.
        ...

"""Tests for the DirectoryStore class."""

import uuid

import pytest

import langchain_core.documents
import langchain_core.embeddings
import langchain_core.vectorstores


class FakeEmbeddings(langchain_core.embeddings.Embeddings):
    """Fake embeddings for testing -- returns deterministic dummy vectors."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[0.1, 0.2, 0.3] for _ in texts]

    def embed_query(self, text: str) -> list[float]:
        return [0.1, 0.2, 0.3]


class FakeVectorStore(langchain_core.vectorstores.VectorStore):
    """
    In-memory fake vector store for testing.

    Stores documents in a dict keyed by generated ID. Supports filtering
    by metadata in similarity_search.
    """

    def __init__(self):
        self._docs: dict[str, langchain_core.documents.Document] = {}
        self._embeddings = FakeEmbeddings()

    @property
    def embeddings(self) -> FakeEmbeddings:
        return self._embeddings

    def add_documents(
        self,
        documents: list[langchain_core.documents.Document],
        **kwargs,
    ) -> list[str]:
        ids = []
        for doc in documents:
            doc_id = doc.id or str(uuid.uuid4())
            doc.id = doc_id
            self._docs[doc_id] = doc
            ids.append(doc_id)
        return ids

    def delete(self, ids: list[str] | None = None, **kwargs) -> None:
        if ids is None:
            return
        for doc_id in ids:
            self._docs.pop(doc_id, None)

    def similarity_search(
        self,
        query: str,
        k: int = 4,
        **kwargs,
    ) -> list[langchain_core.documents.Document]:
        filter_dict = kwargs.get("filter")
        results = []
        for doc in self._docs.values():
            if filter_dict:
                if all(doc.metadata.get(key) == val for key, val in filter_dict.items()):
                    results.append(doc)
            else:
                results.append(doc)
        return results[:k]

    @classmethod
    def from_texts(
        cls,
        texts: list[str],
        embedding: langchain_core.embeddings.Embeddings,
        metadatas: list[dict] | None = None,
        **kwargs,
    ) -> "FakeVectorStore":
        raise NotImplementedError("Use add_documents instead")


# -- Tests ---------------------------------------------------------------

from dirstore import DirectoryStore


def test_constructor():
    vs = FakeVectorStore()
    emb = FakeEmbeddings()
    store = DirectoryStore(vs, emb)
    assert store.vector_store is vs
    assert store.embeddings is emb


@pytest.mark.asyncio
async def test_delete_file_removes_documents():
    vs = FakeVectorStore()
    store = DirectoryStore(vs, FakeEmbeddings())

    # Manually add docs to simulate embedded state
    vs.add_documents([
        langchain_core.documents.Document(page_content="a", metadata={"file_path": "x.txt"}),
        langchain_core.documents.Document(page_content="b", metadata={"file_path": "y.txt"}),
    ])
    assert len(vs._docs) == 2

    await store.delete_file("x.txt")

    assert len(vs._docs) == 1
    assert list(vs._docs.values())[0].metadata["file_path"] == "y.txt"


@pytest.mark.asyncio
async def test_delete_file_noop_for_missing_path():
    vs = FakeVectorStore()
    store = DirectoryStore(vs, FakeEmbeddings())

    await store.delete_file("nonexistent.txt")  # should not raise


@pytest.mark.asyncio
async def test_embed_file_stores_documents_with_metadata():
    vs = FakeVectorStore()
    store = DirectoryStore(vs, FakeEmbeddings())

    await store.embed_file("docs/readme.md", "# Hello\n\nWorld", {"author": "test"})

    assert len(vs._docs) > 0
    for doc in vs._docs.values():
        assert doc.metadata["file_path"] == "docs/readme.md"
        assert doc.metadata["author"] == "test"
        assert "created_at" in doc.metadata


@pytest.mark.asyncio
async def test_embed_file_uses_markdown_splitter_for_md():
    vs = FakeVectorStore()
    store = DirectoryStore(vs, FakeEmbeddings())

    content = ("# Section 1\n\n" + "Word " * 1000 + "\n\n# Section 2\n\n" + "Word " * 1000)
    await store.embed_file("file.md", content, None)

    texts = [doc.page_content for doc in vs._docs.values()]
    assert len(texts) >= 2


@pytest.mark.asyncio
async def test_embed_file_uses_recursive_splitter_for_non_md():
    vs = FakeVectorStore()
    store = DirectoryStore(vs, FakeEmbeddings())

    await store.embed_file("file.txt", "Hello world", None)

    assert len(vs._docs) == 1
    assert list(vs._docs.values())[0].page_content == "Hello world"


@pytest.mark.asyncio
async def test_embed_file_re_embeds_on_second_call():
    vs = FakeVectorStore()
    store = DirectoryStore(vs, FakeEmbeddings())

    await store.embed_file("file.txt", "version 1", None)
    await store.embed_file("file.txt", "version 2", None)

    docs = list(vs._docs.values())
    assert len(docs) == 1
    assert docs[0].page_content == "version 2"

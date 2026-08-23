from pathlib import Path

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)
from langchain_community.vectorstores import Chroma

from knowledge.document_loader import (
    KnowledgeDocumentLoader,
)

from knowledge.embedder import (
    KnowledgeEmbedder,
)


class KnowledgeRetriever:

    def __init__(
        self,
        documents_dir="knowledge/documents",
        persist_directory="knowledge/vector_store",
    ):

        self.documents_dir = Path(
            documents_dir
        )

        self.persist_directory = (
            persist_directory
        )

        self.loader = KnowledgeDocumentLoader(
            documents_dir
        )

        self.embedder = KnowledgeEmbedder()

    def build(self):

        documents = self.loader.load()

        if not documents:

            raise ValueError(
                "No knowledge documents found."
            )

        splitter = (
            RecursiveCharacterTextSplitter(
                chunk_size=800,
                chunk_overlap=120,
            )
        )

        chunks = splitter.split_documents(
            documents
        )

        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=self.embedder.get_embeddings(),
            persist_directory=self.persist_directory,
        )

        return vector_store

    def retrieve(
        self,
        query: str,
        k: int = 4,
    ):

        vector_store = self.build()

        return vector_store.similarity_search(
            query,
            k=k,
        )
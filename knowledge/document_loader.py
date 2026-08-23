from pathlib import Path

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
)


class KnowledgeDocumentLoader:

    def __init__(self, documents_dir="knowledge/documents"):
        self.documents_dir = Path(documents_dir)

    def load(self):

        documents = []

        for file_path in self.documents_dir.rglob("*"):

            if not file_path.is_file():
                continue

            suffix = file_path.suffix.lower()

            try:

                if suffix == ".pdf":

                    loader = PyPDFLoader(
                        str(file_path)
                    )

                    documents.extend(
                        loader.load()
                    )

                elif suffix in [".txt", ".md"]:

                    loader = TextLoader(
                        str(file_path),
                        encoding="utf-8",
                    )

                    documents.extend(
                        loader.load()
                    )

            except Exception as exc:

                print(
                    f"Failed to load {file_path}: {exc}"
                )

        return documents
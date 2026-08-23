import os

from langchain_google_genai import GoogleGenerativeAIEmbeddings


class KnowledgeEmbedder:
    def __init__(self, model="gemini-embedding-001"):

        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY or GOOGLE_API_KEY is not set."
            )

        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=model,
            google_api_key=api_key,
        )

    def get_embeddings(self):
        return self.embeddings
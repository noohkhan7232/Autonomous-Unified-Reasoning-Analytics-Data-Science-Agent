def __init__(self, model: str = "gemini-3.6-flash"):
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "Google Gemini API key not found. "
            "Set GOOGLE_API_KEY or GEMINI_API_KEY."
        )

    self.llm = ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=0.3,
    )

    self.retriever = KnowledgeRetriever()
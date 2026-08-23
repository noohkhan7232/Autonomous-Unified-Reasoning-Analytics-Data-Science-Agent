from langchain_google_genai import ChatGoogleGenerativeAI


class KnowledgeAgent:

    def __init__(
        self,
        model="gemini-3.6-flash",
    ):

        self.llm = ChatGoogleGenerativeAI(
            model=model,
            temperature=0,
        )

    def generate_grounded_explanation(
        self,
        question: str,
        context: str,
    ):

        prompt = f"""
You are the knowledge-grounding agent
inside AURA-DS.

Answer the question using ONLY the
provided knowledge context.

Question:
{question}

Knowledge Context:
{context}

Requirements:

1. Do not invent facts.
2. Clearly explain the reasoning.
3. If the context is insufficient, say so.
4. Keep the explanation concise and technical.
"""

        response = self.llm.invoke(prompt)

        return response.content
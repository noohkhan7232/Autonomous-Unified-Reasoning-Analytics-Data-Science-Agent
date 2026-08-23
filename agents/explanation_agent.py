import os

from typing import Dict
import json

from langchain_google_genai import ChatGoogleGenerativeAI

from knowledge.retriever import KnowledgeRetriever


class ExplanationAgent:
    """
    RAG-powered Explanation Agent of AURA-DS.

    Uses:
    - Structured analytics results
    - Retrieved domain knowledge
    - Google Gemini

    to generate a professional analytical report.
    """

    def __init__(self, model="gemini-3.6-flash"):

        api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY is not configured."
            )

        self.llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            temperature=0,
        )

        # Initialize knowledge retriever
        self.retriever = KnowledgeRetriever()

    def run(
        self,
        eda_summary: Dict,
        model_metrics: Dict,
        task_type: str,
        target_column: str,
    ) -> str:

        # ---------------------------------------------------------
        # 1. Build a knowledge query from the current analysis
        # ---------------------------------------------------------

        knowledge_query = self._build_knowledge_query(
            task_type=task_type,
            model_metrics=model_metrics,
        )

        # ---------------------------------------------------------
        # 2. Retrieve relevant domain knowledge
        # ---------------------------------------------------------

        retrieved_docs = self.retriever.retrieve(
            knowledge_query
        )

        knowledge_context = self._format_retrieved_knowledge(
            retrieved_docs
        )

        # ---------------------------------------------------------
        # 3. Build RAG-enhanced prompt
        # ---------------------------------------------------------

        prompt = self._build_prompt(
            eda_summary=eda_summary,
            model_metrics=model_metrics,
            task_type=task_type,
            target_column=target_column,
            knowledge_context=knowledge_context,
        )

        # ---------------------------------------------------------
        # 4. Generate final explanation
        # ---------------------------------------------------------

        response = self.llm.invoke(prompt)

        return response.content

    def _build_knowledge_query(
        self,
        task_type: str,
        model_metrics: Dict,
    ) -> str:
        """
        Creates a focused query for the knowledge retriever.
        """

        metrics = ", ".join(
            f"{key}: {value}"
            for key, value in model_metrics.items()
        )

        return (
            f"Machine learning {task_type} evaluation. "
            f"Explain the meaning and interpretation of these "
            f"model metrics: {metrics}. "
            f"Provide relevant guidance for interpreting "
            f"model performance."
        )

    def _format_retrieved_knowledge(
        self,
        retrieved_docs,
    ) -> str:
        """
        Converts retrieved documents into prompt-ready context.
        """

        if not retrieved_docs:
            return "No relevant knowledge was retrieved."

        context_parts = []

        for index, doc in enumerate(retrieved_docs, start=1):

            content = getattr(
                doc,
                "page_content",
                str(doc),
            )

            context_parts.append(
                f"[Knowledge Source {index}]\n{content}"
            )

        return "\n\n".join(context_parts)

    def _build_prompt(
        self,
        eda_summary: Dict,
        model_metrics: Dict,
        task_type: str,
        target_column: str,
        knowledge_context: str,
    ) -> str:

        return f"""
You are the Explanation Agent of AURA-DS,
an autonomous data science and analytics system.

You are given the results of an autonomous data analysis
pipeline together with relevant machine learning knowledge
retrieved from the AURA-DS knowledge base.

Task type:
{task_type}

Target variable:
{target_column}

==================================================
EXPLORATORY DATA ANALYSIS
==================================================

{json.dumps(eda_summary, indent=2)}

==================================================
MODEL EVALUATION
==================================================

{json.dumps(model_metrics, indent=2)}

==================================================
RETRIEVED KNOWLEDGE
==================================================

{knowledge_context}

==================================================
INSTRUCTIONS
==================================================

Use the retrieved knowledge as supporting context when
explaining the model metrics and analytical findings.

Write a concise, professional analytical report covering:

1. Key characteristics of the dataset
2. Important data quality issues
3. Model performance
4. Meaning of the evaluation metrics
5. Important patterns or findings
6. Practical implications of the results

IMPORTANT RULES:

- Do not invent facts.
- Do not invent dataset characteristics.
- Do not invent model metrics.
- Base dataset-specific claims strictly on the supplied
  analysis results.
- Use retrieved knowledge only to explain concepts,
  metrics, and analytical interpretation.
- Clearly distinguish between observed results and
  general machine learning knowledge.
- Keep the report professional and concise.

The final response should read like an intelligent
machine learning analysis report generated by AURA-DS.
"""
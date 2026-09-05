import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.services.ai_context import context_to_text


load_dotenv()


def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not configured. "
            "Add it to backend/.env"
        )

    return genai.Client(api_key=api_key)


def ask_dataset_ai(dataset_id: str, question: str):
    """
    Ask Gemini a question about a specific dataset.
    """

    dataset_context = context_to_text(dataset_id)

    system_instruction = """
You are DataPilot AI, an intelligent data analysis assistant.

Your job is to help users understand and analyze their uploaded dataset.

Important rules:

1. Answer primarily using the dataset context provided.
2. Do not invent dataset values or statistics.
3. If the available context is insufficient, clearly say so.
4. Explain insights clearly and professionally.
5. Use simple language unless the user asks for advanced analysis.
6. When discussing statistics, mention relevant column names.
7. Identify possible missing data, duplicates, outliers, correlations,
   trends, and patterns when relevant.
8. Do not claim to have calculated values that are not present
   in the dataset context.
9. Keep answers reasonably concise but useful.
10. You are a data analysis assistant, not a general-purpose chatbot.
"""

    prompt = f"""
DATASET CONTEXT:

{dataset_context}

USER QUESTION:

{question}

Analyze the dataset and answer the user's question.
"""

    client = get_gemini_client()

    response = client.models.generate_content(
        model="gemini-3.7-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.2,
            max_output_tokens=1200,
        ),
    )

    answer = response.text

    if not answer:
        answer = (
            "I could not generate a response for this "
            "dataset question."
        )

    return answer

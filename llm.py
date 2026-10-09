from google import genai
import streamlit as st
import time


def generate_answer(query, retrieved_chunks):

    # --------------------------------------------------
    # NO RETRIEVED INFORMATION
    # --------------------------------------------------

    if not retrieved_chunks:
        return (
            "I couldn't find relevant information "
            "in your uploaded documents."
        )

    # --------------------------------------------------
    # BUILD CONTEXT
    # --------------------------------------------------

    context_parts = []

    for i, result in enumerate(retrieved_chunks, start=1):

        context_parts.append(
            f"""
SOURCE {i}
Similarity score: {result['score']:.3f}

{result['chunk']}
"""
        )

    context = "\n".join(context_parts)

    # --------------------------------------------------
    # PROMPT
    # --------------------------------------------------

    prompt = f"""
You are ASTRA, a RAG-based document assistant.

Answer the user's question using ONLY the information
contained in the retrieved document context below.

RULES:

1. Do not use outside knowledge.
2. Do not invent facts.
3. If the answer is not present in the context, say:
   "I couldn't find that information in the uploaded documents."
4. Give a clear and direct answer.
5. Use short bullet points when useful.
6. Do not repeat the entire context.
7. Answer only what the user asked.

USER QUESTION:
{query}

RETRIEVED DOCUMENT CONTEXT:
{context}

Now answer the user's question.
"""

    # --------------------------------------------------
    # API KEY
    # --------------------------------------------------

    api_key = st.secrets.get("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not configured."
        )

    # --------------------------------------------------
    # GEMINI CLIENT
    # --------------------------------------------------

    client = genai.Client(
        api_key=api_key
    )

    # --------------------------------------------------
    # MODEL RETRY / FALLBACK
    # --------------------------------------------------

    models = [
        "gemini-3.8-flash",
        "gemini-3.5-flash-lite"
    ]

    last_error = None

    for model_name in models:

        for attempt in range(2):

            try:

                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )

                if response.text:
                    return response.text.strip()

            except Exception as error:

                last_error = error

                print(
                    f"ASTRA Gemini error | "
                    f"Model: {model_name} | "
                    f"Type: {type(error).__name__} | "
                    f"Details: {error}",
                    flush=True
                )

                if attempt == 0:
                    time.sleep(2)

    # --------------------------------------------------
    # FRIENDLY FAILURE
    # --------------------------------------------------

    return (
        "ASTRA couldn't generate an answer right now "
        "because the AI service is temporarily unavailable. "
        "Your documents and retrieval system are working; "
        "please try again shortly."
    )
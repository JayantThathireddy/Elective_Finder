"""
generate.py — Generate grounded answers using Groq LLM + retrieved chunks.

The system prompt strictly confines the model to the retrieved context.
Source attribution is both requested in the prompt and appended programmatically.

Can be run standalone to test end-to-end:
    python generate.py
"""

import os
from groq import Groq
from dotenv import load_dotenv
from retrieve import retrieve

load_dotenv()

GROQ_MODEL = "llama-3.3-70b-versatile"
DEFAULT_TOP_K = 8

SYSTEM_PROMPT = """\
You are a helpful assistant for UNC Charlotte (UNCC) students who want honest,
student-sourced advice about elective courses and professors.

You will be given excerpts from real student discussions on r/UNCCharlotte.
Answer the user's question using ONLY the information in those excerpts.
Do NOT draw on your own general knowledge about universities or courses.

Rules:
1. If the excerpts contain enough information, answer directly and specifically.
2. If the excerpts do NOT contain enough information to answer, say exactly:
   "I don't have enough information in the available student discussions to answer that."
3. Never speculate or guess beyond what is in the excerpts.
4. End your response with: "Sources:" followed by the post titles you used.
"""

_client: Groq | None = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError("GROQ_API_KEY not set in .env")
        _client = Groq(api_key=api_key)
    return _client


def ask(question: str, k: int = DEFAULT_TOP_K) -> dict:
    """
    Retrieve relevant chunks and generate a grounded answer.

    Returns:
        answer  — LLM response text (includes inline source citations)
        sources — list of unique Reddit thread URLs retrieved
        chunks  — raw retrieved chunk dicts (for debugging/evaluation)
    """
    chunks = retrieve(question, k=k)

    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(
            f'[Excerpt {i} — from post: "{chunk["title"]}"]\n{chunk["text"]}'
        )
    context = "\n\n".join(context_parts)

    user_message = (
        f"Student discussions retrieved:\n\n{context}\n\n"
        f"Student question: {question}"
    )

    client = _get_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.3,
        max_tokens=900,
    )

    answer = response.choices[0].message.content
    unique_sources = list(dict.fromkeys(c["source"] for c in chunks))

    return {
        "answer": answer,
        "sources": unique_sources,
        "chunks": chunks,
    }


if __name__ == "__main__":
    questions = [
        "What UNCC courses do students recommend as easy electives?",
        "What is the meaning of life?",  # out-of-scope test
    ]
    for q in questions:
        print(f"\nQ: {q}")
        result = ask(q)
        print(f"A: {result['answer'][:600]}")
        print("Sources:")
        for s in result["sources"]:
            print(f"  - {s}")
        print()

"""
LONG-TERM MEMORY
----------------
Stores durable facts and preferences about a user in a separate Pinecone namespace.
Each record: dense vector + metadata {user_id, text}.
Kept apart from document chunks (namespace "user_memory").
"""

import hashlib
import json
import math

from google.genai import types
from ML.utils import generate_embeddings

MEMORY_NAMESPACE = "user_memory"
EXTRACT_MODEL = "gemini-3.5-flash-lite"
TOP_K = 3
MIN_SCORE = 0.35  # cosine-like score; tune by testing real questions

EXTRACT_PROMPT = """You maintain long-term memory about a user of a document Q&A app.
From the exchange below, extract ONLY durable facts about the user or their preferences
(role, studies, projects, goals, preferred answer style).
Do NOT extract facts from the documents, one-off questions, or temporary details.
Return ONLY a JSON array of short sentences about the user, for example:
["The user is a 3rd-year computer science student.", "The user prefers short bullet-point answers."]
Return [] if nothing is worth remembering.

QUESTION: {question}
ANSWER: {answer}
"""


def _normalize(vec):
    """Unit length, so dot product == cosine similarity (same as documents)."""
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def _record_id(user_id, text):
    """Same fact for the same user always gets the same ID, so no duplicates."""
    digest = hashlib.sha1(text.lower().encode("utf-8")).hexdigest()[:16]
    return f"{user_id}::{digest}"


def recall(index, user_id, question):
    """Return memories relevant to this question for this user."""
    vectors = generate_embeddings([question], task_type="RETRIEVAL_QUERY")
    if not vectors:
        return []
    res = index.query(
        vector=_normalize(vectors[0]),
        top_k=TOP_K,
        include_metadata=True,
        namespace=MEMORY_NAMESPACE,
        filter={"user_id": {"$eq": user_id}},
    )
    return [m.metadata["text"] for m in res.matches if m.score >= MIN_SCORE]


def save(index, client, user_id, question, answer_text):
    """Ask Gemini what is worth remembering from this exchange, then store it."""
    response = client.models.generate_content(
        model=EXTRACT_MODEL,
        contents=EXTRACT_PROMPT.format(question=question, answer=answer_text),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0,
        ),
    )
    try:
        data = json.loads(response.text)
    except json.JSONDecodeError:
        return 0
    if not isinstance(data, list):
        return 0

    facts = [f.strip() for f in data if isinstance(f, str) and f.strip()]
    if not facts:
        return 0

    vectors = generate_embeddings(facts)  # RETRIEVAL_DOCUMENT, same as chunks
    if len(vectors) != len(facts):
        return 0

    records = [
        {
            "id": _record_id(user_id, text),
            "values": _normalize(vec),
            "metadata": {"user_id": user_id, "text": text},
        }
        for text, vec in zip(facts, vectors)
    ]
    index.upsert(vectors=records, namespace=MEMORY_NAMESPACE)
    return len(records)


def list_memories(index, user_id):
    """All stored memories for one user (used by the GET endpoint)."""
    ids = []
    for page in index.list(prefix=f"{user_id}::", namespace=MEMORY_NAMESPACE):
        ids.extend(page)
    if not ids:
        return []
    fetched = index.fetch(ids=ids, namespace=MEMORY_NAMESPACE)
    return [v.metadata["text"] for v in fetched.vectors.values()]


def delete_memories(index, user_id):
    """Forget everything about one user (used by the DELETE endpoint)."""
    ids = []
    for page in index.list(prefix=f"{user_id}::", namespace=MEMORY_NAMESPACE):
        ids.extend(page)
    if ids:
        index.delete(ids=ids, namespace=MEMORY_NAMESPACE)
    return len(ids)
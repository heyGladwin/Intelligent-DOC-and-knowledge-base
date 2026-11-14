"""
SHARED RETRIEVAL PIPELINE (framework-agnostic, no graph)
--------------------------------------------------------
  1. DENSE search   (Gemini embedding, meaning)        -> top N chunks
  2. SPARSE search  (Pinecone sparse model, keywords)  -> top N chunks
  3. RRF fusion     (merge both rankings by rank position)
  4. RERANK         (bge-reranker-v2-m3 cross-encoder) -> best top_n chunks
  5. GENERATE       (Gemini answers from those chunks only)
"""

import os
import math
from pinecone import Pinecone, ServerlessSpec
from google import genai

from ML.utils import generate_embeddings

# ---------------- CONFIG ----------------
INDEX_NAME = os.getenv("PINECONE_INDEX", "intelligent-doc-hybrid")
NAMESPACE = "knowledge_base"
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "3072"))

SPARSE_MODEL = "pinecone-sparse-english-v0"
RERANK_MODEL = "bge-reranker-v2-m3"
ANSWER_MODEL = "gemini-2.5-flash"

CANDIDATES_PER_SEARCH = 20  # chunks returned by each search, input to RRF
RRF_K = 60                  # standard RRF smoothing constant
RERANK_INPUT = 20           # fused candidates sent to the reranker
FINAL_TOP_N = 5             # chunks sent to Gemini
# ----------------------------------------

# ---------------- CLIENTS ----------------
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
llm = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

if not pc.has_index(INDEX_NAME):
    pc.create_index(
        name=INDEX_NAME,
        dimension=EMBEDDING_DIM,
        metric="dotproduct",  # required for hybrid (dense + sparse in one index)
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )

index = pc.Index(INDEX_NAME)
# -----------------------------------------


# ---------------- HELPERS ----------------
def normalize(vec):
    """Scale to length 1 so dot product == cosine similarity."""
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def _get(obj, key):
    return obj[key] if isinstance(obj, dict) else getattr(obj, key)


def generate_sparse(texts, input_type):
    """Sparse keyword vectors from Pinecone's hosted model.
    input_type: 'passage' for stored documents, 'query' for questions."""
    out = []
    for start in range(0, len(texts), 96):
        res = pc.inference.embed(
            model=SPARSE_MODEL,
            inputs=texts[start:start + 96],
            parameters={"input_type": input_type, "truncate": "END"},
        )
        for e in res:
            out.append({
                "indices": list(_get(e, "sparse_indices")),
                "values": list(_get(e, "sparse_values")),
            })
    return out


def reciprocal_rank_fusion(rankings, k=RRF_K):
    """RRF: each chunk earns 1/(k+rank) per list it appears in; scores add up."""
    scores, by_id = {}, {}
    for ranking in rankings:
        for rank, match in enumerate(ranking, start=1):
            scores[match.id] = scores.get(match.id, 0.0) + 1.0 / (k + rank)
            by_id[match.id] = match
    return [by_id[i] for i in sorted(scores, key=scores.get, reverse=True)]


def rerank_chunks(question, candidates, top_n):
    """Cross-encoder reranking. Falls back to RRF order if the reranker fails."""
    if not candidates:
        return []
    try:
        result = pc.inference.rerank(
            model=RERANK_MODEL,
            query=question,
            documents=[{"id": c.id, "text": c.metadata["content"]} for c in candidates],
            rank_fields=["text"],
            top_n=top_n,
            return_documents=False,
        )
        return [candidates[_get(r, "index")] for r in result.data]
    except Exception as e:
        print(f"⚠️ Rerank failed, using RRF order instead: {e}")
        return candidates[:top_n]
# -----------------------------------------


# ---------------- MAIN ENTRY POINTS ----------------
def retrieve(question):
    """Run dense + sparse search, fuse with RRF, rerank. Returns a list of chunk texts."""
    # 1. Dense
    query_embeddings = generate_embeddings([question], task_type="RETRIEVAL_QUERY")
    if not query_embeddings:
        raise RuntimeError("Failed to generate embeddings for the question.")
    dense = normalize(query_embeddings[0])

    dense_results = index.query(
        vector=dense, top_k=CANDIDATES_PER_SEARCH,
        include_metadata=True, namespace=NAMESPACE,
    )
    rankings = [dense_results.matches]

    # 2. Sparse
    sparse = generate_sparse([question], input_type="query")[0]
    if sparse["indices"]:
        try:
            sparse_results = index.query(
                vector=[0.0] * EMBEDDING_DIM,  # zero dense part: sparse signal only
                sparse_vector=sparse,
                top_k=CANDIDATES_PER_SEARCH,
                include_metadata=True, namespace=NAMESPACE,
            )
            rankings.append(sparse_results.matches)
        except Exception as e:
            print(f"⚠️ Sparse search failed, continuing with dense only: {e}")

    # 3. RRF + 4. Rerank
    fused = reciprocal_rank_fusion(rankings)
    top = rerank_chunks(question, fused[:RERANK_INPUT], FINAL_TOP_N)
    return [m.metadata["content"] for m in top]


def answer(question):
    """Retrieve, then generate. Returns a dict ready to jsonify."""
    chunks = retrieve(question)

    if not chunks:
        return {
            "answer": "I couldn't find anything relevant in the uploaded documents.",
            "sources": [],
        }

    context = "\n\n".join(chunks)
    response = llm.models.generate_content(
        model=ANSWER_MODEL,
        contents=(
            "Answer the question using only the context below. "
            "If the context doesn't contain the answer, say you don't know.\n\n"
            f"Context:\n{context}\n\nQuestion: {question}"
        ),
    )
    return {"answer": response.text, "sources": chunks}
def index_chunks(filename, chunks):
    """Embed chunks (dense + sparse) and upsert them into Pinecone."""
    dense_vectors = generate_embeddings(chunks)  # RETRIEVAL_DOCUMENT by default
    sparse_vectors = generate_sparse(chunks, input_type="passage")

    if not (len(chunks) == len(dense_vectors) == len(sparse_vectors)):
        raise RuntimeError(
            f"Mismatch: {len(chunks)} chunks, {len(dense_vectors)} dense, "
            f"{len(sparse_vectors)} sparse."
        )

    records = []
    for i in range(len(chunks)):
        record = {
            "id": f"{filename}-{i}",
            "values": normalize(dense_vectors[i]),
            "metadata": {"source": filename, "content": chunks[i]},
        }
        if sparse_vectors[i]["indices"]:
            record["sparse_values"] = sparse_vectors[i]
        records.append(record)

    for start in range(0, len(records), 100):
        index.upsert(vectors=records[start:start + 100], namespace=NAMESPACE)

    return len(chunks)
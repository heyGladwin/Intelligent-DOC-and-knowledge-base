"""
PIPELINE OVERVIEW (what technique is used where)
------------------------------------------------
UPLOAD  /upload-knowledge
    PDF -> chunks -> [DENSE embedding: Gemini] + [SPARSE embedding: Pinecone] -> upsert (same record)

ASK     /ask
    Question
      1. DENSE search   (meaning)   -> top 20 chunks   \
      2. SPARSE search  (keywords)  -> top 20 chunks   /  two separate rankings
      3. RRF fusion     -> merges both rankings into one candidate list
      4. RERANK         -> a cross-encoder model re-scores candidates, keeps best 5
      5. GENERATION     -> Gemini answers using only those 5 chunks (RAG)
"""

import os
import math
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv, find_dotenv

from google import genai
from utils import extract_and_chunk_pdf, generate_embeddings

load_dotenv(find_dotenv())
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# =====================================================================
# CONFIG
# =====================================================================
INDEX_NAME = os.getenv("PINECONE_INDEX", "intelligent-doc-hybrid")
NAMESPACE = "knowledge_base"
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "3072"))

SPARSE_MODEL = "pinecone-sparse-english-v0"  # SPARSE: keyword-style vectors (hosted by Pinecone)
RERANK_MODEL = "bge-reranker-v2-m3"          # RERANK: cross-encoder that re-scores (query, chunk) pairs

CANDIDATES_PER_SEARCH = 20  # how many chunks EACH search (dense / sparse) returns for RRF
RRF_K = 60                  # RRF smoothing constant; 60 is the standard default
RERANK_INPUT = 20           # how many fused candidates are sent to the reranker
FINAL_TOP_N = 5             # how many chunks finally go to Gemini

# =====================================================================
# PINECONE INDEX SETUP
# metric="dotproduct" is REQUIRED so one index can hold dense + sparse vectors.
# Dense vectors are L2-normalized in code, so dot product == cosine similarity.
# =====================================================================
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

if not pc.has_index(INDEX_NAME):
    pc.create_index(
        name=INDEX_NAME,
        dimension=EMBEDDING_DIM,
        metric="dotproduct",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )

index = pc.Index(INDEX_NAME)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    question: str


# =====================================================================
# HELPERS
# =====================================================================
def normalize(vec):
    """DENSE: scale a vector to length 1 so dot product behaves like cosine similarity."""
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def _get(obj, key):
    """Read a field whether the SDK returns a dict or an object."""
    return obj[key] if isinstance(obj, dict) else getattr(obj, key)


def generate_sparse(texts, input_type):
    """
    SPARSE EMBEDDING: turns text into keyword weights using Pinecone's hosted model.
    input_type: 'passage' for documents being stored, 'query' for the user's question.
    """
    out = []
    for start in range(0, len(texts), 96):  # model's max batch size is 96
        batch = texts[start:start + 96]
        res = pc.inference.embed(
            model=SPARSE_MODEL,
            inputs=batch,
            parameters={"input_type": input_type, "truncate": "END"},
        )
        for e in res:
            out.append({
                "indices": list(_get(e, "sparse_indices")),
                "values": list(_get(e, "sparse_values")),
            })
    return out


def reciprocal_rank_fusion(rankings, k=RRF_K):
    """
    RRF (Reciprocal Rank Fusion): merges several ranked lists into one.
    Each chunk earns 1 / (k + rank) from every list it appears in, and the scores add up.
    - A chunk ranked high in BOTH lists wins.
    - Uses only RANK POSITIONS, never raw scores, so dense and sparse scores
      (which are on different scales) can be combined fairly.
    """
    scores = {}
    by_id = {}
    for ranking in rankings:
        for rank, match in enumerate(ranking, start=1):
            scores[match.id] = scores.get(match.id, 0.0) + 1.0 / (k + rank)
            by_id[match.id] = match
    ordered_ids = sorted(scores, key=scores.get, reverse=True)
    return [by_id[i] for i in ordered_ids]


def rerank_chunks(question, candidates, top_n):
    """
    RERANKING: a cross-encoder reads the question and each chunk TOGETHER and scores
    how well the chunk answers the question. Slower than vector search but much more
    accurate, so it is only run on the small RRF candidate list.
    If the reranker fails (quota, network), we fall back to the RRF order.
    """
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


# =====================================================================
# UPLOAD
# =====================================================================
@app.post("/upload-knowledge")
async def upload_pdf(file: UploadFile = File(...)):
    temp_path = f"temp_{file.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        chunks = extract_and_chunk_pdf(temp_path)
        if not chunks:
            raise HTTPException(status_code=400, detail="PDF contains no readable text.")

        # DENSE embeddings (Gemini) -> capture meaning
        dense_vectors = generate_embeddings(chunks)  # task_type defaults to RETRIEVAL_DOCUMENT
        # SPARSE embeddings (Pinecone) -> capture exact keywords
        sparse_vectors = generate_sparse(chunks, input_type="passage")

        if not (len(chunks) == len(dense_vectors) == len(sparse_vectors)):
            raise HTTPException(
                status_code=500,
                detail=(
                    f"Mismatch: {len(chunks)} chunks, {len(dense_vectors)} dense, "
                    f"{len(sparse_vectors)} sparse."
                ),
            )

        records = []
        for i in range(len(chunks)):
            record = {
                "id": f"{file.filename}-{i}",  # deterministic ID: re-upload overwrites
                "values": normalize(dense_vectors[i]),
                "metadata": {"source": file.filename, "content": chunks[i]},
            }
            # Skip sparse part if the chunk produced no keywords (empty vectors are rejected)
            if sparse_vectors[i]["indices"]:
                record["sparse_values"] = sparse_vectors[i]
            records.append(record)

        for start in range(0, len(records), 100):
            index.upsert(vectors=records[start:start + 100], namespace=NAMESPACE)

        return {"status": "success", "message": f"Indexed {len(chunks)} sections (hybrid)."}

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Upload Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# =====================================================================
# ASK
# =====================================================================
@app.post("/ask")
async def ask_question(request: QuestionRequest):
    try:
        # ---- Step 1: embed the question both ways ----
        # DENSE query vector; RETRIEVAL_QUERY is the question-side task type
        query_embeddings = generate_embeddings(
            [request.question], task_type="RETRIEVAL_QUERY"
        )
        if not query_embeddings:
            return {"answer": "Error generating embedding for your question."}
        dense = normalize(query_embeddings[0])

        # SPARSE query vector; input_type='query' is the question-side setting
        sparse = generate_sparse([request.question], input_type="query")[0]

        # ---- Step 2: two SEPARATE searches ----
        # DENSE-ONLY search: ranks chunks by meaning
        dense_results = index.query(
            vector=dense,
            top_k=CANDIDATES_PER_SEARCH,
            include_metadata=True,
            namespace=NAMESPACE,
        )
        rankings = [dense_results.matches]

        # SPARSE-ONLY search: ranks chunks by keyword match.
        # A hybrid index still needs a dense vector, so we pass all zeros,
        # which contributes nothing and leaves only the sparse signal.
        if sparse["indices"]:
            try:
                sparse_results = index.query(
                    vector=[0.0] * EMBEDDING_DIM,
                    sparse_vector=sparse,
                    top_k=CANDIDATES_PER_SEARCH,
                    include_metadata=True,
                    namespace=NAMESPACE,
                )
                rankings.append(sparse_results.matches)
            except Exception as e:
                print(f"⚠️ Sparse search failed, continuing with dense only: {e}")

        # ---- Step 3: RRF fusion -> one merged candidate list ----
        fused = reciprocal_rank_fusion(rankings)
        if not fused:
            return {
                "answer": "I couldn't find anything relevant in the uploaded documents.",
                "sources": [],
            }

        # ---- Step 4: RERANK the top fused candidates, keep the best few ----
        top_chunks = rerank_chunks(request.question, fused[:RERANK_INPUT], FINAL_TOP_N)

        sources = [m.metadata["content"] for m in top_chunks]
        context = "\n\n".join(sources)

        # ---- Step 5: GENERATION (the "G" in RAG) ----
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=(
                "Answer the question using only the context below. "
                "If the context doesn't contain the answer, say you don't know.\n\n"
                f"Context:\n{context}\n\nQuestion: {request.question}"
            ),
        )

        return {"answer": response.text, "sources": sources}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    return {"message": "AI Document API is running!"}
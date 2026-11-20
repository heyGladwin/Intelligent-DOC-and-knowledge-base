# AI Document Q&A (Hybrid RAG + Knowledge Graph + Memory)

Upload PDFs and ask questions about them. Answers come only from your documents, using hybrid search, reranking, an entity-relation graph, and long-term memory per user.

## Features

- **Hybrid search:** dense embeddings (meaning) and sparse vectors (exact keywords) stored in one Pinecone index
- **Reciprocal Rank Fusion (RRF):** merges the dense, sparse and graph rankings by rank position
- **Reranking:** a cross-encoder (`bge-reranker-v2-m3`) re-scores the top 20 candidates and keeps the best 5
- **Knowledge graph (Neo4j):** entity relations extracted from each chunk, used to connect facts across documents
- **Long-term memory:** remembers durable facts and preferences per user, stored separately from documents
- **Grounded answers:** Gemini answers only from the retrieved context and says when it doesn't know

## How it works

```
UPLOAD  POST /upload-knowledge
  PDF -> text chunks (1000 chars, 200 overlap)
      -> dense embedding (Gemini) + sparse embedding (Pinecone) -> Pinecone "knowledge_base"
      -> entity relations (Gemini)                               -> Neo4j

ASK     POST /ask
  question -> dense search   (top 20)  \
           -> sparse search  (top 20)   }-> RRF -> rerank -> top 5 chunks
           -> graph lookup   (linked)  /
           -> user memories  (Pinecone "user_memory")
           -> Gemini answer (chunks + relationships + memories)
           -> new facts about the user saved to memory
```

## Tech stack

| Part | Technology |
|---|---|
| API | FastAPI, Uvicorn |
| Vector database | Pinecone (serverless, `dotproduct`, 3072 dims) |
| Graph database | Neo4j AuraDB |
| Embeddings | `gemini-embedding-2` (dense), `pinecone-sparse-english-v0` (sparse) |
| Reranker | `bge-reranker-v2-m3` (Pinecone hosted) |
| LLM | Gemini (answer model set in `ML/retrieval.py`) |
| PDF parsing | pypdf |

## Project structure

```
Rag/
├── api/
│   ├── app.py                  # FastAPI app, CORS, routers
│   └── routes/
│       ├── document_routes.py  # POST /upload-knowledge
│       └── chat_routes.py      # POST /ask, GET/DELETE /memory/{user_id}
├── ML/
│   ├── utils.py                # PDF chunking, Gemini embeddings
│   ├── retrieval.py            # hybrid search, RRF, rerank, answer generation
│   ├── graph_store.py          # Neo4j entity relations
│   └── memory.py               # long-term user memory
├── frontend.py                 # Streamlit UI (upload + chat)
├── requirement.txt
└── .env                        # not committed
```

## Setup

**1. Create a virtual environment (Python 3.12 recommended)**

```powershell
py -3.12 -m venv .venv312
.venv312\Scripts\activate
pip install -r requirement.txt
```

**2. Create `.env` in the project root**

```
GOOGLE_API_KEY=your_gemini_key
PINECONE_API_KEY=your_pinecone_key
NEO4J_URI=neo4j+s://xxxxxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password
```

Optional: `PINECONE_INDEX` (default `intelligent-doc-hybrid`), `EMBEDDING_DIM` (default `3072`).

The Pinecone index is created automatically on first start. Never commit `.env`.

**3. Run the API (from the project root)**

```powershell
uvicorn api.app:app --reload
```

Open http://127.0.0.1:8000/docs to try every endpoint in the browser.

**4. Run the UI (in a second terminal, from the project root)**

```powershell
streamlit run frontend.py
```

## API

| Method | Endpoint | Body / params | Returns |
|---|---|---|---|
| GET | `/` | none | health message |
| POST | `/upload-knowledge` | form field `file` (PDF) | sections indexed, relations stored, `graph` status |
| POST | `/ask` | `{"question": "...", "user_id": "alice"}` | `answer`, `sources`, `graph_facts`, `memories_used` |
| GET | `/memory/{user_id}` | none | stored memories for that user |
| DELETE | `/memory/{user_id}` | none | number of memories deleted |

`user_id` is optional and defaults to `default`, which is shared by everyone who omits it. Use a real user ID in production.

## Behaviour notes

- **Re-uploading a file** overwrites its chunks (IDs are `<filename>-<index>`) and replaces its graph relations.
- **The graph is optional.** If Neo4j can't connect at startup, the app prints a warning and runs without it. Upload returns `"graph": "disabled"`.
- **Fallbacks:** if sparse search or reranking fails, the request continues with a simpler ranking and prints a `⚠️` line.
- **Busy models:** graph extraction retries `503`/`429` errors with backoff, then tries a fallback model. A chunk that still fails is skipped.
- **Graph matching is by exact entity name** (after lowercasing and removing punctuation), so "Alice Chen" and "Alice" are different entities.

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: ML` or `api` | Run commands from the project root |
| `Vector dimension ... does not match` | Embeddings must be 3072 dims; recreate the index if it was made with another size |
| Neo4j `SSLCertVerificationError` | The driver trusts `certifi`'s CA list via `TrustCustomCAs(certifi.where())` with `neo4j://` and `encrypted=True` |
| Neo4j `AuthError` | Wrong password: Aura console → ⋯ → Recover Database Credentials |
| Very slow answers | Use a faster answer model or lower its thinking level |
| `pydantic-core` build fails | Use Python 3.12, or don't pin pydantic |

## Roadmap

- [x] Hybrid search, RRF, reranking
- [x] Neo4j entity-relation graph
- [x] Long-term user memory

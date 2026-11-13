import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv, find_dotenv

# NEW SDK
from google import genai
from utils import extract_and_chunk_pdf, generate_embeddings

load_dotenv(find_dotenv())
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# ---------------- Pinecone setup ----------------
INDEX_NAME = os.getenv("PINECONE_INDEX", "intelligent-doc")
NAMESPACE = "knowledge_base"
# MUST match your embedding model's output size:
#   gemini-embedding-001 -> 3072 (default) | text-embedding-004 -> 768
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "3072"))

pc = Pinecone(api_key=os.getenv("pcsk_RFsSS_63ZNNyxY71qyto1imkae1QaB8WfArkP8pGrRNMCUpLzHFiRWRFvjQcTwcZydsdH"))

if not pc.has_index(INDEX_NAME):
    pc.create_index(
        name=INDEX_NAME,
        dimension=EMBEDDING_DIM,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )

index = pc.Index(INDEX_NAME)
# ------------------------------------------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    question: str


@app.post("/upload-knowledge")
async def upload_pdf(file: UploadFile = File(...)):
    temp_path = f"temp_{file.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        chunks = extract_and_chunk_pdf(temp_path)
        if not chunks:
            raise HTTPException(status_code=400, detail="PDF contains no readable text.")

        vectors = generate_embeddings(chunks)

        # Alignment check
        if len(chunks) != len(vectors):
            raise HTTPException(
                status_code=500,
                detail=f"Mismatch: Got {len(chunks)} chunks but only {len(vectors)} vectors.",
            )

        # Deterministic IDs: re-uploading the same file overwrites instead of duplicating
        records = [
            {
                "id": f"{file.filename}-{i}",
                "values": vectors[i],
                "metadata": {"source": file.filename, "content": chunks[i]},
            }
            for i in range(len(chunks))
        ]

        # Upsert in batches (Pinecone recommends ~100 records per request)
        for start in range(0, len(records), 100):
            index.upsert(vectors=records[start:start + 100], namespace=NAMESPACE)

        return {"status": "success", "message": f"Indexed {len(chunks)} sections."}

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Upload Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.post("/ask")
async def ask_question(request: QuestionRequest):
    try:
        # Vectorize the question
        query_embeddings = generate_embeddings([request.question])
        if not query_embeddings:
            return {"answer": "Error generating embedding for your question."}

        query_vector = query_embeddings[0]

        # Vector search
        results = index.query(
            vector=query_vector,
            top_k=3,
            include_metadata=True,
            namespace=NAMESPACE,
        )
        MIN_SCORE = 0.5  # tune this by testing

        matches = [m for m in results.matches if m.score >= MIN_SCORE]
        if not matches:
            return {
        "answer": "I couldn't find anything relevant in the uploaded documents.",
        "sources": []
        }

        sources = [m.metadata["content"] for m in results.matches]
        context = "\n\n".join(sources)

        # Generate response
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Use this context to answer: {context}\n\nQuestion: {request.question}",
        )

        return {"answer": response.text, "sources": sources}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    return {"message": "AI Document API is running!"}
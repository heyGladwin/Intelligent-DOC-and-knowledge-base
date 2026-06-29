import os
import shutil
import certifi
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from dotenv import load_dotenv, find_dotenv

# NEW SDK
from google import genai
from utils import extract_and_chunk_pdf, generate_embeddings

load_dotenv(find_dotenv())
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# MongoDB Connection
mongo_uri = os.getenv("MONGO_URI")
mongo_client = MongoClient(mongo_uri, tlsCAFile=certifi.where())
db = mongo_client['intelligentDoc']
collection = db['knowledge_base']

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

        # 🚨 THE CRITICAL FIX: Alignment Check
        if len(chunks) != len(vectors):
            raise HTTPException(
                status_code=500, 
                detail=f"Mismatch: Got {len(chunks)} chunks but only {len(vectors)} vectors."
            )

        documents = [
            {
                "source": file.filename,
                "content": chunks[i],
                "embedding": vectors[i]
            }
            for i in range(len(chunks))
        ]

        collection.insert_many(documents)
        return {"status": "success", "message": f"Indexed {len(chunks)} sections."}

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

        # Vector Search
        pipeline = [
            {"$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": query_vector,
                "numCandidates": 10,
                "limit": 3
            }},
            {"$project": {"_id": 0, "content": 1}}
        ]
        
        results = list(collection.aggregate(pipeline))
        context = "\n\n".join([res['content'] for res in results])

        # Generate Response
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Use this context to answer: {context}\n\nQuestion: {request.question}"
        )

        return {"answer": response.text, "sources": [res['content'] for res in results]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/")
async def root():
    return {"message": "AI Document API is running!"}
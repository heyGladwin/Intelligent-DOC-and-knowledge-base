import os
import shutil

from fastapi import APIRouter, File, HTTPException, UploadFile

from ML.utils import extract_and_chunk_pdf
from ML.retrieval import index_chunks, llm, GRAPH_ENABLED
from ML import graph_store

router = APIRouter()


@router.post("/upload-knowledge")
def upload_pdf(file: UploadFile = File(...)):
    temp_path = f"temp_{file.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        chunks = extract_and_chunk_pdf(temp_path)
        if not chunks:
            raise HTTPException(status_code=400, detail="PDF contains no readable text.")

        # 1. Vectors -> Pinecone (dense + sparse). If this fails, the upload fails.
        count = index_chunks(file.filename, chunks)

        # 2. Entity relations -> Neo4j. Optional: a failure here does not fail the upload.
        relation_count = 0
        graph_status = "disabled"
        if GRAPH_ENABLED:
            try:
                relation_count = graph_store.add_document_triples(llm, file.filename, chunks)
                graph_status = "ok"
            except Exception as e:
                graph_status = "failed"
                print(f"⚠️ Graph storage failed for {file.filename}: {e}")

        return {
            "status": "success",
            "message": f"Indexed {count} sections and {relation_count} relations from {file.filename}",
            "graph": graph_status,
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Upload Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
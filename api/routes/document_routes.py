import os
import shutil

from fastapi import APIRouter, File, HTTPException, UploadFile

from ML.utils import extract_and_chunk_pdf
from ML.retrieval import index_chunks

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

        count = index_chunks(file.filename, chunks)
        return {
            "status": "success",
            "message": f"Indexed {count} sections (hybrid) from {file.filename}",
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Upload Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
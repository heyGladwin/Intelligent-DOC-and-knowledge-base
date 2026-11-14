from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ML.retrieval import answer

router = APIRouter()


class QuestionRequest(BaseModel):
    question: str


@router.post("/ask")
def ask(request: QuestionRequest):  # plain def: runs in a thread, since the pipeline blocks
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Missing 'question' in request body")
    try:
        return answer(question)
    except Exception as e:
        print(f"Server Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
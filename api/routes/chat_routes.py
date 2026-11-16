from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ML.retrieval import answer, index
from ML import memory

router = APIRouter()


class QuestionRequest(BaseModel):
    question: str
    user_id: str = "default"  # in production, take this from the logged-in user


@router.post("/ask")
def ask(request: QuestionRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Missing 'question' in request body")
    try:
        return answer(question, request.user_id.strip() or "default")
    except Exception as e:
        print(f"Server Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memory/{user_id}")
def get_memory(user_id: str):
    return {"user_id": user_id, "memories": memory.list_memories(index, user_id)}


@router.delete("/memory/{user_id}")
def delete_memory(user_id: str):
    return {"user_id": user_id, "deleted": memory.delete_memories(index, user_id)}
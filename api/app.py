from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.chat_routes import router as chat_router
from api.routes.document_routes import router as document_router

app = FastAPI(title="AI Document API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace with your frontend URL before deploying
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(document_router)
app.include_router(chat_router)


@app.get("/")
def root():
    return {"message": "AI Document API is running!"}
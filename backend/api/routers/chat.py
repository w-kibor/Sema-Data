from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class QueryRequest(BaseModel):
    question: str
    history: list = []

class QueryResponse(BaseModel):
    answer: str
    sources: list

@router.post("/chat", response_model=QueryResponse)
async def chat_endpoint(request: QueryRequest):
    """
    Endpoint to interact with the RAG system.
    """
    # TODO: Connect to RAG service
    return QueryResponse(
        answer=f"This is a mocked response to: '{request.question}'. The RAG system is not yet connected.",
        sources=[{"title": "Sample Source", "page": 1, "text": "This is a sample source text."}]
    )

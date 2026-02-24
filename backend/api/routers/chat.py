from fastapi import APIRouter, Request
from pydantic import BaseModel

from api.services.pdf import build_pdf_sources

router = APIRouter()

class QueryRequest(BaseModel):
    question: str
    history: list = []

class QueryResponse(BaseModel):
    answer: str
    sources: list

@router.post("/chat", response_model=QueryResponse)
async def chat_endpoint(payload: QueryRequest, request: Request):
    """
    Endpoint to interact with the RAG system.
    """
    # TODO: Connect to RAG service
    sources = build_pdf_sources(str(request.base_url))
    if not sources:
        sources = [
            {
                "title": "Sample Source",
                "page": 1,
                "text": "This is a sample source text.",
                "agency": "Public Records Office",
                "publishDate": "2024-01-15",
                "fileSize": "2.4 MB",
            }
        ]
    return QueryResponse(
        answer=f"This is a mocked response to: '{payload.question}'. The RAG system is not yet connected.",
        sources=sources,
    )

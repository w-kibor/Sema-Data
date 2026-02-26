from fastapi import APIRouter, Request
from pydantic import BaseModel

from api.services.pdf import build_pdf_source, build_pdf_sources
from api.services.rag import RAGService

router = APIRouter()
_rag_service: RAGService | None = None


def _get_rag_service() -> RAGService:
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service

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
    rag_service = _get_rag_service()
    await rag_service.ensure_indexed()
    result = await rag_service.get_response(payload.question)

    sources = []
    for source in result.sources:
        file_name = source.get("file_name")
        page = source.get("page") or 1
        text = source.get("text") or ""
        if file_name:
            enriched = build_pdf_source(str(request.base_url), file_name, page, text)
            if enriched:
                sources.append(enriched)
                continue
        sources.append(
            {
                "title": source.get("title") or "Unknown Document",
                "page": page,
                "text": text,
            }
        )

    if not sources:
        sources = build_pdf_sources(str(request.base_url))

    return QueryResponse(answer=result.answer, sources=sources)

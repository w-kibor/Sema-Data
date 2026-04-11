from fastapi.testclient import TestClient

import main
from api.routers import chat as chat_router
from api.services.rag import RAGResult


class _DummyRAGService:
    async def ensure_indexed(self) -> int:
        return 0

    async def get_response(self, query: str) -> RAGResult:
        return RAGResult(
            answer=f"Echo: {query}",
            sources=[
                {
                    "title": "Budget Circular",
                    "page": 7,
                    "text": "Funding update excerpt.",
                }
            ],
        )


class _DummyRAGServiceNoSources:
    async def ensure_indexed(self) -> int:
        return 0

    async def get_response(self, query: str) -> RAGResult:
        return RAGResult(answer=f"Echo: {query}", sources=[])


def test_chat_endpoint_returns_llm_answer_and_sources(monkeypatch) -> None:
    chat_router._rag_service = None
    monkeypatch.setattr(chat_router, "_get_rag_service", lambda: _DummyRAGService())

    client = TestClient(main.app)
    response = client.post("/api/v1/chat", json={"question": "Show me the budget changes", "history": []})

    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"] == "Echo: Show me the budget changes"
    assert payload["sources"][0]["title"] == "Budget Circular"
    assert payload["sources"][0]["page"] == 7


def test_chat_endpoint_falls_back_to_pdf_listing_when_no_sources(monkeypatch) -> None:
    fallback = [
        {
            "title": "Fallback Source",
            "page": 1,
            "text": "Preview",
        }
    ]
    chat_router._rag_service = None
    monkeypatch.setattr(chat_router, "_get_rag_service", lambda: _DummyRAGServiceNoSources())
    monkeypatch.setattr(chat_router, "build_pdf_sources", lambda *_args, **_kwargs: fallback)

    client = TestClient(main.app)
    response = client.post("/api/v1/chat", json={"question": "Any updates?", "history": []})

    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"] == "Echo: Any updates?"
    assert payload["sources"] == fallback

from api.services.rag import RAGService, _chunk_text


def test_chunk_text_respects_overlap() -> None:
    chunks = list(_chunk_text("abcdefghij", chunk_size=4, overlap=1))
    assert chunks == ["abcd", "defg", "ghij", "j"]


def test_chunk_text_ignores_empty_chunks() -> None:
    chunks = list(_chunk_text("   abc   ", chunk_size=20, overlap=0))
    assert chunks == ["abc"]


def test_build_prompt_embeds_sources_and_question() -> None:
    service = object.__new__(RAGService)
    prompt = service._build_prompt(
        "What changed in the budget?",
        [
            {"title": "County Budget", "page": 3, "text": "Health spending increased."},
            {"title": "Gazette Notice", "page": 12, "text": "Procurement amendment posted."},
        ],
    )

    assert "Source 1 (County Budget, page 3):" in prompt
    assert "Source 2 (Gazette Notice, page 12):" in prompt
    assert "What changed in the budget?" in prompt

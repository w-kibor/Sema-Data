from pathlib import Path

from api.services import pdf as pdf_service


def test_build_pdf_source_returns_none_for_missing_file(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(pdf_service, "PDF_LIBRARY_DIR", tmp_path)
    source = pdf_service.build_pdf_source("http://test/", "missing.pdf", 1, "example")
    assert source is None


def test_build_pdf_source_enriches_metadata(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(pdf_service, "PDF_LIBRARY_DIR", tmp_path)
    monkeypatch.setattr(pdf_service, "_ensure_thumbnail", lambda _: None)

    file_path = tmp_path / "county_budget_2024.pdf"
    file_path.write_bytes(b"%PDF-1.4 mock")

    source = pdf_service.build_pdf_source("http://test/", file_path.name, 2, "Budget excerpt")

    assert source is not None
    assert source["title"] == "county budget 2024"
    assert source["page"] == 2
    assert source["text"] == "Budget excerpt"
    assert source["url"] == f"http://test/pdfs/{file_path.name}"
    assert source["thumbnailUrl"] is None
    assert source["fileSize"].endswith("B")


def test_build_pdf_sources_respects_limit(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(pdf_service, "PDF_LIBRARY_DIR", tmp_path)
    monkeypatch.setattr(pdf_service, "_ensure_thumbnail", lambda _: Path("thumb.png"))

    for idx in range(3):
        (tmp_path / f"doc_{idx}.pdf").write_bytes(b"%PDF-1.4 mock")

    sources = pdf_service.build_pdf_sources("http://test/", limit=2)
    assert len(sources) == 2
    assert all(item["url"].startswith("http://test/pdfs/") for item in sources)
    assert all(item["thumbnailUrl"] == "http://test/thumbnails/thumb.png" for item in sources)

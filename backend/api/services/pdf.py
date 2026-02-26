from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import fitz

BASE_DIR = Path(__file__).resolve().parents[3]
PDF_LIBRARY_DIR = Path(os.getenv("PDF_LIBRARY_DIR", BASE_DIR / "pdf-library"))
THUMBNAIL_DIR = Path(os.getenv("PDF_THUMBNAIL_DIR", BASE_DIR / "pdf-thumbnails"))

PDF_LIBRARY_DIR.mkdir(parents=True, exist_ok=True)
THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)


def _format_size(num_bytes: int) -> str:
    if num_bytes < 1024:
        return f"{num_bytes} B"
    if num_bytes < 1024 * 1024:
        return f"{num_bytes / 1024:.1f} KB"
    return f"{num_bytes / (1024 * 1024):.1f} MB"


def _guess_agency(file_name: str) -> str:
    normalized = file_name.replace("_", " ").replace("-", " ").strip()
    tokens = [token for token in normalized.split() if token]
    if len(tokens) >= 2:
        return " ".join(tokens[:2]).title()
    return "Public Records Office"


def _ensure_thumbnail(pdf_path: Path) -> Optional[Path]:
    thumbnail_path = THUMBNAIL_DIR / f"{pdf_path.stem}.png"
    if thumbnail_path.exists():
        return thumbnail_path

    try:
        doc = fitz.open(pdf_path)
        page = doc.load_page(0)
        pix = page.get_pixmap(matrix=fitz.Matrix(1.2, 1.2))
        pix.save(thumbnail_path)
        doc.close()
        return thumbnail_path
    except Exception:
        return None


def list_pdfs(limit: int = 5) -> List[Path]:
    return list(PDF_LIBRARY_DIR.glob("*.pdf"))[:limit]


def build_pdf_sources(base_url: str, limit: int = 3) -> List[dict]:
    sources: List[dict] = []
    for pdf_path in list_pdfs(limit=limit):
        stat = pdf_path.stat()
        publish_date = datetime.fromtimestamp(stat.st_mtime).date().isoformat()
        thumbnail_path = _ensure_thumbnail(pdf_path)

        sources.append(
            {
                "title": pdf_path.stem.replace("_", " "),
                "page": 1,
                "text": "Excerpt preview is loading from the original document.",
                "url": f"{base_url}pdfs/{pdf_path.name}",
                "thumbnailUrl": f"{base_url}thumbnails/{thumbnail_path.name}" if thumbnail_path else None,
                "agency": _guess_agency(pdf_path.stem),
                "publishDate": publish_date,
                "fileSize": _format_size(stat.st_size),
            }
        )

    return sources


def build_pdf_source(base_url: str, file_name: str, page: int, text: str) -> Optional[dict]:
    pdf_path = PDF_LIBRARY_DIR / file_name
    if not pdf_path.exists():
        return None

    stat = pdf_path.stat()
    publish_date = datetime.fromtimestamp(stat.st_mtime).date().isoformat()
    thumbnail_path = _ensure_thumbnail(pdf_path)

    return {
        "title": pdf_path.stem.replace("_", " "),
        "page": page,
        "text": text,
        "url": f"{base_url}pdfs/{pdf_path.name}",
        "thumbnailUrl": f"{base_url}thumbnails/{thumbnail_path.name}" if thumbnail_path else None,
        "agency": _guess_agency(pdf_path.stem),
        "publishDate": publish_date,
        "fileSize": _format_size(stat.st_size),
    }

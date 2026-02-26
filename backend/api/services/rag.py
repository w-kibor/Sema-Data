from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import anyio
import fitz
import google.generativeai as genai

from api.services.pdf import PDF_LIBRARY_DIR

try:
    from pinecone import Pinecone, ServerlessSpec
except Exception:  # pragma: no cover - optional dependency shape
    Pinecone = None
    ServerlessSpec = None

try:
    import pinecone
except Exception:  # pragma: no cover - optional dependency shape
    pinecone = None


@dataclass
class RAGResult:
    answer: str
    sources: List[Dict[str, Any]]


def _chunk_text(text: str, chunk_size: int, overlap: int) -> Iterable[str]:
    if chunk_size <= 0:
        return
    step = max(chunk_size - overlap, 1)
    for start in range(0, len(text), step):
        chunk = text[start : start + chunk_size].strip()
        if chunk:
            yield chunk


class RAGService:
    def __init__(self) -> None:
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.pinecone_index = os.getenv("PINECONE_INDEX")
        self.pinecone_env = os.getenv("PINECONE_ENVIRONMENT")
        self.pinecone_cloud = os.getenv("PINECONE_CLOUD", "aws")
        self.pinecone_region = os.getenv("PINECONE_REGION", "us-east-1")
        self.namespace = os.getenv("PINECONE_NAMESPACE", "default")
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.embedding_model = os.getenv("GEMINI_EMBEDDING_MODEL", "models/embedding-001")
        self.chunk_size = int(os.getenv("RAG_CHUNK_SIZE", "1000"))
        self.chunk_overlap = int(os.getenv("RAG_CHUNK_OVERLAP", "200"))
        self.top_k = int(os.getenv("RAG_TOP_K", "4"))
        self.auto_ingest = os.getenv("RAG_AUTO_INGEST", "true").lower() == "true"
        self.batch_size = int(os.getenv("RAG_UPSERT_BATCH", "50"))

        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required")
        if not self.pinecone_api_key or not self.pinecone_index:
            raise ValueError("PINECONE_API_KEY and PINECONE_INDEX are required")

        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel(self.model_name)
        self._index = self._init_index()
        self._indexed = False

    def _init_index(self):
        if Pinecone is not None:
            client = Pinecone(api_key=self.pinecone_api_key)
            existing = client.list_indexes().names()
            if self.pinecone_index not in existing:
                client.create_index(
                    name=self.pinecone_index,
                    dimension=768,
                    metric="cosine",
                    spec=ServerlessSpec(cloud=self.pinecone_cloud, region=self.pinecone_region),
                )
            return client.Index(self.pinecone_index)

        if pinecone is None:
            raise RuntimeError("pinecone client is not available")

        pinecone.init(
            api_key=self.pinecone_api_key,
            environment=self.pinecone_env or "us-east1-gcp",
        )
        if self.pinecone_index not in pinecone.list_indexes():
            pinecone.create_index(self.pinecone_index, dimension=768, metric="cosine")
        return pinecone.Index(self.pinecone_index)

    def _embed(self, text: str, task_type: str) -> List[float]:
        result = genai.embed_content(
            model=self.embedding_model,
            content=text,
            task_type=task_type,
        )
        return result["embedding"]

    def _extract_chunks(self, pdf_path: Path) -> Iterable[Tuple[int, str]]:
        doc = fitz.open(pdf_path)
        try:
            for page_index in range(len(doc)):
                page = doc.load_page(page_index)
                text = page.get_text("text")
                for chunk in _chunk_text(text, self.chunk_size, self.chunk_overlap):
                    yield page_index + 1, chunk
        finally:
            doc.close()

    def _upsert_batch(self, items: List[Tuple[str, List[float], Dict[str, Any]]]) -> None:
        if not items:
            return
        if Pinecone is not None:
            self._index.upsert(vectors=items, namespace=self.namespace)
        else:
            self._index.upsert(vectors=items, namespace=self.namespace)

    def index_from_library(self) -> int:
        pdfs = list(PDF_LIBRARY_DIR.glob("*.pdf"))
        if not pdfs:
            return 0

        upsert_batch: List[Tuple[str, List[float], Dict[str, Any]]] = []
        total = 0
        for pdf_path in pdfs:
            title = pdf_path.stem.replace("_", " ")
            for chunk_idx, (page, chunk) in enumerate(self._extract_chunks(pdf_path)):
                embedding = self._embed(chunk, task_type="retrieval_document")
                vector_id = f"{pdf_path.stem}-p{page}-c{chunk_idx}"
                metadata = {
                    "file_name": pdf_path.name,
                    "title": title,
                    "page": page,
                    "text": chunk,
                }
                upsert_batch.append((vector_id, embedding, metadata))
                total += 1
                if len(upsert_batch) >= self.batch_size:
                    self._upsert_batch(upsert_batch)
                    upsert_batch = []

        self._upsert_batch(upsert_batch)
        return total

    async def ensure_indexed(self) -> int:
        if self._indexed or not self.auto_ingest:
            return 0
        count = await anyio.to_thread.run_sync(self.index_from_library)
        self._indexed = True
        return count

    def _query_index(self, query_vector: List[float]) -> List[Dict[str, Any]]:
        response = self._index.query(
            vector=query_vector,
            top_k=self.top_k,
            include_metadata=True,
            namespace=self.namespace,
        )
        matches = getattr(response, "matches", None) or response.get("matches", [])
        results = []
        for match in matches:
            metadata = getattr(match, "metadata", None) or match.get("metadata", {})
            results.append(metadata)
        return results

    def _build_prompt(self, question: str, contexts: List[Dict[str, Any]]) -> str:
        context_blocks = []
        for idx, ctx in enumerate(contexts, start=1):
            snippet = (ctx.get("text") or "").strip()
            title = ctx.get("title") or "Unknown Document"
            page = ctx.get("page") or "?"
            context_blocks.append(f"Source {idx} ({title}, page {page}):\n{snippet}")

        context_text = "\n\n".join(context_blocks)
        return (
            "You are Sema-Data, an AI assistant that answers questions about public records. "
            "Use the provided sources to answer the question. If the sources do not contain "
            "enough information, say so clearly.\n\n"
            f"Sources:\n{context_text}\n\n"
            f"Question: {question}\nAnswer:"
        )

    def _get_response_sync(self, query: str) -> RAGResult:
        query_vector = self._embed(query, task_type="retrieval_query")
        contexts = self._query_index(query_vector)
        prompt = self._build_prompt(query, contexts)
        response = self.model.generate_content(prompt)
        answer = response.text or "I could not generate an answer from the current sources."
        sources = []
        for ctx in contexts:
            sources.append(
                {
                    "file_name": ctx.get("file_name"),
                    "title": ctx.get("title"),
                    "page": ctx.get("page"),
                    "text": ctx.get("text"),
                }
            )
        return RAGResult(answer=answer, sources=sources)

    async def get_response(self, query: str) -> RAGResult:
        return await anyio.to_thread.run_sync(self._get_response_sync, query)

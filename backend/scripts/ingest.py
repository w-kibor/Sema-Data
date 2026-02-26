import argparse
import os
import sys
from pathlib import Path

# Add backend directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from api.services.rag import RAGService


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest PDFs from pdf-library into Pinecone.")
    parser.add_argument(
        "--pdf-dir",
        default=None,
        help="Override PDF_LIBRARY_DIR for this run.",
    )
    parser.add_argument(
        "--no-auto",
        action="store_true",
        help="Disable automatic ingestion inside the server.",
    )
    args = parser.parse_args()

    if args.pdf_dir:
        os.environ["PDF_LIBRARY_DIR"] = str(Path(args.pdf_dir).resolve())

    if args.no_auto:
        os.environ["RAG_AUTO_INGEST"] = "false"

    service = RAGService()
    total = service.index_from_library()
    print(f"Indexed {total} chunks.")


if __name__ == "__main__":
    main()

import os
import sys
from utils.ocr import extract_text_from_pdf

def process_pdf(file_path):
    """
    Extracts text from a PDF and returns it.
    """
    print(f"Processing {file_path}...")
    text = extract_text_from_pdf(file_path)
    if not text:
        print(f"No text extracted from {file_path}")
        return None
    return text

def main():
    print("Starting Sema-Data Ingestion Pipeline...")
    # TODO: Watch folder or process list of URLs
    
if __name__ == "__main__":
    main()


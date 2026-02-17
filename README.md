# Sema-Data: AI-Driven Transparency for African Public Records

## Problem Statement
Public governance in Africa suffers from an "Information Asymmetry" problem. Crucial data such as budgets, procurement records, and legal gazettes are locked in fragmented, non-machine-readable PDF formats. This "Data Silo" prevents citizens and SMEs from participating in the economy or holding institutions accountable.

## Proposed Solution
Sema-Data is an end-to-end Data Engineering and AI platform that digitizes, indexes, and makes public records "conversational" via a Retrieval-Augmented Generation (RAG) framework.

### Features
1.  **Automated Ingestion:** ETL pipeline monitoring government portals.
2.  **Semantic Search:** Vector Embeddings for context-aware search.
3.  **Citizen-Centric Interface:** Natural language interface for complex queries.

## Technical Stack
-   **Frontend:** Next.js Progressive Web App (PWA)
-   **Backend:** FastAPI
-   **AI Engine:** LangChain, Gemini 3 (via Groq), Pinecone
-   **Infrastructure:** Docker, AWS

## getting Started

### Prerequisites
-   Node.js & npm
-   Python 3.10+
-   Docker (optional)

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/sema-data.git
    cd sema-data
    ```

2.  Setup Frontend:
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

3.  Setup Backend:
    ```bash
    cd backend
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    uvicorn main:app --reload
    ```

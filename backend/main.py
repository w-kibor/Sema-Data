from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Sema-Data API",
    description="Backend for Sema-Data: AI-Driven Transparency for African Public Records",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to clean Sema-Data API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

from api.routers import chat
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.documents import router as documents_router
from app.rag.embeddings import generate_embedding
from app.rag.vector_store import get_chunk_count
from app.api.query import router as query_router
from app.llm.ollama_client import generate_structured_answer


app = FastAPI(
    title="SecureRAG-QR API",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    documents_router,
    prefix="/api/documents",
    tags=["Documents"]
)


@app.get("/")
def root():
    return {
        "message": "SecureRAG-QR backend is running"
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "application": "SecureRAG-QR"
    }

@app.get("/api/vector-store/count")
def vector_store_count():
    return {
        "stored_chunks": get_chunk_count()
    }

@app.get("/api/test-embedding")
def test_embedding():
    text = "SecureRAG-QR converts document knowledge into secure QR payloads"

    embedding = generate_embedding(text)

    return {
        "text": text,
        "embedding_dimension": len(embedding),
        "first_10_values": embedding[:10]
    }

app.include_router(
    documents_router,
    prefix="/api/documents",
    tags=["Documents"]
)

app.include_router(
    query_router,
    prefix="/api/query",
    tags=["Query"]
)
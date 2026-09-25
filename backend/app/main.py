from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.documents import router as documents_router


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
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from app.rag.retriever import retrieve_chunks
from app.rag.pipeline import run_rag_pipeline


router = APIRouter()


class QueryRequest(BaseModel):
    query: str
    document_id: str
    encrypt: bool = True
    password: str | None = None
    top_k: int = 3
    mode: Literal["fast", "ai"] = "fast"


@router.post("/")
def query_document(request: QueryRequest):
    chunks = retrieve_chunks(
        query=request.query,
        document_id=request.document_id,
        top_k=request.top_k
    )

    return {
        "query": request.query,
        "document_id": request.document_id,
        "results": chunks
    }


@router.post("/answer")
def answer_document(request: QueryRequest):
    result = run_rag_pipeline(
        query=request.query,
        document_id=request.document_id,
        encrypt=request.encrypt,
        password=request.password,
        top_k=request.top_k,
        mode=request.mode
    )

    return result

from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.ingestion.cleaner import clean_text
from app.ingestion.chunker import chunk_text
import uuid
from app.rag.embeddings import generate_embeddings
from app.rag.vector_store import store_chunks

from app.ingestion.pdf_loader import extract_text_from_pdf


router = APIRouter()

UPLOAD_DIR = Path("storage/documents")

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported right now."
        )

    file_path = UPLOAD_DIR / file.filename

    file_content = await file.read()

    with open(file_path, "wb") as saved_file:
        saved_file.write(file_content)

    extracted = extract_text_from_pdf(str(file_path))

    cleaned_text = clean_text(extracted["text"])

    chunks = chunk_text(
       cleaned_text,
       chunk_size=1000,
       overlap=200
    )
    document_id = str(uuid.uuid4())

    chunk_texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = generate_embeddings(chunk_texts)

    store_chunks(
        document_id=document_id,
        chunks=chunks,
        embeddings=embeddings
    )

    return {
        "document_id": document_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "page_count": extracted["page_count"],
        "character_count": len(extracted["text"]),
        "preview": extracted["text"][:500],
        "first_chunk": chunks[0] if chunks else None
    }
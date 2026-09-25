from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException

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

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "page_count": extracted["page_count"],
        "character_count": len(extracted["text"]),
        "preview": extracted["text"][:500]
    }
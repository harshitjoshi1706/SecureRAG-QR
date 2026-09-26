from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel

from app.rag.pipeline import run_rag_pipeline
from app.qr.packet import create_packet, packet_to_json
from app.qr.fragmenter import fragment_packet
from app.qr.generator import generate_qr_codes


router = APIRouter()


class TransferRequest(BaseModel):
    query: str
    document_id: str
    password: str
    top_k: int = 3


@router.post("/generate")
def generate_transfer(request: TransferRequest):

    result = run_rag_pipeline(
        query=request.query,
        document_id=request.document_id,
        password=request.password,
        top_k=request.top_k
    )

    encrypted = result["encrypted"]

    packet = create_packet(
        salt=encrypted["salt"],
        nonce=encrypted["nonce"],
        ciphertext=encrypted["ciphertext"]
    )

    packet_json = packet_to_json(packet)

    fragments = fragment_packet(
        packet_json=packet_json,
        transfer_id=packet["transfer_id"],
        fragment_size=800
    )

    qr_files = generate_qr_codes(
        fragments=fragments,
        transfer_id=packet["transfer_id"]
    )

    qr_urls = []

    for file_path in qr_files:
        filename = Path(file_path).name

        qr_urls.append(
            f"http://127.0.0.1:8000/qr/{filename}"
        )

    return {
        "transfer_id": packet["transfer_id"],
        "fragment_count": len(fragments),
        "qr_count": len(qr_files),
        "qr_urls": qr_urls,
        "answer": result["answer"],
        "size_metrics": result["size_metrics"]
    }
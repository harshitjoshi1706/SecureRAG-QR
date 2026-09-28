from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.transfer_store import get_transfer
from app.qr.packet import (
    create_encrypted_packet,
    create_unencrypted_packet,
    packet_to_json
)
from app.qr.fragmenter import fragment_packet
from app.qr.generator import generate_qr_codes


router = APIRouter()


class TransferRequest(BaseModel):
    transfer_id: str


@router.post("/generate")
def generate_transfer(request: TransferRequest):

    stored = get_transfer(
        request.transfer_id
    )

    if stored is None:
        raise HTTPException(
            status_code=404,
            detail="Transfer not found."
        )

    if stored["is_encrypted"]:
        encrypted_data = stored["encrypted_data"]

        packet = create_encrypted_packet(
            salt=encrypted_data["salt"],
            nonce=encrypted_data["nonce"],
            ciphertext=encrypted_data["ciphertext"]
        )

    else:
        packet = create_unencrypted_packet(
            compressed_data=stored["compressed_data"]
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
        "is_encrypted": stored["is_encrypted"],
        "fragment_count": len(fragments),
        "qr_count": len(qr_files),
        "qr_urls": qr_urls,
        "answer": stored["answer"],
        "size_metrics": stored["size_metrics"]
    }
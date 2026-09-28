from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.qr.receiver import MAX_FRAGMENTS, QRReceiver, receiver


router = APIRouter()


class FragmentRequest(BaseModel):
    fragment: str = Field(max_length=4096)


class RecoverRequest(BaseModel):
    transfer_id: str = Field(min_length=1, max_length=128)
    password: str | None = None


class DecodeRequest(RecoverRequest):
    fragments: list[str] = Field(min_length=1, max_length=MAX_FRAGMENTS)


@router.post("/decode")
def decode_transfer(request: DecodeRequest):
    """Request-local recovery: no shared fragment state or RAG dependencies."""
    local_receiver = QRReceiver()
    try:
        for fragment in request.fragments:
            local_receiver.add_fragment(fragment)
        payload = local_receiver.recover_payload(request.transfer_id, request.password)
        return {"success": True, "payload": payload}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.post("/fragment")
def add_fragment(request: FragmentRequest):
    try:
        return receiver.add_fragment(request.fragment)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.post("/recover")
def recover_transfer(request: RecoverRequest):
    try:
        payload = receiver.recover_payload(request.transfer_id, request.password)
        return {"success": True, "payload": payload}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.post("/reset")
def reset_transfer():
    receiver.reset()
    return {"success": True}

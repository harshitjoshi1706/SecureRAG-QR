from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.qr.receiver import receiver


router = APIRouter()


class FragmentRequest(BaseModel):
    fragment: str


class RecoverRequest(BaseModel):
    transfer_id: str
    password: str


@router.post("/fragment")
def add_fragment(request: FragmentRequest):
    try:
        return receiver.add_fragment(
            request.fragment
        )

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.post("/recover")
def recover_transfer(request: RecoverRequest):
    try:
        payload = receiver.recover_payload(
            transfer_id=request.transfer_id,
            password=request.password
        )

        return {
            "success": True,
            "payload": payload
        }

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )
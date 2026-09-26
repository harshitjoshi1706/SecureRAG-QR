import base64
import json
import uuid


PROTOCOL_VERSION = "SRQ1"


def create_packet(
    salt: bytes,
    nonce: bytes,
    ciphertext: bytes
) -> dict:

    transfer_id = str(uuid.uuid4())

    packet = {
        "version": PROTOCOL_VERSION,
        "transfer_id": transfer_id,
        "salt": base64.b64encode(salt).decode("utf-8"),
        "nonce": base64.b64encode(nonce).decode("utf-8"),
        "ciphertext": base64.b64encode(ciphertext).decode("utf-8")
    }

    return packet


def packet_to_json(packet: dict) -> str:
    return json.dumps(
        packet,
        separators=(",", ":")
    )


def json_to_packet(packet_json: str) -> dict:
    return json.loads(packet_json)

def decode_packet(packet: dict) -> dict:
    return {
        "version": packet["version"],
        "transfer_id": packet["transfer_id"],
        "salt": base64.b64decode(packet["salt"]),
        "nonce": base64.b64decode(packet["nonce"]),
        "ciphertext": base64.b64decode(packet["ciphertext"])
    }
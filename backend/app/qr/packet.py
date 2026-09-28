import base64
import binascii
import json
import uuid


PROTOCOL_VERSION = "SRQ1"


def create_encrypted_packet(
    salt: bytes,
    nonce: bytes,
    ciphertext: bytes
) -> dict:

    return {
        "version": PROTOCOL_VERSION,
        "transfer_id": str(uuid.uuid4()),
        "encrypted": True,
        "salt": base64.b64encode(
            salt
        ).decode("utf-8"),
        "nonce": base64.b64encode(
            nonce
        ).decode("utf-8"),
        "payload": base64.b64encode(
            ciphertext
        ).decode("utf-8")
    }


def create_unencrypted_packet(
    compressed_data: bytes
) -> dict:

    return {
        "version": PROTOCOL_VERSION,
        "transfer_id": str(uuid.uuid4()),
        "encrypted": False,
        "payload": base64.b64encode(
            compressed_data
        ).decode("utf-8")
    }


def packet_to_json(packet: dict) -> str:
    return json.dumps(
        packet,
        separators=(",", ":")
    )


def json_to_packet(packet_json: str) -> dict:
    return json.loads(packet_json)


def decode_packet(packet: dict) -> dict:
    """Validate SRQ1 and decode bytes without changing the wire format."""
    if not isinstance(packet, dict) or packet.get("version") != PROTOCOL_VERSION:
        raise ValueError("Unsupported or malformed SRQ1 packet.")
    if not isinstance(packet.get("transfer_id"), str) or not packet["transfer_id"]:
        raise ValueError("Packet transfer ID is missing.")
    if type(packet.get("encrypted")) is not bool:
        raise ValueError("Packet encrypted flag must be true or false.")

    def decode_field(name: str) -> bytes:
        value = packet.get(name)
        if not isinstance(value, str) or not value:
            raise ValueError(f"Packet {name} must be a nonempty Base64 string.")
        try:
            return base64.b64decode(value, validate=True)
        except (ValueError, binascii.Error) as error:
            raise ValueError(f"Packet {name} contains invalid Base64.") from error

    payload = decode_field("payload")
    if not packet["encrypted"]:
        return {"compressed_data": payload}

    salt, nonce = decode_field("salt"), decode_field("nonce")
    if len(salt) != 16 or len(nonce) != 12 or len(payload) < 16:
        raise ValueError("Invalid encrypted packet salt, nonce, or ciphertext length.")
    return {"salt": salt, "nonce": nonce, "ciphertext": payload}

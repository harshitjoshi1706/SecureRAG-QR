import json

import zstandard as zstd
from cryptography.exceptions import InvalidTag

from app.qr.assembler import assemble_fragments
from app.qr.packet import PROTOCOL_VERSION, json_to_packet, decode_packet
from app.crypto.encryptor import decrypt_data


MAX_FRAGMENTS = 4096
MAX_FRAGMENT_CHARS = 4096
MAX_PACKET_CHARS = 4 * 1024 * 1024
MAX_RECOVERED_BYTES = 8 * 1024 * 1024


class QRReceiver:
    def __init__(self):
        self.sessions = {}

    def add_fragment(self, fragment_json: str) -> dict:
        if not isinstance(fragment_json, str) or len(fragment_json) > MAX_FRAGMENT_CHARS:
            raise ValueError("QR fragment is too large or malformed.")
        try:
            fragment = json.loads(fragment_json)
        except (ValueError, TypeError) as error:
            raise ValueError("QR does not contain valid fragment JSON.") from error
        if not isinstance(fragment, dict) or fragment.get("version") != PROTOCOL_VERSION:
            raise ValueError("QR is not an SRQ1 fragment.")
        transfer_id = fragment.get("transfer_id")
        index, total = fragment.get("fragment_index"), fragment.get("fragment_total")
        payload = fragment.get("payload")
        if not isinstance(transfer_id, str) or not 1 <= len(transfer_id) <= 128:
            raise ValueError("Invalid fragment transfer ID.")
        if type(total) is not int or not 1 <= total <= MAX_FRAGMENTS:
            raise ValueError("Invalid fragment total.")
        if type(index) is not int or not 1 <= index <= total:
            raise ValueError("Fragment index is outside the transfer range.")
        if not isinstance(payload, str) or not payload:
            raise ValueError("Fragment payload must be a nonempty string.")
        if self.sessions and transfer_id not in self.sessions:
            raise ValueError("This fragment belongs to another transfer. Reset first.")
        session = self.sessions.setdefault(transfer_id, {"total": total, "fragments": {}})
        if session["total"] != total:
            raise ValueError("Fragment total mismatch.")
        existing = session["fragments"].get(index)
        duplicate = existing is not None
        if duplicate and json.loads(existing)["payload"] != payload:
            raise ValueError("Conflicting duplicate fragment. Reset and upload the original QR images.")
        if not duplicate:
            size = sum(len(json.loads(item)["payload"]) for item in session["fragments"].values())
            if size + len(payload) > MAX_PACKET_CHARS:
                raise ValueError("Transfer exceeds the receiver size limit.")
            session["fragments"][index] = fragment_json
        received = len(session["fragments"])
        return {
            "transfer_id": transfer_id, "received": received, "total": total,
            "complete": received == total, "duplicate": duplicate,
        }

    def recover_payload(self, transfer_id: str, password: str | None = None) -> dict:
        if transfer_id not in self.sessions:
            raise ValueError("Unknown transfer ID.")
        session = self.sessions[transfer_id]
        if len(session["fragments"]) != session["total"]:
            raise ValueError(f"Transfer is incomplete: {len(session['fragments'])} of {session['total']} fragments received.")
        try:
            packet = json_to_packet(assemble_fragments(list(session["fragments"].values())))
        except ValueError as error:
            raise ValueError("Reconstructed packet is malformed.") from error
        decoded = decode_packet(packet)
        if packet["transfer_id"] != transfer_id:
            raise ValueError("Packet transfer ID does not match its fragments.")
        if packet["encrypted"]:
            if not password:
                raise ValueError("Enter the password for this encrypted transfer.")
            try:
                compressed = decrypt_data(**decoded, password=password)
            except InvalidTag as error:
                raise ValueError("Incorrect password or damaged encrypted data.") from error
        else:
            compressed = decoded["compressed_data"]
        try:
            # Bound decompression even when the frame advertises a very large size.
            with zstd.ZstdDecompressor().stream_reader(compressed) as reader:
                recovered = reader.read(MAX_RECOVERED_BYTES + 1)
            if len(recovered) > MAX_RECOVERED_BYTES:
                raise ValueError("Recovered information exceeds the receiver size limit.")
        except zstd.ZstdError as error:
            raise ValueError("Packet contains invalid Zstandard data.") from error
        try:
            result = json.loads(recovered.decode("utf-8"))
        except (UnicodeDecodeError, ValueError) as error:
            raise ValueError("Recovered information is not valid UTF-8 JSON.") from error
        if not isinstance(result, dict) or not isinstance(result.get("answer"), str):
            raise ValueError("Recovered information must contain an answer string.")
        facts, chunks = result.get("facts", []), result.get("source_chunks", [])
        if not isinstance(facts, list) or not all(isinstance(item, str) for item in facts):
            raise ValueError("Recovered facts must be a list of strings.")
        if not isinstance(chunks, list) or not all(type(item) is int for item in chunks):
            raise ValueError("Recovered source chunks must be a list of integers.")
        return {**result, "facts": facts, "source_chunks": chunks}

    def reset(self):
        self.sessions.clear()


# Compatibility for existing clients of /fragment and /recover.
receiver = QRReceiver()

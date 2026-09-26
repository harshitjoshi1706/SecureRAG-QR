import json

from app.qr.assembler import assemble_fragments
from app.qr.packet import json_to_packet, decode_packet
from app.crypto.encryptor import decrypt_data
from app.compression.compressor import decompress_data


class QRReceiver:
    def __init__(self):
        self.sessions = {}

    def add_fragment(self, fragment_json: str) -> dict:
        fragment = json.loads(fragment_json)

        transfer_id = fragment["transfer_id"]
        fragment_index = fragment["fragment_index"]
        fragment_total = fragment["fragment_total"]

        if transfer_id not in self.sessions:
            self.sessions[transfer_id] = {
                "total": fragment_total,
                "fragments": {}
            }

        session = self.sessions[transfer_id]

        if session["total"] != fragment_total:
            raise ValueError("Fragment total mismatch.")

        session["fragments"][fragment_index] = fragment_json

        received = len(session["fragments"])

        return {
            "transfer_id": transfer_id,
            "received": received,
            "total": fragment_total,
            "complete": received == fragment_total
        }

    def recover_payload(
        self,
        transfer_id: str,
        password: str
    ) -> dict:

        if transfer_id not in self.sessions:
            raise ValueError("Unknown transfer ID.")

        session = self.sessions[transfer_id]

        fragments = list(
            session["fragments"].values()
        )

        if len(fragments) != session["total"]:
            raise ValueError("Transfer is incomplete.")

        packet_json = assemble_fragments(
            fragments
        )

        packet = json_to_packet(
            packet_json
        )

        decoded = decode_packet(
            packet
        )

        decrypted_compressed = decrypt_data(
            salt=decoded["salt"],
            nonce=decoded["nonce"],
            ciphertext=decoded["ciphertext"],
            password=password
        )

        recovered_bytes = decompress_data(
            decrypted_compressed
        )

        recovered_payload = json.loads(
            recovered_bytes.decode("utf-8")
        )

        return recovered_payload


receiver = QRReceiver()
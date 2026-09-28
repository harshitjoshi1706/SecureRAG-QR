import base64
import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.documents import router as documents_router
from app.api.query import router as query_router
from app.api.receiver import router as receiver_router
from app.api.transfer import router as transfer_router

from app.rag.embeddings import generate_embedding
from app.rag.vector_store import get_chunk_count

from app.compression.compressor import (
    compress_data,
    decompress_data
)

from app.crypto.encryptor import (
    encrypt_data,
    decrypt_data
)

from app.qr.packet import (
    create_encrypted_packet,
    create_unencrypted_packet,
    packet_to_json,
    json_to_packet
)

from app.qr.fragmenter import fragment_packet
from app.qr.generator import generate_qr_codes
from app.qr.assembler import assemble_fragments


app = FastAPI(
    title="SecureRAG-QR API",
    version="0.1.0"
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Routers
# --------------------------------------------------

app.include_router(
    documents_router,
    prefix="/api/documents",
    tags=["Documents"]
)

app.include_router(
    query_router,
    prefix="/api/query",
    tags=["Query"]
)

app.include_router(
    receiver_router,
    prefix="/api/receiver",
    tags=["Receiver"]
)

app.include_router(
    transfer_router,
    prefix="/api/transfer",
    tags=["Transfer"]
)


# --------------------------------------------------
# QR static files
# --------------------------------------------------

app.mount(
    "/qr",
    StaticFiles(directory="storage/qr"),
    name="qr"
)


# --------------------------------------------------
# Root
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "SecureRAG-QR backend is running"
    }


# --------------------------------------------------
# Health test
# --------------------------------------------------

@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "application": "SecureRAG-QR"
    }


# --------------------------------------------------
# Vector store test
# --------------------------------------------------

@app.get("/api/vector-store/count")
def vector_store_count():
    return {
        "stored_chunks": get_chunk_count()
    }


# --------------------------------------------------
# Embedding test
# --------------------------------------------------

@app.get("/api/test-embedding")
def test_embedding():

    text = (
        "SecureRAG-QR converts document knowledge "
        "into secure QR payloads"
    )

    embedding = generate_embedding(text)

    return {
        "text": text,
        "embedding_dimension": len(embedding),
        "first_10_values": embedding[:10]
    }


# --------------------------------------------------
# Compression test
# --------------------------------------------------

@app.get("/api/test-compression")
def test_compression():

    payload = {
        "answer": "Fixed-size chunking was most robust.",
        "facts": [
            "It had the smallest relative degradation.",
            "It had low computational cost."
        ],
        "source_chunks": [34, 35]
    }

    json_string = json.dumps(
        payload,
        separators=(",", ":")
    )

    original_bytes = json_string.encode("utf-8")

    compressed = compress_data(
        original_bytes
    )

    decompressed = decompress_data(
        compressed
    )

    recovered_string = decompressed.decode(
        "utf-8"
    )

    return {
        "original_bytes": len(original_bytes),
        "compressed_bytes": len(compressed),
        "recovered_matches_original": (
            recovered_string == json_string
        )
    }


# --------------------------------------------------
# Encryption test
# --------------------------------------------------

@app.get("/api/test-encryption")
def test_encryption():

    original_data = (
        b"SecureRAG-QR encrypted payload"
    )

    password = "test-password"

    encrypted = encrypt_data(
        data=original_data,
        password=password
    )

    decrypted = decrypt_data(
        salt=encrypted["salt"],
        nonce=encrypted["nonce"],
        ciphertext=encrypted["ciphertext"],
        password=password
    )

    return {
        "original_bytes": len(original_data),
        "encrypted_bytes": len(
            encrypted["ciphertext"]
        ),
        "decryption_successful": (
            decrypted == original_data
        )
    }


# --------------------------------------------------
# Encrypted packet test
# --------------------------------------------------

@app.get("/api/test-packet")
def test_packet():

    original_data = (
        b"SecureRAG-QR packet test"
    )

    password = "test-password"

    encrypted = encrypt_data(
        data=original_data,
        password=password
    )

    packet = create_encrypted_packet(
        salt=encrypted["salt"],
        nonce=encrypted["nonce"],
        ciphertext=encrypted["ciphertext"]
    )

    packet_json = packet_to_json(
        packet
    )

    parsed_packet = json_to_packet(
        packet_json
    )

    salt = base64.b64decode(
        parsed_packet["salt"]
    )

    nonce = base64.b64decode(
        parsed_packet["nonce"]
    )

    ciphertext = base64.b64decode(
        parsed_packet["payload"]
    )

    decrypted = decrypt_data(
        salt=salt,
        nonce=nonce,
        ciphertext=ciphertext,
        password=password
    )

    return {
        "protocol_version": packet["version"],
        "transfer_id": packet["transfer_id"],
        "encrypted": packet["encrypted"],
        "packet_json_bytes": len(
            packet_json.encode("utf-8")
        ),
        "recovered_matches_original": (
            decrypted == original_data
        )
    }


# --------------------------------------------------
# Unencrypted packet test
# --------------------------------------------------

@app.get("/api/test-unencrypted-packet")
def test_unencrypted_packet():

    original_data = (
        b"SecureRAG-QR standard packet test"
    )

    compressed = compress_data(
        original_data
    )

    packet = create_unencrypted_packet(
        compressed_data=compressed
    )

    packet_json = packet_to_json(
        packet
    )

    parsed_packet = json_to_packet(
        packet_json
    )

    compressed_payload = base64.b64decode(
        parsed_packet["payload"]
    )

    recovered_data = decompress_data(
        compressed_payload
    )

    return {
        "protocol_version": packet["version"],
        "transfer_id": packet["transfer_id"],
        "encrypted": packet["encrypted"],
        "recovered_matches_original": (
            recovered_data == original_data
        )
    }


# --------------------------------------------------
# QR generation test
# --------------------------------------------------

@app.get("/api/test-qr")
def test_qr():

    test_data = (
        b"SecureRAG-QR QR fragmentation test "
        * 50
    )

    password = "test-password"

    encrypted = encrypt_data(
        data=test_data,
        password=password
    )

    packet = create_encrypted_packet(
        salt=encrypted["salt"],
        nonce=encrypted["nonce"],
        ciphertext=encrypted["ciphertext"]
    )

    packet_json = packet_to_json(
        packet
    )

    fragments = fragment_packet(
        packet_json=packet_json,
        transfer_id=packet["transfer_id"],
        fragment_size=800
    )

    qr_files = generate_qr_codes(
        fragments=fragments,
        transfer_id=packet["transfer_id"]
    )

    return {
        "transfer_id": packet["transfer_id"],
        "packet_bytes": len(
            packet_json.encode("utf-8")
        ),
        "fragment_count": len(fragments),
        "qr_count": len(qr_files),
        "qr_files": qr_files
    }


# --------------------------------------------------
# Full reconstruction test
# --------------------------------------------------

@app.get("/api/test-reconstruction")
def test_reconstruction():

    original_payload = {
        "answer": "Fixed-size chunking was most robust.",
        "facts": [
            "It had the smallest relative degradation.",
            "It had low computational cost."
        ],
        "source_chunks": [34, 35]
    }

    password = "test-password"

    # 1. JSON -> bytes
    payload_json = json.dumps(
        original_payload,
        separators=(",", ":")
    )

    original_bytes = payload_json.encode(
        "utf-8"
    )

    # 2. Compress
    compressed = compress_data(
        original_bytes
    )

    # 3. Encrypt
    encrypted = encrypt_data(
        data=compressed,
        password=password
    )

    # 4. Create encrypted packet
    packet = create_encrypted_packet(
        salt=encrypted["salt"],
        nonce=encrypted["nonce"],
        ciphertext=encrypted["ciphertext"]
    )

    packet_json = packet_to_json(
        packet
    )

    # 5. Fragment packet
    fragments = fragment_packet(
        packet_json=packet_json,
        transfer_id=packet["transfer_id"],
        fragment_size=80
    )

    # 6. Reverse fragments to test ordering
    shuffled_fragments = list(
        reversed(fragments)
    )

    # 7. Reassemble fragments
    reconstructed_json = assemble_fragments(
        shuffled_fragments
    )

    # 8. Parse reconstructed packet
    parsed_packet = json_to_packet(
        reconstructed_json
    )

    # 9. Decode Base64 fields
    salt = base64.b64decode(
        parsed_packet["salt"]
    )

    nonce = base64.b64decode(
        parsed_packet["nonce"]
    )

    ciphertext = base64.b64decode(
        parsed_packet["payload"]
    )

    # 10. Decrypt
    decrypted_compressed = decrypt_data(
        salt=salt,
        nonce=nonce,
        ciphertext=ciphertext,
        password=password
    )

    # 11. Decompress
    recovered_bytes = decompress_data(
        decrypted_compressed
    )

    # 12. Convert back to JSON
    recovered_payload = json.loads(
        recovered_bytes.decode("utf-8")
    )

    return {
        "fragment_count": len(fragments),
        "fragments_received_in_reverse_order": True,
        "reconstruction_successful": (
            recovered_payload == original_payload
        ),
        "recovered_payload": recovered_payload
    }
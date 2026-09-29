import json
import uuid
from typing import Literal

from app.rag.retriever import retrieve_chunks
from app.compression.compressor import compress_data
from app.crypto.encryptor import encrypt_data
from app.transfer_store import save_transfer


def run_rag_pipeline(
    query: str,
    document_id: str,
    encrypt: bool,
    password: str | None = None,
    top_k: int = 3,
    mode: Literal["fast", "ai"] = "fast"
) -> dict:

    if mode not in ("fast", "ai"):
        raise ValueError("Processing mode must be 'fast' or 'ai'.")

    retrieved_chunks = retrieve_chunks(
        query=query,
        document_id=document_id,
        top_k=top_k
    )

    context_parts = []

    for chunk in retrieved_chunks:
        chunk_number = chunk["metadata"]["chunk_number"]
        text = chunk["text"]

        context_parts.append(
            f"[Chunk {chunk_number}]\n{text}"
        )

    context = "\n\n".join(context_parts)

    if mode == "fast":
        # Preserve the full text of the requested top-k chunks, in retrieval order.
        # No Ollama import or generation call is made on this branch.
        payload = {
            "mode": "fast",
            "query": query,
            "retrieved_information": [
                {
                    "chunk_number": chunk["metadata"]["chunk_number"],
                    "text": chunk["text"]
                }
                for chunk in retrieved_chunks
            ],
            "source_chunks": [
                chunk["metadata"]["chunk_number"] for chunk in retrieved_chunks
            ]
        }
    else:
        from app.llm.ollama_client import generate_structured_answer

        prompt = f"""
You must answer using only the provided context.

Question:
{query}

Context:
{context}

Return only JSON in exactly this structure:

{{
  "answer": "short direct answer",
  "facts": [
    "important supporting fact",
    "important supporting fact"
  ],
  "source_chunks": [1, 2]
}}

Rules:
- Use only the provided context.
- Do not invent facts.
- Keep the answer short.
- Keep facts concise.
- source_chunks must contain the chunk numbers that support the answer.
- Do not include markdown.
- Do not include explanations outside the JSON.
"""

        structured_answer = generate_structured_answer(prompt)
        payload = {**structured_answer.model_dump(), "mode": "ai"}

    retrieved_text_size = len(
        context.encode("utf-8")
    )

    compact_json = json.dumps(
        payload,
        separators=(",", ":")
    )

    compact_bytes = compact_json.encode("utf-8")

    compact_payload_size = len(
        compact_bytes
    )

    compressed_bytes = compress_data(
        compact_bytes
    )

    compressed_payload_size = len(
        compressed_bytes
    )

    encrypted_data = None
    encrypted_payload_size = None

    if encrypt:
        if not password:
            raise ValueError(
                "Password is required for encrypted transfer."
            )

        encrypted_data = encrypt_data(
            data=compressed_bytes,
            password=password
        )

        encrypted_payload_size = len(
            encrypted_data["ciphertext"]
        )

    size_metrics = {
        "retrieved_context_bytes": retrieved_text_size,
        "compact_payload_bytes": compact_payload_size,
        "compressed_payload_bytes": compressed_payload_size,
        "encrypted_payload_bytes": encrypted_payload_size,
        "reduction_bytes": (
            retrieved_text_size - compact_payload_size
        ),
        "compression_saved_bytes": (
            compact_payload_size - compressed_payload_size
        )
    }

    transfer_id = str(uuid.uuid4())

    save_transfer(
        transfer_id,
        {
            "is_encrypted": encrypt,
            "encrypted_data": encrypted_data,
            "compressed_data": compressed_bytes,
            "answer": payload,
            "size_metrics": size_metrics
        }
    )

    return {
        "transfer_id": transfer_id,
        "query": query,
        "is_encrypted": encrypt,
        "answer": payload,
        "mode": mode,
        "size_metrics": size_metrics,
        "sources": retrieved_chunks
    }

import json

from app.rag.retriever import retrieve_chunks
from app.llm.ollama_client import generate_structured_answer
from app.compression.compressor import compress_data
from app.crypto.encryptor import encrypt_data


def run_rag_pipeline(
    query: str,
    document_id: str,
    password: str,
    top_k: int = 3
) -> dict:

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

    retrieved_text_size = len(
        context.encode("utf-8")
    )

    compact_json = json.dumps(
        structured_answer.model_dump(),
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

    encrypted = encrypt_data(
        data=compressed_bytes,
        password=password
    )

    encrypted_payload_size = len(
        encrypted["ciphertext"]
    )

    return {
        "query": query,
        "answer": structured_answer.model_dump(),
        "size_metrics": {
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
        },
        "sources": retrieved_chunks,
        "encrypted": encrypted
    }
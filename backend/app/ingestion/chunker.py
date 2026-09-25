def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200
) -> list[dict]:

    chunks = []

    start = 0
    chunk_number = 1

    while start < len(text):
        end = start + chunk_size

        chunk = text[start:end]

        chunks.append({
            "chunk_number": chunk_number,
            "text": chunk,
            "start_char": start,
            "end_char": min(end, len(text))
        })

        start += chunk_size - overlap
        chunk_number += 1

    return chunks
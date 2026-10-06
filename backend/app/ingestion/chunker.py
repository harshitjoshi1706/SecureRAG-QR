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

# Currently chunker is fixed -size character chunking. It does not consider semantic meaning or sentence boundaries. Future improvements could include:
# 1. Sentence-based chunking: Split text into sentences and create chunks based on sentence boundaries to preserve semantic meaning.
# 2. Paragraph-based chunking: Split text into paragraphs and create chunks based on paragraph boundaries to maintain context.
# 3. Semantic chunking: Use NLP techniques to identify semantically meaningful chunks of text, which could improve the quality of the chunks for downstream tasks like summarization or question answering.
# 4. Adaptive chunking: Dynamically adjust chunk size based on the content, such as increasing chunk size for less dense text and decreasing it for more dense text, to optimize the balance between context and chunk size.
# 5. Overlap optimization: Experiment with different overlap sizes or use adaptive overlap based on the content to ensure that important context is preserved across chunks without creating excessive redundancy.
import chromadb


client = chromadb.PersistentClient(
    path="storage/chroma"
)

collection = client.get_or_create_collection(
    name="secure_rag_documents"
)

def get_chunk_count() -> int:
    return collection.count()

def store_chunks(
    document_id: str,
    chunks: list[dict],
    embeddings: list[list[float]]
):
    ids = []
    documents = []
    metadatas = []

    for index, chunk in enumerate(chunks):
        chunk_id = f"{document_id}_chunk_{chunk['chunk_number']}"

        ids.append(chunk_id)
        documents.append(chunk["text"])

        metadatas.append({
            "document_id": document_id,
            "chunk_number": chunk["chunk_number"],
            "start_char": chunk["start_char"],
            "end_char": chunk["end_char"]
        })

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )
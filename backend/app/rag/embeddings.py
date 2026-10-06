from sentence_transformers import SentenceTransformer # sentence_transformers is a Python library used for converting text into embeddings

MODEL_NAME = "BAAI/bge-small-en-v1.5"

model = SentenceTransformer(MODEL_NAME)


def generate_embedding(text: str) -> list[float]:
    embedding = model.encode(text)
    return embedding.tolist()
# for single text, we can use the generate_embedding function to get the embedding vector as a list of floats.

def generate_embeddings(texts: list[str]) -> list[list[float]]:
    embeddings = model.encode(texts) # Instead of calling the model three separate times manually: you pass the whole list: This is called batch encoding.

    return embeddings.tolist()

# for multiple texts, we can use the generate_embeddings function to get the embedding vectors as a list of lists of floats.
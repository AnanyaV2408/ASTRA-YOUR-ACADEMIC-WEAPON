from sentence_transformers import SentenceTransformer


# Load the embedding model once.
model = SentenceTransformer("all-MiniLM-L6-v2")


def create_embeddings(chunks):
    """
    Convert text chunks into numerical vectors.
    """

    if not chunks:
        return []

    embeddings = model.encode(
        chunks,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    return embeddings
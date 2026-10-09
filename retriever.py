import numpy as np


def retrieve_top_chunks(
    query_embedding,
    chunks,
    chunk_embeddings,
    top_k=3
):
    # If there is nothing to search
    if not chunks or len(chunk_embeddings) == 0:
        return []

    # Convert to NumPy arrays
    query_embedding = np.asarray(query_embedding)
    chunk_embeddings = np.asarray(chunk_embeddings)

    # Calculate cosine similarity
    # Embeddings are already normalized,
    # so dot product = cosine similarity
    similarities = np.dot(
        chunk_embeddings,
        query_embedding
    )

    # Get indices of the highest similarity scores
    top_indices = np.argsort(
        similarities
    )[::-1][:top_k]

    results = []

    for index in top_indices:

        results.append(
            {
                "chunk": chunks[index],
                "score": float(similarities[index]),
                "index": int(index)
            }
        )

    return results
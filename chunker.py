def chunk_text(text, chunk_size=500, overlap=100):
    """
    Split document text into overlapping chunks.

    chunk_size:
        Maximum number of words in each chunk.

    overlap:
        Number of words repeated between consecutive chunks.
    """

    if not text or not text.strip():
        return []

    if overlap >= chunk_size:
        raise ValueError(
            "Overlap must be smaller than chunk size."
        )

    words = text.split()

    chunks = []

    step = chunk_size - overlap

    for start in range(0, len(words), step):

        end = start + chunk_size

        chunk = " ".join(words[start:end]).strip()

        if chunk:
            chunks.append(chunk)

        # Stop once we've reached the end
        if end >= len(words):
            break

    return chunks
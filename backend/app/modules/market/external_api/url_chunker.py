def chunk_ids_for_url(ids: list[str], url: str, max_length: int = 2048) -> list[list[str]]:
    chunks = []
    current_chunk = []
    current_length = len(url)
    for id in ids:
        if current_length + len(id) + 1 > max_length and current_chunk:
            chunks.append(current_chunk)
            current_chunk = []
            current_length = len(url)
        current_chunk.append(id)
        current_length += len(id) + 1
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

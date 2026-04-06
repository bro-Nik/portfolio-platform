def chunk_ids_for_url(ids: list[str], url: str, max_length: int = 2048) -> list[list[str]]:
    """Разбивает ID на чанки, чтобы URL не превышал лимит длины.

    Args:
        ids: Список ID для добавления в URL
        url: Полный URL
        max_length: Максимальная длина URL (по умолчанию 2048)

    Returns:
        Список чанков ID, каждый из которых безопасно добавить в URL

    """
    chunks = []
    current_chunk = []
    current_length = len(url)

    for id in ids:
        # Проверяем, влезет ли следующий ID
        if current_length + len(id) + 1 > max_length and current_chunk:
            chunks.append(current_chunk)
            current_chunk = []
            current_length = len(url)

        current_chunk.append(id)
        current_length += len(id) + 1

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

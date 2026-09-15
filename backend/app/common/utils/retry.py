import asyncio
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import httpx

logger = logging.getLogger(__name__)


def exponential_backoff(attempt: int, base: float, cap: float) -> float:
    """Задержка перед повтором: base * 2^attempt, ограниченная сверху cap."""
    return min(base * (2**attempt), cap)


def parse_retry_after(response: 'httpx.Response', default: float = 5.0) -> float:
    """Достаёт Retry-After из заголовков ответа, иначе — значение по умолчанию."""
    raw = response.headers.get('Retry-After')
    if raw:
        try:
            return float(raw)
        except ValueError:
            pass
    return default


async def retry_pause(
    attempt: int,
    max_retries: int,
    *,
    subject: str,
    error: Exception | None = None,
    retry_after: float | None = None,
    base: float = 1.0,
    cap: float = 30.0,
) -> None:
    """Логирует причину и выдерживает паузу перед повторной попыткой.

    `retry_after` (например, из заголовка 429-ответа) имеет приоритет над экспоненциальным backoff.
    """
    if retry_after is not None:
        logger.warning('%s: 429, повтор через %.1fс (попытка %d/%d)', subject, retry_after, attempt + 1, max_retries)
        await asyncio.sleep(retry_after)
        return
    delay = exponential_backoff(attempt, base, cap)
    suffix = f': {error}' if error else ''
    logger.warning('%s: повтор через %.1fс (попытка %d/%d)%s', subject, delay, attempt + 1, max_retries, suffix)
    await asyncio.sleep(delay)

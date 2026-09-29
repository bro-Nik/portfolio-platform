import logging

from app.core.database import AsyncSessionLocal
from app.core.taskiq import broker
from app.modules.auth.repositories import TokenRepository
from app.modules.auth.services.email import EmailService

logger = logging.getLogger(__name__)


@broker.task(task_name='send_verification_email')
async def send_verification_email(email: str, token: str) -> None:
    await EmailService.send_verification_email(email, token)


@broker.task(task_name='send_password_reset_email')
async def send_password_reset_email(email: str, token: str) -> None:
    await EmailService.send_password_reset_email(email, token)


@broker.task(task_name='send_password_reset_confirmation_email')
async def send_password_reset_confirmation_email(email: str) -> None:
    await EmailService.send_password_reset_confirmation_email(email)


@broker.task(task_name='cleanup_expired_tokens')
async def cleanup_expired_tokens() -> dict:
    """Удаляет истёкшие refresh-токены вместе с привязанными сессиями.

    Сессия хранит IP-адрес и отпечаток устройства, поэтому она не должна жить
    дольше токена, который её создал.
    """
    async with AsyncSessionLocal() as session:
        removed = await TokenRepository(session).delete_expired()
        await session.commit()
    logger.info('Удалено истёкших refresh-токенов: %s', removed)
    return {'removed': removed}

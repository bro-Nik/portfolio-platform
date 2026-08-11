import argparse
import asyncio
import logging
import sys

from app.core.database import AsyncSessionLocal
from app.modules.auth.repositories import UserRepository
from app.modules.auth.security import SecurityService

logger = logging.getLogger(__name__)

MIN_PASSWORD_LENGTH = 8


async def set_password(email: str, password: str) -> None:
    async with AsyncSessionLocal() as session:
        repo = UserRepository(session)
        user = await repo.get_by_email(email)
        if not user:
            raise SystemExit(f'Пользователь с email {email} не найден')
        await repo.update(user.id, {'password_hash': SecurityService.get_password_hash(password)})
        await session.commit()
        logger.info('Пароль пользователя %s обновлён', email)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    parser = argparse.ArgumentParser(description='Set a new password without a mail server')
    parser.add_argument('--email', required=True)
    parser.add_argument('--password', help='New password; if omitted, read from stdin')
    args = parser.parse_args()

    password = args.password if args.password is not None else sys.stdin.readline().strip()
    if len(password) < MIN_PASSWORD_LENGTH:
        raise SystemExit('Пароль слишком короткий (минимум 8 символов)')
    asyncio.run(set_password(args.email, password))


if __name__ == '__main__':
    main()

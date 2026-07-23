import argparse
import asyncio
import logging
import os

from app.common.schemas import AuthUser, Context
from app.common.schemas.auth import UserRole
from app.core.database import AsyncSessionLocal
from app.modules.auth.repositories import UserRepository
from app.modules.auth.schemas import UserCreateRequest
from app.modules.auth.services.user import UserService
from app.modules.market.repositories import ProviderRepository, TaskRepository
from app.modules.market.schemas.provider import ProviderCreate
from app.modules.market.schemas.task import TaskCreate


logger = logging.getLogger(__name__)

async def run(admin_email: str, admin_password: str) -> None:
    async with AsyncSessionLocal() as session:
        user_repo = UserRepository(session)
        provider_repo = ProviderRepository(session)
        task_repo = TaskRepository(session)

        user_count = await user_repo.count()
        if user_count > 0:
            return

        logger.info("Создание admin-пользователя: %s", admin_email)
        user_data = UserCreateRequest(email=admin_email, password=admin_password, role=UserRole.ADMIN)
        ctx = Context(_actor=AuthUser(id=0, role=UserRole.ADMIN, login=admin_email.split("@")[0]), client_ip="seed", request_id="seed")
        user_service = UserService(session, ctx)
        user = await user_service.create(user_data)

        ctx = Context(
            _actor=AuthUser(id=user.id, role=UserRole.ADMIN, login=admin_email.split("@")[0]),
            client_ip="seed",
            request_id="seed",
        )
        provider_exists = await provider_repo.exists_by_name("CoinGecko")
        if not provider_exists:
            logger.info("Создание провайдера CoinGecko")
            provider_data = ProviderCreate(
                name="CoinGecko",
                is_active=True,
            )
            await provider_repo.create(provider_data.model_dump())
            await session.flush()
        else:
            logger.info("Провайдер CoinGecko уже существует — пропускаем")

        if not await task_repo.exists_by_name("Update prices (Coingecko)"):
            logger.info("Создание задачи обновления цен (ежедневно)")
            price_task = TaskCreate(
                name="Update prices (Coingecko)",
                provider_name="CoinGecko",
                task_type="selective_price_update",
                schedule="0 0 * * *",
                parameters={"strategy": "all"},
            )
            await task_repo.create(price_task.model_dump())
        else:
            logger.info("Задача обновления цен уже существует — пропускаем")

        if not await task_repo.exists_by_name("Load tickers (Coingecko)"):
            logger.info("Создание задачи загрузки тикеров (ежемесячно)")
            load_task = TaskCreate(
                name="Load tickers (Coingecko)",
                provider_name="CoinGecko",
                task_type="load_tickers",
                schedule="0 0 1 * *",
                parameters={"strategy": "all"},
            )
            await task_repo.create(load_task.model_dump())
        else:
            logger.info("Задача загрузки тикеров уже существует — пропускаем")

        await session.commit()
        logger.info("Seed завершён")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    parser = argparse.ArgumentParser(description="Seed initial data")
    parser.add_argument("--admin-email", default=os.getenv("SEED_ADMIN_EMAIL", "admin@example.com"))
    parser.add_argument("--admin-password", default=os.getenv("SEED_ADMIN_PASSWORD", "admin123"))
    args = parser.parse_args()
    asyncio.run(run(args.admin_email, args.admin_password))


if __name__ == "__main__":
    main()

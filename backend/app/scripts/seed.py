import argparse
import asyncio
import logging
import os
from datetime import UTC, datetime, timedelta

from app.common.schemas.auth import UserRole
from app.core.database import AsyncSessionLocal
import app.modules.auth.models

from app.modules.auth.repositories import UserRepository
from app.modules.auth.security import SecurityService
import app.modules.market.models
from app.modules.market.constants import CURRENCY_CODES
from app.modules.market.models import Ticker
from app.modules.market.repositories import ProviderRepository, TaskRepository, TickerRepository
from app.modules.market.schemas.provider import ProviderCreate
from app.modules.market.schemas.task import TaskCreate
import app.modules.portfolios.models
import app.modules.tags.models

logger = logging.getLogger(__name__)

_CURRENCY_NAMES = {
    'AED': 'United Arab Emirates Dirham',
    'AMD': 'Armenian Dram',
    'AUD': 'Australian Dollar',
    'AZN': 'Azerbaijani Manat',
    'BRL': 'Brazilian Real',
    'BYN': 'New Belarusian Ruble',
    'CAD': 'Canadian Dollar',
    'CHF': 'Swiss Franc',
    'CNY': 'Chinese Yuan',
    'CZK': 'Czech Republic Koruna',
    'DKK': 'Danish Krone',
    'EUR': 'Euro',
    'GBP': 'British Pound Sterling',
    'GEL': 'Georgian Lari',
    'HKD': 'Hong Kong Dollar',
    'HUF': 'Hungarian Forint',
    'IDR': 'Indonesian Rupiah',
    'ILS': 'Israeli New Sheqel',
    'INR': 'Indian Rupee',
    'ISK': 'Icelandic Króna',
    'JPY': 'Japanese Yen',
    'KGS': 'Kyrgystani Som',
    'KRW': 'South Korean Won',
    'KZT': 'Kazakhstani Tenge',
    'MDL': 'Moldovan Leu',
    'MXN': 'Mexican Peso',
    'MYR': 'Malaysian Ringgit',
    'NOK': 'Norwegian Krone',
    'NZD': 'New Zealand Dollar',
    'PHP': 'Philippine Peso',
    'PLN': 'Polish Zloty',
    'RON': 'Romanian Leu',
    'RUB': 'Russian Ruble',
    'SEK': 'Swedish Krona',
    'SGD': 'Singapore Dollar',
    'THB': 'Thai Baht',
    'TJS': 'Tajikistani Somoni',
    'TRY': 'Turkish Lira',
    'UAH': 'Ukrainian Hryvnia',
    'USD': 'United States Dollar',
    'UZS': 'Uzbekistan Som',
    'VND': 'Vietnamese Dong',
    'ZAR': 'South African Rand',
}


async def seed_currencies(session) -> None:
    ticker_repo = TickerRepository(session)
    existing = await ticker_repo.get_all(Ticker.market == 'currency')
    existing_symbols = {t.symbol for t in existing}
    missing = [code for code in CURRENCY_CODES if code not in existing_symbols]
    if not missing:
        logger.info('Валюты уже есть (%d шт.) — пропускаем', len(existing))
        return
    logger.info('Создание валют: %s', ', '.join(missing))
    await ticker_repo.create_all([
        {
            'market': 'currency',
            'symbol': code,
            'name': _CURRENCY_NAMES.get(code, code),
            'price': 1.0 if code == 'USD' else 0.0,
        }
        for code in missing
    ])
    await session.flush()


async def run(admin_email: str, admin_password: str) -> None:
    async with AsyncSessionLocal() as session:
        user_repo = UserRepository(session)
        provider_repo = ProviderRepository(session)
        task_repo = TaskRepository(session)

        await seed_currencies(session)
        await session.commit()

        user_count = await user_repo.count()
        if user_count > 0:
            return

        logger.info("Создание admin-пользователя: %s", admin_email)
        security = SecurityService()
        await user_repo.create({
            'email': admin_email,
            'password_hash': security.get_password_hash(admin_password),
            'role': UserRole.ADMIN,
            'status': 'active',
        })
        await session.flush()

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
                next_run=datetime.now(UTC) + timedelta(minutes=2),
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
                next_run=datetime.now(UTC),
            )
            await task_repo.create(load_task.model_dump())
        else:
            logger.info("Задача загрузки тикеров уже существует — пропускаем")

        await session.commit()
        logger.info("Seed завершён")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    parser = argparse.ArgumentParser(description="Seed initial data")
    parser.add_argument("--admin-email", default=os.getenv("ADMIN_EMAIL", "admin@example.com"))
    parser.add_argument("--admin-password", default=os.getenv("ADMIN_PASSWORD", "admin123"))
    args = parser.parse_args()
    asyncio.run(run(args.admin_email, args.admin_password))


if __name__ == "__main__":
    main()

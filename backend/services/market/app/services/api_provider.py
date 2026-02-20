from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.repositories.async_repo.api_provider import ApiProviderRepository
from app.external_api.management.registry import ApiProviderRegistry, registry


class ApiProviderService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ApiProviderRepository(db)

    async def get_providers(self, skip: int = 0, limit: Optional[int] = None, active_only: bool = False):
        return await self.repo.get_all(skip, limit, active_only)

    async def get_provider(self, provider_id: int):
        return await self.repo.get(provider_id)

    async def create_provider(self, data: schemas.ApiProviderCreate):
        """Создать API провайдера с бизнес-логикой"""
        try:
            # Проверка на уникальность имени
            existing = await self.repo.get_by_name(data.name)
            if existing:
                raise ValueError(f'Сервис с именем "{data.name}" уже существует')

            # Дополнительная логика
            if data.requests_per_minute > 1000:
                raise ValueError('Слишком много запросов в минуту')

            # Создание
            provider = await self.repo.create(data)

            await self.db.commit()
            await self.db.refresh(provider)
            return provider

        except Exception as e:
            await self.db.rollback()
            raise

    async def update_provider(self, provider_id: int, data: schemas.ApiProviderUpdate):
        """Обновить API провайдера с бизнес-логикой"""
        try:
            # Дополнительная логика
            if data.requests_per_minute and data.requests_per_minute > 1000:
                raise ValueError('Слишком много запросов в минуту')

            # Маскируем API ключ при обновлении
            if 'api_key' in data and data['api_key'] == '***':
                del data['api_key']

            # Обновление
            provider = await self.repo.update(provider_id, data)

            await self.db.commit()
            await self.db.refresh(provider)
            return provider

        except Exception as e:
            await self.db.rollback()
            raise

    async def delete_provider(self, provider_id: int):
        try:
            await self.repo.delete(provider_id)
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise

    async def reset_counters(self, provider_id: int):
        provider = await self.repo.get(provider_id)
        if not provider:
            return None

        try:
            if provider:
                now = datetime.utcnow()
                provider.minute_counter = 0
                provider.hour_counter = 0
                provider.day_counter = 0
                provider.month_counter = 0
                provider.last_minute_reset = now
                provider.last_hour_reset = now
                provider.last_day_reset = now
                provider.last_month_reset = now
                provider.updated_at = now

                await self.db.commit()
                await self.db.refresh(provider)

        except Exception as e:
            await self.db.rollback()
            raise

        return provider

    async def get_stats(self, provider_id: int) -> Dict[str, Any]:
        """Получить статистику по провайдеру"""
        provider = await self.repo.get(provider_id)
        if not provider:
            return {}

        # Запросы за последние 24 часа
        day_ago = datetime.utcnow() - timedelta(days=10)
        logs = await self.repo.get_logs_to_stats(provider_id, day_ago)

        # Расчет процентов использования
        minute_percent = (provider.minute_counter / provider.requests_per_minute * 100) if provider.requests_per_minute else 0
        hour_percent = (provider.hour_counter / provider.requests_per_hour * 100) if provider.requests_per_hour else 0
        day_percent = (provider.day_counter / provider.requests_per_day * 100) if provider.requests_per_day else 0

        return {
            'provider_name': provider.name,
            'requests_today': logs.total or 0,
            'successful_today': logs.successful or 0,
            'failed_today': (logs.total or 0) - (logs.successful or 0),
            'avg_response_time': round(logs.avg_response_time or 0, 2),
            'minute_counter': provider.minute_counter,
            'minute_limit': provider.requests_per_minute,
            'hour_counter': provider.hour_counter,
            'hour_limit': provider.requests_per_hour,
            'day_counter': provider.day_counter,
            'day_limit': provider.requests_per_day,
            'month_counter': provider.month_counter,
            'month_limit': provider.requests_per_month,
            'pending_in_queue': 0,
            'utilization_percent': {
                'minute': round(minute_percent, 2),
                'hour': round(hour_percent, 2),
                'day': round(day_percent, 2),
            }
        }

    async def get_logs(
        self,
        provider_id: int,
        hours: int = 24,
        limit: Optional[int] = 100
    ):

        last_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        logs = await self.repo.get_logs(provider_id, last_time=last_time, limit=limit)
        return logs

    async def get_provider_with_methods(self) -> List[Dict[str, Any]]:
        result = []
        providers = await self.get_providers(active_only=True)
        for provider in providers:
            methods = ApiProviderRegistry.get_provider_methods(provider.name)
            methods_list = []
            if methods:
                for method_name, method in methods.items():
                    methods_list.append(method_name)
            if methods:
                info = {
                    'id': provider.id,
                    'name': provider.display_name or provider.name,
                    'methods': methods_list
                }
                result.append(info)
        return result

    def get_providers_with_settings(self) -> List[Dict[str, Any]]:
        result = []
        providers = registry.PROVIDERS
        for provider_name in providers:
            provider = providers[provider_name]
            provider_dict = {
                'name': provider_name,
                'display_name': provider.DISPLAY_NAME,
                'description': provider.DESCRIPTION,
                'requests_per_minute': provider.REQUESTS_PER_MINUTE,
                'requests_per_hour': provider.REQUESTS_PER_HOUR,
                'requests_per_day': provider.REQUESTS_PER_DAY,
                'requests_per_month': provider.REQUESTS_PER_MONTH,
                'timeout': provider.TIMEOUT,
                'api_key_note': provider.API_KEY_NOTE
            }
            result.append(provider_dict)

        return result

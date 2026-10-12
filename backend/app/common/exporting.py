"""Машиночитаемая выгрузка строк БД: общее ядро персональных экспортов.

Модули описывают свои разделы через коллекторы (см. auth.protocols),
а сериализация строк одинакова для всех — поэтому живёт здесь.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

#: Поля, которые не попадают в выгрузку: выгрузка предназначена для предъявления
#: субъекту, а не для переноса сессий или доступа к чужим ресурсам.
SECRET_FIELDS = frozenset(
    {
        'password_hash',
        'token',
        'token_hash',
        'reset_password_token_hash',
        'reset_password_token_expires_at',
    }
)


def serialize_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    return value


def model_rows(entities: list[Any]) -> list[dict[str, Any]]:
    """Самоописание строк по колонкам модели, без секретных полей."""
    if not entities:
        return []
    columns = [c for c in entities[0].__table__.columns if c.key not in SECRET_FIELDS]
    return [{c.key: serialize_value(getattr(entity, c.key)) for c in columns} for entity in entities]


async def fetch_all(session: AsyncSession, model: Any, *conditions: Any) -> list[Any]:
    stmt = select(model).where(*conditions) if conditions else select(model)
    return list((await session.execute(stmt)).scalars())

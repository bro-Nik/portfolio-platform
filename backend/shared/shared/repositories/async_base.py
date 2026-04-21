# pyright: reportAttributeAccessIssue=false

from collections.abc import Sequence
from typing import TYPE_CHECKING

from pydantic import BaseModel
from sqlalchemy import delete, exists, select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import ColumnElement

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


Id = int | str
Ids = list[Id]
Rel = Sequence[str] | None
Order = Sequence[ColumnElement] | None
Where = ColumnElement[bool] | None


class BaseAsyncRepository[Model, CreateSchema: BaseModel, UpdateSchema: BaseModel]:
    """Базовый асинхронный CRUD репозиторий для SQLAlchemy.

    Примечание:
        - Требуется commit для сохранения изменений
        - Возвращает None если объект не найден
    """

    def __init__(self, model: type[Model], session: 'AsyncSession') -> None:
        self.model = model
        self.session = session

    async def get(self, id: Id, relations: Rel = None) -> Model | None:
        """Получить объект по ID."""
        return await self._get_one(self.model.id == id, relations=relations)

    async def get_by(self, *where: Where, order: Order = None, relations: Rel = None) -> Model | None:
        """Получить объект по условию."""
        return await self._get_one(*where, order=order, relations=relations)

    async def get_many(self, ids: Ids, relations: Rel = None) -> list[Model]:
        """Получить список объектов по списку ID."""
        return await self._get_many(self.model.id.in_(ids), relations=relations) if ids else []

    async def get_all(self, *where: Where, order: Order = None, relations: Rel = None) -> list[Model]:
        """Получить список объектов по условию."""
        return await self._get_many(*where, order=order, relations=relations)

    async def create(self, data: CreateSchema) -> Model:
        """Создать объект."""
        obj = self.model(**data.model_dump())
        self.session.add(obj)
        return obj

    async def create_many(self, objects: Sequence[CreateSchema]) -> list[Model]:
        """Создать несколько объектов."""
        objs = [self.model(**obj.model_dump()) for obj in objects]
        self.session.add_all(objs)
        return objs

    async def update(self, id: Id, data: UpdateSchema, *, partial: bool = True) -> Model | None:
        """Обновить объект по ID."""
        return await self._update_one(data, self.model.id == id, partial=partial)

    async def update_by(self, data: UpdateSchema, *where: Where, partial: bool = True) -> Model | None:
        """Обновить объект по условию."""
        return await self._update_one(data, *where, partial=partial)

    async def update_many(self, ids: Ids, data: UpdateSchema, *, partial: bool = True) -> list[Model]:
        """Обновить несколько объектов по списку ID."""
        return await self._update_many(data, self.model.id.in_(ids), partial=partial) if ids else []

    async def update_all(self, data: UpdateSchema, *where: Where, partial: bool = True) -> list[Model]:
        """Обновить несколько объектов по условию."""
        return await self._update_many(data, *where, partial=partial)

    async def delete(self, id: Id) -> Id:
        """Удалить объект по ID."""
        return await self._delete_one(self.model.id == id)

    async def delete_by(self, *where: Where, order: Order = None) -> Id:
        """Удалить объект по условию."""
        return await self._delete_one(*where, order=order)

    async def delete_many(self, ids: Ids) -> Ids:
        """Удалить несколько объектов по списку ID, вернуть список ID удалённых."""
        return await self._delete_many(self.model.id.in_(ids)) if ids else []

    async def delete_all(self, *where: Where, order: Order = None) -> Ids:
        """Удалить объекты по условию, вернуть список ID удалённых."""
        return await self._delete_many(*where, order=order)

    async def get_or_create(self, defaults: CreateSchema | None = None, **kwargs: object) -> Model:
        """Получить объект или создать новый."""
        # Строим условия поиска из kwargs
        conditions = []
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                conditions.append(getattr(self.model, key) == value)

        # Пытаемся найти существующий объект
        obj = await self.get_by(*conditions)
        if obj:
            return obj

        # Создаем новый объект
        create_data = defaults.model_dump() if defaults else {}

        # Добавляем kwargs в create_data
        for key, value in kwargs.items():
            if key not in create_data and hasattr(self.model, key):
                create_data[key] = value

        obj = self.model(**create_data)
        self.session.add(obj)
        return obj

    async def count(self, *where: Where) -> int:
        """Подсчитать количество объектов."""
        stmt = select(func.count()).select_from(self.model)
        stmt = self._apply(stmt, where=where)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def exists(self, id: Id) -> bool:
        """Проверить существование объекта по ID."""
        return await self._exists(self.model.id == id)

    async def exists_by(self, *where: Where) -> bool:
        """Проверить существование объекта по условию."""
        return await self._exists(*where)

    async def paginate(
        self,
        *where: Where,
        page: int = 1,
        size: int = 20,
        order: Order = None,
        relations: Rel = None,
    ) -> tuple[list[Model], int]:
        """Пагинация с подсчетом общего количества."""
        total = await self.count(*where)
        
        skip = (page - 1) * size
        stmt = select(self.model)
        stmt = self._apply(stmt, where=where, order=order, relations=relations)
        stmt = stmt.offset(skip).limit(size)
        
        result = await self.session.execute(stmt)
        items = result.unique().scalars().all()
        
        return items, total

    def _apply(self, stmt, where: tuple[Where, ...] = (), order: Order = None, relations: Rel = None):
        if where:
            stmt = stmt.where(*where)
        if order:
            stmt = stmt.order_by(*order)
        if relations:
            for relation in relations:
                stmt = stmt.options(selectinload(getattr(self.model, relation)))
        return stmt

    async def _get_one(self, *where: Where, order: Order = None, relations: Rel = None) -> Model | None:
        stmt = select(self.model)
        stmt = self._apply(stmt, where=where, order=order, relations=relations)
        stmt = stmt.limit(1)
        
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def _get_many(self, *where: Where, order: Order = None, relations: Rel = None) -> list[Model]:
        stmt = select(self.model)
        stmt = self._apply(stmt, where=where, order=order, relations=relations)
        
        result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def _update_one(self, data: UpdateSchema, *where: Where, partial: bool = True) -> Model | None:
        dump = data.model_dump(exclude_unset=partial)
        stmt = update(self.model).where(*where).values(**dump).returning(self.model)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def _update_many(self, data: UpdateSchema, *where: Where, partial: bool = True) -> list[Model]:
        dump = data.model_dump(exclude_unset=partial)
        stmt = update(self.model).where(*where).values(**dump).returning(self.model)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def _delete_one(self, *where: Where, order: Order = None) -> Id:
        stmt = delete(self.model)
        stmt = self._apply(stmt, where=where, order=order)
        stmt = stmt.returning(self.model.id)
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def _delete_many(self, *where: Where, order: Order = None) -> Ids:
        stmt = delete(self.model)
        stmt = self._apply(stmt, where=where, order=order)
        stmt = stmt.returning(self.model.id)
        
        result = await self.session.execute(stmt)
        return [row[0] for row in result.all()]

    async def _exists(self, *where: Where) -> bool:
        stmt = select(exists().where(*where))
        result = await self.session.execute(stmt)
        return result.scalar_one()

    # TODO: Для обратной совместимости (удалить после перехода)
    async def get_many_by(self, *where, order_by=None, relations=None, **_) -> list[Model]:
        return await self.get_all(*where, order=order_by, relations=relations)

    async def delete_many_by(self, *where: Where, order_by: Order = None) -> Ids:
        return await self.delete_all(*where, order=order_by)

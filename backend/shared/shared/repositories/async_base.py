# pyright: reportAttributeAccessIssue=false

from collections.abc import Sequence

from sqlalchemy import Delete, Select, Update, delete, exists, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import ColumnElement

Id = int | str
Ids = list[Id]

class BaseRepository[Model]:
    """Базовый асинхронный CRUD репозиторий для SQLAlchemy.

    Примечание:
        - Требуется commit для сохранения изменений
        - Возвращает None если объект не найден
    """

    def __init__(self, model: type[Model], session: AsyncSession) -> None:
        self.model = model
        self._session = session

    async def get(self, id: Id, relations: Sequence[str] | None = None) -> Model | None:
        """Получить объект по ID."""
        return await self._get_one(self.model.id == id, relations=relations)

    async def get_by(
        self,
        *where: ColumnElement[bool],
        order: Sequence[ColumnElement] | None = None,
        relations: Sequence[str] | None = None
    ) -> Model | None:
        """Получить объект по условию."""
        return await self._get_one(*where, order=order, relations=relations)

    async def get_all(
        self,
        *where: ColumnElement[bool],
        order: Sequence[ColumnElement] | None = None,
        relations: Sequence[str] | None = None
    ) -> list[Model]:
        """Получить список объектов по условию."""
        return await self._get_all(*where, order=order, relations=relations)

    async def get_all_by_ids(
        self,
        ids: Ids,
        order: Sequence[ColumnElement] | None = None,
        relations: Sequence[str] | None = None
    ) -> list[Model]:
        """Получить список объектов по списку ID."""
        return await self._get_all(self.model.id.in_(ids), order=order, relations=relations) if ids else []

    async def create(self, data: dict) -> Model:
        """Создать объект."""
        obj = self.model(**data)
        self._session.add(obj)
        return obj

    async def create_all(self, objects: Sequence[dict]) -> list[Model]:
        """Создать несколько объектов."""
        objs = [self.model(**obj) for obj in objects]
        self._session.add_all(objs)
        return objs

    async def update(self, id: Id, data: dict) -> Model | None:
        """Обновить объект по ID."""
        return await self._update_one(data, self.model.id == id)

    async def update_by(
        self,
        data: dict,
        *where: ColumnElement[bool],
        order: Sequence[ColumnElement] | None = None,
    ) -> Model | None:
        """Обновить объект по условию."""
        return await self._update_one(data, *where, order=order)

    async def update_all(
        self,
        data: dict,
        *where: ColumnElement[bool],
        order: Sequence[ColumnElement] | None = None,
    ) -> list[Model]:
        """Обновить несколько объектов по условию."""
        return await self._update_all(data, *where, order=order)

    async def update_all_by_ids(
        self,
        ids: Ids,
        data: dict,
        order: Sequence[ColumnElement] | None = None,
    ) -> list[Model]:
        """Обновить несколько объектов по списку ID."""
        return await self._update_all(data, self.model.id.in_(ids), order=order) if ids else []

    async def delete(self, id: Id) -> Id | None:
        """Удалить объект по ID."""
        return await self._delete_one(self.model.id == id)

    async def delete_by(
        self,
        *where: ColumnElement[bool],
        order: Sequence[ColumnElement] | None = None
    ) -> Id | None:
        """Удалить объект по условию."""
        return await self._delete_one(*where, order=order)

    async def delete_all(
        self,
        *where: ColumnElement[bool],
        order: Sequence[ColumnElement] | None = None
    ) -> Ids:
        """Удалить объекты по условию, вернуть список ID удалённых."""
        return await self._delete_all(*where, order=order)

    async def delete_all_by_ids(self, ids: Ids) -> Ids:
        """Удалить несколько объектов по списку ID, вернуть список ID удалённых."""
        return await self._delete_all(self.model.id.in_(ids)) if ids else []

    async def get_or_create(self, defaults: dict | None = None, **kwargs: object) -> Model:
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
        create_data = defaults.copy() if defaults else {}

        # Добавляем kwargs в create_data
        for key, value in kwargs.items():
            if key not in create_data and hasattr(self.model, key):
                create_data[key] = value

        obj = self.model(**create_data)
        self._session.add(obj)
        return obj

    async def count(self, *where: ColumnElement[bool]) -> int:
        """Подсчитать количество объектов."""
        stmt = select(func.count()).select_from(self.model)
        stmt = self._apply(stmt, where=where)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def exists(self, id: Id) -> bool:
        """Проверить существование объекта по ID."""
        return await self._exists(self.model.id == id)

    async def exists_by(self, *where: ColumnElement[bool]) -> bool:
        """Проверить существование объекта по условию."""
        return await self._exists(*where)

    async def paginate(
        self,
        *where: ColumnElement[bool],
        page: int = 1,
        size: int = 20,
        order: Sequence[ColumnElement] | None = None,
        relations: Sequence[str] | None = None,
    ) -> tuple[list[Model], int]:
        """Пагинация с подсчетом общего количества."""
        total = await self.count(*where)
        
        skip = (page - 1) * size
        stmt = select(self.model)
        stmt = self._apply(stmt, where=where, order=order, relations=relations)
        stmt = stmt.offset(skip).limit(size)
        
        result = await self._session.execute(stmt)
        items = list(result.unique().scalars().all())
        
        return items, total

    def _apply(
        self,
        stmt: Select | Update | Delete,
        where: tuple[ColumnElement[bool], ...] = (),
        order: Sequence[ColumnElement] | None = None,
        relations: Sequence[str] | None = None
    ) -> Select | Update | Delete:
        if where:
            stmt = stmt.where(*where)
        if order:
            stmt = stmt.order_by(*order)
        if relations:
            for relation in relations:
                stmt = stmt.options(selectinload(getattr(self.model, relation)))
        return stmt

    async def _get_one(
        self,
        *where: ColumnElement[bool],
        order: Sequence[ColumnElement] | None = None,
        relations: Sequence[str] | None = None,
    ) -> Model | None:
        stmt = select(self.model)
        stmt = self._apply(stmt, where=where, order=order, relations=relations)
        stmt = stmt.limit(1)
        
        result = await self._session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def _get_all(
        self,
        *where: ColumnElement[bool],
        order: Sequence[ColumnElement] | None = None,
        relations: Sequence[str] | None = None,
    ) -> list[Model]:
        stmt = select(self.model)
        stmt = self._apply(stmt, where=where, order=order, relations=relations)
        
        result = await self._session.execute(stmt)
        return list(result.unique().scalars().all())

    async def _update_one(
        self,
        data: dict,
        *where: ColumnElement[bool],
        order: Sequence[ColumnElement] | None = None,
    ) -> Model | None:
        stmt = update(self.model)
        stmt = self._apply(stmt, where=where, order=order)
        stmt = stmt.values(**data).returning(self.model)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def _update_all(
        self,
        data: dict,
        *where: ColumnElement[bool],
        order: Sequence[ColumnElement] | None = None,
    ) -> list[Model]:
        stmt = update(self.model)
        stmt = self._apply(stmt, where=where, order=order)
        stmt = stmt.values(**data).returning(self.model)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def _delete_one(
        self,
        *where: ColumnElement[bool],
        order: Sequence[ColumnElement] | None = None,
    ) -> Id | None:
        stmt = delete(self.model)
        stmt = self._apply(stmt, where=where, order=order)
        stmt = stmt.returning(self.model.id)
        
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def _delete_all(
        self,
        *where: ColumnElement[bool],
        order: Sequence[ColumnElement] | None = None,
    ) -> Ids:
        stmt = delete(self.model)
        stmt = self._apply(stmt, where=where, order=order)
        stmt = stmt.returning(self.model.id)
        
        result = await self._session.execute(stmt)
        return [row[0] for row in result.all()]

    async def _exists(self, *where: ColumnElement[bool]) -> bool:
        stmt = select(exists().where(*where))
        result = await self._session.execute(stmt)
        return result.scalar_one()

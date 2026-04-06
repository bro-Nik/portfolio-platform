# pyright: reportAttributeAccessIssue=false

from collections.abc import Sequence
from typing import TYPE_CHECKING

from pydantic import BaseModel
from sqlalchemy import delete, exists, select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import ColumnElement

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


Id = int | str
Ids = list[Id]
Rel = Sequence[str] | None
Order = Sequence[ColumnElement] | None
Where = ColumnElement[bool] | None


class BaseSyncRepository[Model, CreateSchema: BaseModel, UpdateSchema: BaseModel]:
    """Базовый синхронный CRUD репозиторий для SQLAlchemy.

    Примечание:
        - Требуется commit для сохранения изменений
        - Возвращает None если объект не найден
        - Поддерживает блокировки с with_for_update
    """

    def __init__(self, model: type[Model], session: 'Session') -> None:
        self.model = model
        self.session = session

    def get(self, id: Id, relations: Rel = None, for_update: bool = False) -> Model | None:
        """Получить объект по ID."""
        return self._get_one(self.model.id == id, relations=relations, for_update=for_update)

    def get_by(self, *where: Where, order: Order = None, relations: Rel = None, for_update: bool = False) -> Model | None:
        """Получить объект по условию."""
        return self._get_one(*where, order=order, relations=relations, for_update=for_update)

    def get_many(self, ids: Ids, relations: Rel = None, for_update: bool = False) -> list[Model]:
        """Получить список объектов по списку ID."""
        return self._get_many(self.model.id.in_(ids), relations=relations, for_update=for_update) if ids else []

    def get_all(self, *where: Where, order: Order = None, relations: Rel = None, for_update: bool = False) -> list[Model]:
        """Получить список объектов по условию."""
        return self._get_many(*where, order=order, relations=relations, for_update=for_update)

    def create(self, data: CreateSchema) -> Model:
        """Создать объект."""
        obj = self.model(**data.model_dump())
        self.session.add(obj)
        return obj

    def create_many(self, objects: list[CreateSchema]) -> list[Model]:
        """Создать несколько объектов."""
        objs = [self.model(**obj.model_dump()) for obj in objects]
        self.session.add_all(objs)
        return objs

    def update(self, id: Id, data: UpdateSchema, *, partial: bool = True) -> Model | None:
        """Обновить объект по ID."""
        return self._update_one(data, self.model.id == id, partial=partial)

    def update_by(self, data: UpdateSchema, *where: Where, partial: bool = True) -> Model | None:
        """Обновить объект по условию."""
        return self._update_one(data, *where, partial=partial)

    def update_many(self, ids: Ids, data: UpdateSchema, *, partial: bool = True) -> list[Model]:
        """Обновить несколько объектов по списку ID."""
        return self._update_many(data, self.model.id.in_(ids), partial=partial) if ids else []

    def update_all(self, data: UpdateSchema, *where: Where, partial: bool = True) -> list[Model]:
        """Обновить несколько объектов по условию."""
        return self._update_many(data, *where, partial=partial)

    def delete(self, id: Id) -> Id:
        """Удалить объект по ID."""
        return self._delete_one(self.model.id == id)

    def delete_by(self, *where: Where, order: Order = None) -> Id:
        """Удалить объект по условию."""
        return self._delete_one(*where, order=order)

    def delete_many(self, ids: Ids) -> Ids:
        """Удалить несколько объектов по списку ID, вернуть список ID удалённых."""
        return self._delete_many(self.model.id.in_(ids)) if ids else []

    def delete_all(self, *where: Where, order: Order = None) -> Ids:
        """Удалить объекты по условию, вернуть список ID удалённых."""
        return self._delete_many(*where, order=order)

    def count(self, *where: Where) -> int:
        """Подсчитать количество объектов."""
        stmt = select(func.count()).select_from(self.model)
        stmt = self._apply(stmt, where=where)
        result = self.session.execute(stmt)
        return result.scalar_one()

    def get_or_create(self, defaults: CreateSchema | None = None, for_update: bool = False, **kwargs: object) -> Model:
        """Получить объект или создать новый."""
        conditions = []
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                conditions.append(getattr(self.model, key) == value)

        obj = self.get_by(*conditions, for_update=for_update)
        if obj:
            return obj

        create_data = defaults.model_dump() if defaults else {}

        for key, value in kwargs.items():
            if key not in create_data and hasattr(self.model, key):
                create_data[key] = value

        obj = self.model(**create_data)
        self.session.add(obj)
        return obj

    def exists(self, id: Id) -> bool:
        """Проверить существование объекта по ID."""
        return self._exists(self.model.id == id)

    def exists_by(self, *where: Where) -> bool:
        """Проверить существование объекта по условию."""
        return self._exists(*where)

    def _apply(self, stmt, where: tuple[Where, ...] = (), order: Order = None, relations: Rel = None, for_update: bool = False):
        if where:
            stmt = stmt.where(*where)
        if order:
            stmt = stmt.order_by(*order)
        if for_update:
            stmt = stmt.with_for_update()
        if relations:
            for relation in relations:
                stmt = stmt.options(selectinload(getattr(self.model, relation)))
        return stmt

    def _get_one(self, *where: Where, order: Order = None, relations: Rel = None, for_update: bool = False) -> Model | None:
        stmt = select(self.model)
        stmt = self._apply(stmt, where=where, order=order, relations=relations, for_update=for_update)
        stmt = stmt.limit(1)
        
        result = self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    def _get_many(self, *where: Where, order: Order = None, relations: Rel = None, for_update: bool = False) -> list[Model]:
        stmt = select(self.model)
        stmt = self._apply(stmt, where=where, order=order, relations=relations, for_update=for_update)
        
        result = self.session.execute(stmt)
        return result.unique().scalars().all()

    def _update_one(self, data: UpdateSchema, *where: Where, partial: bool = True) -> Model | None:
        dump = data.model_dump(exclude_unset=partial)
        stmt = update(self.model).where(*where).values(**dump).returning(self.model).limit(1)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def _update_many(self, data: UpdateSchema, *where: Where, partial: bool = True) -> list[Model]:
        dump = data.model_dump(exclude_unset=partial)
        stmt = update(self.model).where(*where).values(**dump).returning(self.model)
        result = self.session.execute(stmt)
        return result.scalars().all()

    def _delete_one(self, *where: Where, order: Order = None) -> Id:
        stmt = delete(self.model)
        stmt = self._apply(stmt, where=where, order=order)
        stmt = stmt.limit(1).returning(self.model.id)
        
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def _delete_many(self, *where: Where, order: Order = None) -> Ids:
        stmt = delete(self.model)
        stmt = self._apply(stmt, where=where, order=order)
        stmt = stmt.returning(self.model.id)
        
        result = self.session.execute(stmt)
        return [row[0] for row in result.all()]

    def _exists(self, *where: Where) -> bool:
        stmt = select(exists().where(*where))
        result = self.session.execute(stmt)
        return result.scalar_one()

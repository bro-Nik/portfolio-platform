# ruff: noqa: A002
# pyright: reportAttributeAccessIssue=false

from collections.abc import Sequence
from typing import TYPE_CHECKING, TypeVar

from pydantic import BaseModel
from sqlalchemy import delete, exists, select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import expression, func

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


Id = TypeVar('Id', int, str)


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

    def get(self, id: Id, relations: tuple[str, ...] = (), for_update: bool = False) -> Model | None:
        """Получить объект по ID."""
        stmt = select(self.model).where(self.model.id == id)

        if for_update:
            stmt = stmt.with_for_update()

        for relation in relations:
            stmt = stmt.options(selectinload(getattr(self.model, relation)))

        result = self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    def get_by(
        self,
        *where: expression.ColumnElement[bool],
        order_by: Sequence[expression.ColumnElement] | None = None,
        relations: tuple[str, ...] = (),
        for_update: bool = False,
    ) -> Model | None:
        """Получить объект по условию."""
        stmt = select(self.model)

        if where:
            stmt = stmt.where(*where)

        if order_by:
            stmt = stmt.order_by(*order_by)

        if for_update:
            stmt = stmt.with_for_update()

        for relation in relations:
            stmt = stmt.options(selectinload(getattr(self.model, relation)))

        stmt = stmt.limit(1)
        result = self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    def get_many(
        self,
        ids: Sequence[Id],
        relations: tuple[str, ...] = (),
        for_update: bool = False,
    ) -> list[Model]:
        """Получить список объектов по списку ID."""
        if not ids:
            return []

        stmt = select(self.model).where(self.model.id.in_(ids))

        if for_update:
            stmt = stmt.with_for_update()

        for relation in relations:
            stmt = stmt.options(selectinload(getattr(self.model, relation)))

        result = self.session.execute(stmt)
        return result.unique().scalars().all()

    def get_many_by(
        self,
        *where: expression.ColumnElement[bool],
        order_by: Sequence[expression.ColumnElement] | None = None,
        skip: int = 0,
        limit: int | None = None,
        relations: tuple[str, ...] = (),
        for_update: bool = False,
    ) -> list[Model]:
        """Получить список объектов по условию."""
        stmt = select(self.model)

        if where:
            stmt = stmt.where(*where)

        if order_by:
            stmt = stmt.order_by(*order_by)

        if for_update:
            stmt = stmt.with_for_update()

        for relation in relations:
            stmt = stmt.options(selectinload(getattr(self.model, relation)))

        stmt = stmt.offset(skip)
        if limit:
            stmt = stmt.limit(limit)

        result = self.session.execute(stmt)
        return result.unique().scalars().all()

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

    def update(
        self,
        id: Id,
        data: UpdateSchema,
        *,
        exclude_unset: bool = True,
    ) -> Model | None:
        """Обновить объект."""
        update_data = data.model_dump(exclude_unset=exclude_unset)

        stmt = (
            update(self.model)
            .where(self.model.id == id)
            .values(**update_data)
            .returning(self.model)
        )

        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def update_many(
        self,
        ids: list[Id],
        data: UpdateSchema,
        *,
        exclude_unset: bool = True,
    ) -> list[Model]:
        """Обновить несколько объектов."""
        if not ids:
            return []

        update_data = data.model_dump(exclude_unset=exclude_unset)

        stmt = (
            update(self.model)
            .where(self.model.id.in_(ids))
            .values(**update_data)
            .returning(self.model)
        )

        result = self.session.execute(stmt)
        return result.scalars().all()

    def delete(self, id: Id) -> bool:
        """Удалить объект по ID."""
        stmt = delete(self.model).where(self.model.id == id).returning(self.model.id)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    def delete_by(
        self,
        *where: expression.ColumnElement[bool],
        order_by: Sequence[expression.ColumnElement] | None = None,
    ) -> bool:
        """Удалить объект по условию."""
        stmt = delete(self.model)

        if where:
            stmt = stmt.where(*where)

        if order_by:
            stmt = stmt.order_by(*order_by)

        stmt = stmt.limit(1).returning(self.model.id)

        result = self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    def delete_many(self, ids: Sequence[Id]) -> list[Id]:
        """Удалить несколько объектов по списку ID, вернуть список ID удалённых."""
        if not ids:
            return []

        stmt = delete(self.model).where(self.model.id.in_(ids)).returning(self.model.id)
        result = self.session.execute(stmt)
        return [row[0] for row in result.all()]

    def delete_many_by(
        self,
        *where: expression.ColumnElement[bool],
        order_by: Sequence[expression.ColumnElement] | None = None,
    ) -> list[Id]:
        """Удалить объекты по условию, вернуть список ID удалённых."""
        stmt = delete(self.model)

        if where:
            stmt = stmt.where(*where)

        if order_by:
            stmt = stmt.order_by(*order_by)

        stmt = stmt.returning(self.model.id)

        result = self.session.execute(stmt)
        return [row[0] for row in result.all()]

    def count(
        self,
        *where: expression.ColumnElement[bool],
    ) -> int:
        """Подсчитать количество объектов."""
        stmt = select(func.count()).select_from(self.model)

        if where:
            stmt = stmt.where(*where)

        result = self.session.execute(stmt)
        return result.scalar_one()

    def get_or_create(
        self,
        defaults: CreateSchema | None = None,
        for_update: bool = False,
        **kwargs: object,
    ) -> Model:
        """Получить объект или создать новый.

        Args:
            defaults: Данные для создания (если объект не найден)
            for_update: Блокировать запись для обновления
            **kwargs: Поля для поиска
        """
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
        stmt = select(exists().where(self.model.id == id))
        result = self.session.execute(stmt)
        return result.scalar_one()

    def exists_by(self, *where: expression.ColumnElement[bool]) -> bool:
        """Проверить существование объекта по условию."""
        stmt = select(exists().where(*where))
        result = self.session.execute(stmt)
        return result.scalar_one()

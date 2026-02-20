from typing import Dict, TypeVar, Generic, Type, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import BaseModel
# from sqlalchemy.orm import with_forupdate


ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def _apply_relationships(self, query, relationships: Optional[List[str]] = None):
        """Применяет загрузку связей"""
        if relationships:
            for relationship in relationships:
                if hasattr(self.model, relationship):
                    query = query.options(selectinload(getattr(self.model, relationship)))
        return query

    def _apply_filters(self, query, filters: Optional[Dict] = None):
        """Применяет фильтры с поддержкой разных операторов"""
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)
        return query

    def get(self, obj_id: int) -> Optional[ModelType]:
        result = self.db.execute(select(self.model).where(self.model.id == obj_id))
        return result.scalar_one_or_none()

    def get_with_forupdate(self, obj_id: int) -> Optional[ModelType]:
        result = self.db.execute(select(self.model).where(self.model.id == obj_id).with_for_update())
        return result.scalar_one_or_none()

    def get_by_name(self, obj_name: str) -> Optional[ModelType]:
        result = self.db.execute(select(self.model).where(self.model.name == obj_name))
        return result.scalar_one_or_none()

    def get_by_name_with_forupdate(self, obj_name: str) -> Optional[ModelType]:
        result = self.db.execute(select(self.model).where(self.model.name == obj_name).with_for_update())
        return result.scalar_one_or_none()

    def get_all(
        self,
        skip: int = 0,
        limit: Optional[int] = None,
        filters: Optional[Dict] = None,
        relationships: Optional[List[str]] = None
    ) -> List[ModelType]:
        """Получить все объекты с пагинацией и фильтрацией"""
        query = select(self.model)
        query = self._apply_filters(query, filters)
        query = self._apply_relationships(query, relationships)

        query = query.offset(skip)
        if limit:
            query = query.limit(limit)

        result = self.db.execute(query)
        return result.scalars().all()

    def create(self, obj_in: CreateSchemaType) -> ModelType:
        db_obj = self.model(**obj_in.dict())
        self.db.add(db_obj)
        return db_obj

    def delete(self, obj_id: int) -> Optional[ModelType]:
        result = self.db.execute(
            select(self.model).where(self.model.id == obj_id)
        )
        db_obj = result.scalar_one_or_none()

        if db_obj:
            self.db.delete(db_obj)
        return db_obj

    def update(self, obj_id: int, obj_in: UpdateSchemaType) -> Optional[ModelType]:
        db_obj = self.get(obj_id)
        if not db_obj:
            return None

        # Подготавливаем данные для обновления
        update_data = obj_in.dict(exclude_unset=True)

        # Обновляем поля
        for key, value in update_data.items():
            setattr(db_obj, key, value)

        return db_obj

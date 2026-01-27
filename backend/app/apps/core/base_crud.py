from abc import ABC, abstractmethod
from math import ceil
from typing import Any, Optional

from apps.core.base import Base
from apps.core.schemas import PaginationResponseSchema, SearchParamsSchema, SortEnum
from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import and_, asc, desc, func, or_, select, update
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute


class BaseCRUDManager(ABC):
    model: type[Base] = None

    @abstractmethod
    def __init__(self):
        pass

    async def create(self, *, session: AsyncSession, **kwargs) -> Optional[Base]:
        instance = self.model(**kwargs)
        session.add(instance)

        try:
            await session.commit()
            return instance
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

    async def get(
        self,
        *,
        session: AsyncSession,
        field: InstrumentedAttribute,
        field_value: Any,
    ) -> Optional[Base]:
        query = select(self.model).where(field == field_value)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def patch(
        self,
        instance_id: int,
        session: AsyncSession,
        data_to_patch: BaseModel,
        exclude_unset: bool = True,
    ) -> Base:
        query = (
            select(self.model)
            .filter(self.model.id == instance_id)
            .with_for_update(nowait=True)
        )
        try:
            result = await session.execute(query)
            item = result.scalar_one_or_none()
        except DBAPIError:
            raise HTTPException(
                detail="Row locked, try again later.",
                status_code=status.HTTP_423_LOCKED,
            )
        if not item:
            raise HTTPException(
                detail="Not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        data_for_updating: dict = data_to_patch.model_dump(
            exclude={"id"},
            exclude_unset=exclude_unset,
        )
        if not data_for_updating:
            return item
        query = (
            update(self.model)
            .where(self.model.id == instance_id)
            .values(**data_for_updating)
        )
        await session.execute(query)
        await session.commit()
        return item

    async def get_items_paginated(
        self,
        *,
        session: AsyncSession,
        params: SearchParamsSchema,
        targeted_schema: type[BaseModel],
        search_fields: list[InstrumentedAttribute] = None,
    ) -> PaginationResponseSchema:
        sort_direction = asc if params.sort_direction == SortEnum.ASC else desc
        query = select(self.model)
        count_query = select(func.count()).select_from(self.model)

        if params.q and search_fields:
            if params.use_sharp_filter:
                # Точный поиск: хотя бы одно поле должно быть в точности равно params.q (в нижнем регистре)
                search_field_condition = or_(
                    func.lower(search_field) == params.q
                    for search_field in search_fields
                )
            else:
                # Нечеткий поиск: разбиваем запрос на слова длиннее 1 символа
                words = [word for word in params.q.split() if len(word) > 1]
                # Условие: Для каждого поля поиска проверяем, содержит ли оно ВСЕ слова запроса.
                # Затем объединяем поля через OR.
                # (Field1 содержит Word1 И Word2) ИЛИ (Field2 содержит Word1 И Word2)
                search_field_condition = or_(
                    and_(*(search_field.icontains(word) for word in words))
                    for search_field in search_fields
                )
            query = query.filter(search_field_condition)
            count_query = count_query.filter(search_field_condition)

        sort_field = getattr(self.model, params.sort_by, self.model.id)
        query = query.order_by(sort_direction(sort_field))

        offset = (params.page - 1) * params.limit
        query = query.offset(offset).limit(params.limit)

        result = await session.execute(query)
        result_count = await session.execute(count_query)
        total_count: int = result_count.scalar()

        return PaginationResponseSchema(
            items=[targeted_schema.from_orm(item) for item in result.scalars().all()],
            total=total_count,
            page=params.page,
            limit=params.limit,
            pages=ceil(total_count / params.limit),
        )

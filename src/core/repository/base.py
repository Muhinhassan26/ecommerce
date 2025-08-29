from collections.abc import Sequence
from typing import Any, Generic

from pydantic import BaseModel
from sqlalchemy import JSON, Select, and_, cast, delete, func, or_, select, update
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import RelationshipProperty, joinedload, selectinload
from src.core.db import ModelType, operators_map
from src.core.schemas.common import FilterOptions


class BaseRepository(Generic[ModelType]):  # noqa: UP046
    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    def _get_query(
        self,
        prefetch: tuple[str, ...] | None = None,
        options: list[Any] | None = None,
    ) -> Select[tuple[ModelType]]:
        query = select(self.model)

        if prefetch:
            if options is None:
                options = []
            for relation in prefetch:
                attr = getattr(self.model, relation)

                if hasattr(attr, "property") and isinstance(attr.property, RelationshipProperty):
                    if attr.property.uselist:
                        options.append(selectinload(attr))
                    else:
                        options.append(joinedload(attr))
            query = query.options(*options).execution_options(populate_existing=True)

        return query

    def _build_sorting(self, sorting: dict[str, str]) -> list[Any]:
        """Build list of ORDER_BY clauses."""
        result = []
        for field_name, direction in sorting.items():
            field = getattr(self.model, field_name)
            result.append(getattr(field, direction)())
        return result

    def _build_filters(self, filters: dict[str, Any]) -> list[Any]:
        """Build list of WHERE conditions."""
        result = []
        for expression, value in filters.items():
            parts = expression.split("__")
            op_name = parts[1] if len(parts) > 1 else "exact"
            if op_name not in operators_map:
                msg = f"Expression {expression} has incorrect operator {op_name}"
                raise KeyError(msg)
            operator = operators_map[op_name]
            column = getattr(self.model, parts[0])

            if isinstance(column.type.python_type, type) and column.type.python_type is bool:  # noqa: SIM102
                if isinstance(value, str):
                    if value.lower() in ("1", "true", "t", "yes", "True"):
                        value = True
                    elif value.lower() in ("0", "false", "f", "no", "False"):
                        value = False
                    else:
                        value = None
            result.append(operator(column, value))
        return result

    async def get_by_id(
        self,
        obj_id: int,
        filter_options: FilterOptions | None = None,
    ) -> ModelType | None:
        query = self._get_query(prefetch=filter_options.prefetch).where(self.model.id == obj_id)  # type:ignore

        session = self.session
        result = await session.execute(query)
        return result.scalars().first()

    async def list_all(
        self,
        filter_options: FilterOptions,
    ) -> Sequence[ModelType]:
        query = self._get_query(filter_options.prefetch)

        if filter_options.sorting is not None:
            query = query.order_by(*self._build_sorting(sorting=filter_options.sorting))

        session = self.session
        result = await session.execute(query)
        return result.scalars().all()

    async def get_by_filed(
        self,
        filter_options: FilterOptions,
    ) -> ModelType | None:
        query = self._get_query(prefetch=filter_options.prefetch)

        if filter_options.distinct_on:
            query = query.distinct(getattr(self.model, filter_options.distinct_on))

        if filter_options.sorting is not None:
            query = query.order_by(*self._build_sorting(filter_options.sorting))

        or_conditions = []
        and_conditions = []

        filters = self._build_filters(filter_options.filters)

        for filter_expr in filters:
            if hasattr(filter_expr, "left") and hasattr(filter_expr.left, "key"):
                if (
                    filter_options.or_filters is not None
                    and filter_expr.left.key in filter_options.or_filters
                ):
                    or_conditions.append(filter_expr)
                else:
                    and_conditions.append(filter_expr)

        final_condition = None
        if and_conditions or or_conditions:
            combined_conditions = []
            if and_conditions:
                combined_conditions.append(and_(*and_conditions))
            if or_conditions:
                combined_conditions.append(or_(*or_conditions))
            final_condition = and_(*combined_conditions) if combined_conditions else None
        session = self.session
        db_execute = await session.execute(query.where(final_condition))  # type: ignore
        return db_execute.scalars().first()

    async def filter(
        self,
        filter_options: FilterOptions,  # same object you pass to get_field
    ) -> Sequence[ModelType]:
        session = self.session
        query = self._get_query(prefetch=filter_options.prefetch)

        if filter_options.distinct_on:
            query = query.distinct(getattr(self.model, filter_options.distinct_on))
        if filter_options.sorting is not None:
            query = query.order_by(*self._build_sorting(filter_options.sorting))

        filters = self._build_filters(filter_options.filters)

        or_conditions = []
        and_conditions = []

        for filter_expr in filters:
            if hasattr(filter_expr, "left") and hasattr(filter_expr.left, "key"):
                if (
                    filter_options.or_filters is not None
                    and filter_expr.left.key in filter_options.or_filters
                ):
                    or_conditions.append(filter_expr)
                else:
                    and_conditions.append(filter_expr)
        final_condition = None
        if and_conditions or or_conditions:
            combined_conditions = []
            if and_conditions:
                combined_conditions.append(and_(*and_conditions))
            if or_conditions:
                combined_conditions.append(or_(*or_conditions))
            final_condition = and_(*combined_conditions) if combined_conditions else None

        if final_condition is not None:
            query = query.where(final_condition)

        result = await session.execute(query)
        return result.scalars().all()

    async def paginate_filters(
        self,
        filter_options: FilterOptions,
    ) -> tuple[Sequence[ModelType], int]:
        query = self._get_query(prefetch=filter_options.prefetch)

        if filter_options.sorting is not None:
            query = query.order_by(*self._build_sorting(filter_options.sorting))

        filters = self._build_filters(filter_options.filters)

        or_conditions = []
        and_conditions = []
        search_conditions = []

        search_fields = filter_options.search_fields

        if filter_options.pagination and filter_options.pagination.search and search_fields:
            search_value = filter_options.pagination.search.strip()
            for field in search_fields:
                search_conditions.append(getattr(self.model, field).ilike(f"%{search_value}%"))

        for filter_expr in filters:
            if hasattr(filter_expr, "left") and hasattr(filter_expr.left, "key"):
                if (
                    filter_options.or_filters is not None
                    and filter_expr.left.key in filter_options.or_filters
                ):
                    or_conditions.append(filter_expr)
                else:
                    and_conditions.append(filter_expr)

        final_condition = None
        if and_conditions or or_conditions or search_conditions:
            combined_conditions = []
            if and_conditions:
                combined_conditions.append(and_(*and_conditions))
            if or_conditions:
                combined_conditions.append(or_(*or_conditions))
            if search_conditions:
                combined_conditions.append(or_(*search_conditions))

            final_condition = and_(*combined_conditions) if combined_conditions else None

        session = self.session
        total_query = select(func.count()).select_from(self.model)
        if final_condition is not None:
            total_query = total_query.where(final_condition)
        total = await session.scalar(total_query) or 0

        if filter_options.pagination:
            query = query.offset(filter_options.pagination.skip).limit(
                filter_options.pagination.page_size
            )

        if final_condition is not None:
            query = query.where(final_condition)
        db_execute = await session.execute(query)
        result = db_execute.scalars().all()

        return result, total

    async def create(self, obj: ModelType) -> ModelType:
        session = self.session
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj

    async def update_obj(
        self, where: dict[str, Any], values: dict[str, Any]
    ) -> tuple[ModelType, int] | None:
        session = self.session
        filters = self._build_filters(where)

        # Convert column names to strings for `values`
        update_values = {}
        for key, value in values.items():
            if isinstance(value, dict) and isinstance(getattr(self.model, key).type, JSON):
                update_values[key] = cast(getattr(self.model, key), JSONB).concat(
                    cast(value, JSONB)
                )
            else:
                update_values[key] = value

        query = update(self.model).where(and_(True, *filters)).values(**update_values)
        result = await session.execute(query)
        await session.commit()
        row = result.scalars().one_or_none()  # list of updated model instances
        rowcount = result.rowcount
        return row, rowcount

    async def create_and_update(
        self,
        filter_options: FilterOptions,
        values: BaseModel,
    ) -> ModelType:
        session = self.session
        filters = self._build_filters(filter_options.filters)
        update_values = values.model_dump(exclude_unset=True)

        for key, value in list(update_values.items()):
            if isinstance(value, dict) and isinstance(getattr(self.model, key).type, JSON):
                update_values[key] = cast(getattr(self.model, key), JSON).concat(cast(value, JSON))

        query = select(self.model).where(and_(*filters))
        existing_obj = await session.execute(query)
        existing_obj = existing_obj.scalars().first()  # type:ignore

        if existing_obj:
            for key, value in update_values.items():
                setattr(existing_obj, key, value)
            session.add(existing_obj)
            await session.commit()
            await session.refresh(existing_obj)
            return existing_obj  # type:ignore

        new_obj = self.model(**update_values)
        session.add(new_obj)
        await session.commit()
        await session.refresh(new_obj)
        return new_obj

    async def delete(self, filter_options: FilterOptions) -> int:
        session = self.session
        filters = self._build_filters(filter_options.filters)

        query = delete(self.model).where(and_(*filters))
        result = await session.execute(query)
        await session.commit()

        return result.rowcount  # Number of rows deleted

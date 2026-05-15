from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.models.department import Department


class DepartmentCRUD:

    @staticmethod
    async def create(
        session: AsyncSession,
        data: dict,
    ) -> Department:

        department = Department(**data)

        session.add(department)

        await session.flush()
        await session.refresh(department)

        return department

    @staticmethod
    async def get_by_id(
        session: AsyncSession,
        department_id: int,
    ) -> Department | None:

        query = (
            select(Department)
            .where(Department.id == department_id)
        )

        result = await session.execute(query)

        return result.scalar_one_or_none()

    @staticmethod
    async def get_with_relations(
        session: AsyncSession,
        department_id: int,
    ) -> Department | None:

        query = (
            select(Department)
            .where(Department.id == department_id)
            .options(
                selectinload(Department.employees),
                selectinload(Department.children),
            )
        )

        result = await session.execute(query)

        return result.scalar_one_or_none()

    @staticmethod
    async def update(
        session: AsyncSession,
        department: Department,
        data: dict,
    ) -> Department:

        for key, value in data.items():
            setattr(department, key, value)

        await session.flush()
        await session.refresh(department)

        return department

    @staticmethod
    async def delete(
        session: AsyncSession,
        department: Department,
    ) -> None:

        await session.delete(department)
        await session.flush()
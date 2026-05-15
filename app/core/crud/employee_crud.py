from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.employee import Employee


class EmployeeCRUD:

    @staticmethod
    async def create(
        session: AsyncSession,
        data: dict,
    ) -> Employee:

        employee = Employee(**data)

        session.add(employee)

        await session.flush()
        await session.refresh(employee)

        return employee

    @staticmethod
    async def get_by_department(
        session: AsyncSession,
        department_id: int,
    ) -> list[Employee]:

        query = (
            select(Employee)
            .where(Employee.department_id == department_id)
            .order_by(Employee.full_name)
        )

        result = await session.execute(query)

        return list(result.scalars().all())
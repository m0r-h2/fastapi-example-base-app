from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.crud.department_crud import DepartmentCRUD
from app.core.crud.employee_crud import EmployeeCRUD
from app.core.enums import DepartmentDeleteMode
from app.core.models.department import Department
from app.core.models.employee import Employee
from app.core.schemas.department import (
    DepartmentResponse,
    DepartmentTreeNode,
    EmployeeBriefResponse,
)


class DepartmentService:
    @staticmethod
    def normalize_name(name: str) -> str:
        return name.strip()

    @staticmethod
    async def validate_unique_name(
        session: AsyncSession,
        name: str,
        parent_id: int | None,
        exclude_id: int | None = None,
    ) -> None:
        query = select(Department).where(
            Department.name == name,
            Department.parent_id == parent_id,
        )

        if exclude_id is not None:
            query = query.where(Department.id != exclude_id)

        result = await session.execute(query)
        existing = result.scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=409,
                detail="Department name already exists",
            )

    @staticmethod
    async def ensure_parent_exists(
        session: AsyncSession,
        parent_id: int | None,
    ) -> None:
        if parent_id is None:
            return

        parent = await DepartmentCRUD.get_by_id(session, parent_id)
        if parent is None:
            raise HTTPException(
                status_code=404,
                detail="Parent department not found",
            )

    @staticmethod
    async def create_department(
        session: AsyncSession,
        name: str,
        parent_id: int | None,
    ) -> Department:
        name = DepartmentService.normalize_name(name)

        await DepartmentService.ensure_parent_exists(session, parent_id)
        await DepartmentService.validate_unique_name(
            session=session,
            name=name,
            parent_id=parent_id,
        )

        department = await DepartmentCRUD.create(
            session=session,
            data={
                "name": name,
                "parent_id": parent_id,
            },
        )

        await session.commit()
        return department

    @staticmethod
    async def create_employee(
        session: AsyncSession,
        department_id: int,
        data: dict,
    ) -> Employee:
        department = await DepartmentCRUD.get_by_id(session, department_id)

        if department is None:
            raise HTTPException(
                status_code=404,
                detail="Department not found",
            )

        employee = await EmployeeCRUD.create(
            session=session,
            data={
                **data,
                "department_id": department_id,
            },
        )

        await session.commit()
        return employee

    @staticmethod
    async def check_cycle(
        session: AsyncSession,
        department_id: int,
        parent_id: int | None,
    ) -> None:
        if parent_id is None:
            return

        if department_id == parent_id:
            raise HTTPException(
                status_code=409,
                detail="Department cannot be parent of itself",
            )

        current = await DepartmentCRUD.get_by_id(session, parent_id)
        if current is None:
            raise HTTPException(
                status_code=404,
                detail="Parent department not found",
            )

        while current is not None:
            if current.id == department_id:
                raise HTTPException(
                    status_code=409,
                    detail="Cycle detected",
                )

            if current.parent_id is None:
                break

            current = await DepartmentCRUD.get_by_id(session, current.parent_id)
            if current is None:
                raise HTTPException(
                    status_code=404,
                    detail="Parent department not found",
                )

    @staticmethod
    async def update_department(
        session: AsyncSession,
        department_id: int,
        data: dict,
    ) -> Department:
        department = await DepartmentCRUD.get_by_id(session, department_id)

        if department is None:
            raise HTTPException(
                status_code=404,
                detail="Department not found",
            )

        if "name" in data and data["name"] is not None:
            data["name"] = DepartmentService.normalize_name(data["name"])
            await DepartmentService.validate_unique_name(
                session=session,
                name=data["name"],
                parent_id=data.get("parent_id", department.parent_id),
                exclude_id=department.id,
            )

        if "parent_id" in data:
            await DepartmentService.ensure_parent_exists(
                session,
                data["parent_id"],
            )
            await DepartmentService.check_cycle(
                session=session,
                department_id=department.id,
                parent_id=data["parent_id"],
            )

        department = await DepartmentCRUD.update(
            session=session,
            department=department,
            data=data,
        )

        await session.commit()
        return department

    @staticmethod
    async def build_tree(
        session: AsyncSession,
        department: Department,
        depth: int,
        include_employees: bool,
    ) -> DepartmentTreeNode:
        relations = ["children"] if depth > 0 else []
        if include_employees:
            relations.append("employees")

        if relations:
            await session.refresh(department, relations)

        employees = (
            sorted(department.employees, key=lambda employee: employee.full_name)
            if include_employees
            else []
        )

        children: list[DepartmentTreeNode] = []
        if depth > 0:
            for child in department.children:
                children.append(
                    await DepartmentService.build_tree(
                        session=session,
                        department=child,
                        depth=depth - 1,
                        include_employees=include_employees,
                    )
                )

        return DepartmentTreeNode(
            department=DepartmentResponse.model_validate(department),
            employees=[
                EmployeeBriefResponse.model_validate(employee)
                for employee in employees
            ],
            children=children,
        )

    @staticmethod
    async def get_department_tree(
        session: AsyncSession,
        department_id: int,
        depth: int,
        include_employees: bool,
    ) -> DepartmentTreeNode:
        depth = min(depth, 5)

        department = await DepartmentCRUD.get_by_id(session, department_id)
        if department is None:
            raise HTTPException(
                status_code=404,
                detail="Department not found",
            )

        return await DepartmentService.build_tree(
            session=session,
            department=department,
            depth=depth,
            include_employees=include_employees,
        )

    @staticmethod
    def _parse_delete_mode(mode: str) -> DepartmentDeleteMode:
        try:
            return DepartmentDeleteMode(mode)
        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail="Invalid delete mode",
            ) from exc

    @staticmethod
    async def delete_department(
        session: AsyncSession,
        department_id: int,
        mode: str,
        reassign_to_department_id: int | None = None,
    ) -> None:
        delete_mode = DepartmentService._parse_delete_mode(mode)

        department = await DepartmentCRUD.get_with_relations(session, department_id)

        if department is None:
            raise HTTPException(
                status_code=404,
                detail="Department not found",
            )

        if delete_mode == DepartmentDeleteMode.CASCADE:
            await DepartmentCRUD.delete(session, department)
            await session.commit()
            return

        if delete_mode == DepartmentDeleteMode.REASSIGN:
            if reassign_to_department_id is None:
                raise HTTPException(
                    status_code=400,
                    detail="reassign_to_department_id required",
                )

            if reassign_to_department_id == department_id:
                raise HTTPException(
                    status_code=400,
                    detail="Cannot reassign employees to the same department",
                )

            target_department = await DepartmentCRUD.get_by_id(
                session,
                reassign_to_department_id,
            )
            if target_department is None:
                raise HTTPException(
                    status_code=404,
                    detail="Target department not found",
                )

            for employee in department.employees:
                employee.department_id = reassign_to_department_id

            await DepartmentCRUD.delete(session, department)
            await session.commit()
            return

        raise HTTPException(
            status_code=400,
            detail="Invalid delete mode",
        )

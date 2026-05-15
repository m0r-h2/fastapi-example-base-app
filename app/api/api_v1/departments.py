from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.models import db_helper
from app.core.schemas.department import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentTreeNode,
    DepartmentUpdate,
)
from app.core.schemas.employee import EmployeeCreate, EmployeeResponse
from app.core.services.department_service import DepartmentService

router = APIRouter(
    prefix=settings.api.v1.departments,
    tags=["departments"],
)


@router.post(
    "/",
    response_model=DepartmentResponse,
    status_code=status.HTTP_200_OK,
)
async def create_department(
    body: DepartmentCreate,
    session: AsyncSession = Depends(db_helper.session_getter),
) -> DepartmentResponse:
    department = await DepartmentService.create_department(
        session=session,
        name=body.name,
        parent_id=body.parent_id,
    )
    return DepartmentResponse.model_validate(department)


@router.post(
    "/{department_id}/employees/",
    response_model=EmployeeResponse,
    status_code=status.HTTP_200_OK,
)
async def create_employee(
    department_id: int,
    body: EmployeeCreate,
    session: AsyncSession = Depends(db_helper.session_getter),
) -> EmployeeResponse:
    employee = await DepartmentService.create_employee(
        session=session,
        department_id=department_id,
        data=body.model_dump(),
    )
    return EmployeeResponse.model_validate(employee)


@router.get(
    "/{department_id}",
    response_model=DepartmentTreeNode,
)
async def get_department(
    department_id: int,
    depth: int = Query(default=1, ge=1, le=5),
    include_employees: bool = Query(default=True),
    session: AsyncSession = Depends(db_helper.session_getter),
) -> DepartmentTreeNode:
    return await DepartmentService.get_department_tree(
        session=session,
        department_id=department_id,
        depth=depth,
        include_employees=include_employees,
    )


@router.patch(
    "/{department_id}",
    response_model=DepartmentResponse,
)
async def update_department(
    department_id: int,
    body: DepartmentUpdate,
    session: AsyncSession = Depends(db_helper.session_getter),
) -> DepartmentResponse:
    department = await DepartmentService.update_department(
        session=session,
        department_id=department_id,
        data=body.model_dump(exclude_unset=True),
    )
    return DepartmentResponse.model_validate(department)


@router.delete(
    "/{department_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_department(
    department_id: int,
    mode: str,
    reassign_to_department_id: int | None = None,
    session: AsyncSession = Depends(db_helper.session_getter),
) -> Response:
    await DepartmentService.delete_department(
        session=session,
        department_id=department_id,
        mode=mode,
        reassign_to_department_id=reassign_to_department_id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)

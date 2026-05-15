from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class DepartmentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    parent_id: int | None = None


class DepartmentUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )
    parent_id: int | None = None


class DepartmentResponse(BaseModel):
    id: int
    name: str
    parent_id: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EmployeeBriefResponse(BaseModel):
    id: int
    department_id: int
    full_name: str
    position: str
    hired_at: date | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DepartmentTreeNode(BaseModel):
    department: DepartmentResponse
    employees: list[EmployeeBriefResponse] = Field(default_factory=list)
    children: list["DepartmentTreeNode"] = Field(default_factory=list)


DepartmentTreeNode.model_rebuild()

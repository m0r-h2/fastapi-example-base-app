from typing import TYPE_CHECKING

from sqlalchemy.orm import declared_attr, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

if TYPE_CHECKING:
    from app.core.models.department import Department


class DepartmentRelationMixin:
    _department_id_unique: bool = False
    _department_back_populates: str | None = None
    _department_nullable: bool = False
    _department_back_ondelete: str | None = None

    @declared_attr
    def department_id(cls) -> Mapped[int]:
        return mapped_column(
            ForeignKey(
            "departments.id",
            ondelete=cls._department_back_ondelete,
            ),
            unique=cls._department_id_unique,
            nullable=cls._department_nullable,
        )

    @declared_attr
    def department(cls) -> Mapped["Department"]:
        return relationship(
            "Department",
            back_populates=cls._department_back_populates
        )
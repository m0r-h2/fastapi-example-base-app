from sqlalchemy import ForeignKey
from sqlalchemy.orm import (
    declared_attr,
    relationship,
    mapped_column,
    Mapped
)


class ParentDepartmentMixin:
    _parent_back_populates: str | None = None
    _children_back_populates: str | None = None
    _parent_ondelete: str | None = None

    @declared_attr
    def parent_id(cls) -> Mapped[int | None]:
        return mapped_column(
            ForeignKey(
                "departments.id",
                ondelete=cls._parent_ondelete
            ),
            nullable=True
        )

    @declared_attr
    def parent(cls):
        return relationship(
            "Department",
            remote_side="Department.id",
            back_populates=cls._parent_back_populates,
        )
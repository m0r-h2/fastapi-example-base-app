from datetime import datetime, timezone

from typing import TYPE_CHECKING
from sqlalchemy import String, DateTime, func, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models import Base
from app.core.models.mixins import IntIdPkMixin, ParentDepartmentMixin

if TYPE_CHECKING:
    from .employee import Employee


class Department(
    ParentDepartmentMixin,
    IntIdPkMixin,
    Base,
):
    _parent_back_populates = "children"

    __table_args__ = (
        UniqueConstraint(
            "parent_id",
            "name",
            name="uq_department_parent_name"
        ),

        CheckConstraint(
            "parent_id IS NULL OR parent_id != id",
            name="check_department_not_self_parent"
        ),
    )

    _parent_ondelete = "CASCADE"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now()
    )

    employees: Mapped[list["Employee"]] = relationship(
        "Employee",
        back_populates="department",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    children: Mapped[list["Department"]] = relationship(
        "Department",
        back_populates="parent",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

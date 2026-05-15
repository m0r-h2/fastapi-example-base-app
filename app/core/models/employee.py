from datetime import timezone, date, datetime

from typing import Optional
from sqlalchemy import String, Date ,func, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.models import Base
from app.core.models.mixins import IntIdPkMixin, DepartmentRelationMixin



class Employee(DepartmentRelationMixin, IntIdPkMixin, Base):
    _department_back_populates = "employees"
    _department_back_ondelete = "CASCADE"

    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    position: Mapped[str] = mapped_column(String(255), nullable=False)
    hired_at: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now()
    )


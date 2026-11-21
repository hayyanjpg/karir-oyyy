from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.status_history import StatusHistory
    from app.models.user import User

_STATUS_VALUES = (
    "Applied",
    "Screening",
    "Technical Test",
    "HR Interview",
    "User Interview",
    "Offering",
    "Rejected",
    "Ghosted",
)
_PORTAL_VALUES = (
    "LinkedIn",
    "Glints",
    "JobStreet",
    "Kalibrr",
    "Website Perusahaan",
    "Lainnya",
)


def _quoted(values: tuple[str, ...]) -> str:
    return ", ".join(f"'{value}'" for value in values)


class JobApplication(Base):
    __tablename__ = "job_applications"
    __table_args__ = (
        CheckConstraint("work_model IN ('WFO', 'Hybrid', 'Remote')", name="chk_work_model"),
        CheckConstraint(f"status IN ({_quoted(_STATUS_VALUES)})", name="chk_status"),
        CheckConstraint(f"job_portal IN ({_quoted(_PORTAL_VALUES)})", name="chk_job_portal"),
        Index("ix_job_applications_user_applied", "user_id", "applied_date"),
        Index("ix_job_applications_user_status", "user_id", "status"),
        Index("ix_job_applications_user_work_model", "user_id", "work_model"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    company_name: Mapped[str] = mapped_column(String(150), nullable=False)
    position_title: Mapped[str] = mapped_column(String(150), nullable=False)
    job_portal: Mapped[str] = mapped_column(
        String(100), nullable=False, server_default=text("'Lainnya'")
    )
    work_model: Mapped[str] = mapped_column(
        String(50), nullable=False, server_default=text("'WFO'")
    )
    salary_range: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, server_default=text("'Applied'")
    )
    applied_date: Mapped[date] = mapped_column(Date, nullable=False)
    job_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    user: Mapped[User] = relationship(back_populates="applications")
    history: Mapped[list[StatusHistory]] = relationship(
        back_populates="application",
        cascade="all, delete-orphan",
        order_by="StatusHistory.changed_at",
    )

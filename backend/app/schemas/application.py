from __future__ import annotations

from datetime import UTC, date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator, model_validator

from app.core.enums import (
    FOLLOW_UP_DAYS,
    FOLLOW_UP_STAGES,
    ApplicationStatus,
    JobPortal,
    WorkModel,
)


class ApplicationFields(BaseModel):
    company_name: str = Field(min_length=1, max_length=150)
    position_title: str = Field(min_length=1, max_length=150)
    status: ApplicationStatus = ApplicationStatus.APPLIED
    applied_date: date
    job_portal: JobPortal = JobPortal.OTHER
    work_model: WorkModel = WorkModel.WFO
    salary_range: str | None = Field(default=None, max_length=100)
    job_url: str | None = Field(default=None, max_length=2048)
    notes: str | None = Field(default=None, max_length=5000)


class ApplicationCreate(ApplicationFields):
    @field_validator("company_name", "position_title")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value

    @field_validator("job_url")
    @classmethod
    def validate_job_url(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            return None
        if not value.startswith(("http://", "https://")):
            raise ValueError("job_url must start with http:// or https://")
        return value


class ApplicationUpdate(BaseModel):
    company_name: str | None = Field(default=None, min_length=1, max_length=150)
    position_title: str | None = Field(default=None, min_length=1, max_length=150)
    status: ApplicationStatus | None = None
    applied_date: date | None = None
    job_portal: JobPortal | None = None
    work_model: WorkModel | None = None
    salary_range: str | None = Field(default=None, max_length=100)
    job_url: str | None = Field(default=None, max_length=2048)
    notes: str | None = Field(default=None, max_length=5000)

    @field_validator("company_name", "position_title")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value

    @field_validator("job_url")
    @classmethod
    def validate_job_url(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            return None
        if not value.startswith(("http://", "https://")):
            raise ValueError("job_url must start with http:// or https://")
        return value

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> ApplicationUpdate:
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        for field in (
            "company_name",
            "position_title",
            "status",
            "applied_date",
            "job_portal",
            "work_model",
        ):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class ApplicationRead(ApplicationFields):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def days_since_update(self) -> int:
        updated_at = self.updated_at
        if updated_at.tzinfo is None:
            updated_at = updated_at.replace(tzinfo=UTC)
        return max((datetime.now(UTC) - updated_at).days, 0)

    @computed_field
    @property
    def needs_follow_up(self) -> bool:
        return self.status in FOLLOW_UP_STAGES and self.days_since_update > FOLLOW_UP_DAYS


class ApplicationPage(BaseModel):
    items: list[ApplicationRead]
    total: int
    page: int
    page_size: int
    pages: int

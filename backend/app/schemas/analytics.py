from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.core.enums import ApplicationStatus, JobPortal


class KpiSummary(BaseModel):
    total: int
    active_pipeline: int
    interview_count: int
    interview_rate: float
    offerings: int
    rejected: int
    ghosted: int


class StatusCount(BaseModel):
    status: ApplicationStatus
    count: int


class PortalCount(BaseModel):
    portal: JobPortal
    count: int


class FollowUpItem(BaseModel):
    id: UUID
    company_name: str
    position_title: str
    status: ApplicationStatus
    updated_at: datetime
    days_since_update: int


class AnalyticsSummary(BaseModel):
    kpi: KpiSummary
    by_status: list[StatusCount]
    by_portal: list[PortalCount]
    follow_up: list[FollowUpItem]

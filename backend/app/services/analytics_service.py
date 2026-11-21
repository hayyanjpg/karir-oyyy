from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import (
    ACTIVE_PIPELINE_EXCLUDED,
    FOLLOW_UP_DAYS,
    FOLLOW_UP_STAGES,
    INTERVIEW_STAGES,
    ApplicationStatus,
    JobPortal,
)
from app.models import JobApplication, StatusHistory
from app.schemas.analytics import (
    AnalyticsSummary,
    FollowUpItem,
    KpiSummary,
    PortalCount,
    StatusCount,
)


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=UTC)


async def get_analytics_summary(db: AsyncSession, user_id: UUID) -> AnalyticsSummary:
    total = int(
        await db.scalar(
            select(func.count(JobApplication.id)).where(JobApplication.user_id == user_id)
        )
        or 0
    )

    status_rows = await db.execute(
        select(JobApplication.status, func.count(JobApplication.id))
        .where(JobApplication.user_id == user_id)
        .group_by(JobApplication.status)
    )
    status_counts = {row[0]: int(row[1]) for row in status_rows}

    portal_rows = await db.execute(
        select(JobApplication.job_portal, func.count(JobApplication.id))
        .where(JobApplication.user_id == user_id)
        .group_by(JobApplication.job_portal)
    )
    portal_counts = {row[0]: int(row[1]) for row in portal_rows}

    interview_count = int(
        await db.scalar(
            select(func.count(distinct(StatusHistory.application_id))).where(
                StatusHistory.user_id == user_id,
                StatusHistory.to_status.in_([stage.value for stage in INTERVIEW_STAGES]),
            )
        )
        or 0
    )

    active_pipeline = int(
        await db.scalar(
            select(func.count(JobApplication.id)).where(
                JobApplication.user_id == user_id,
                JobApplication.status.notin_([stage.value for stage in ACTIVE_PIPELINE_EXCLUDED]),
            )
        )
        or 0
    )

    threshold = datetime.now(UTC) - timedelta(days=FOLLOW_UP_DAYS)
    follow_up_rows = await db.execute(
        select(JobApplication)
        .where(
            JobApplication.user_id == user_id,
            JobApplication.status.in_([stage.value for stage in FOLLOW_UP_STAGES]),
            JobApplication.updated_at < threshold,
        )
        .order_by(JobApplication.updated_at.asc())
        .limit(50)
    )
    follow_up = [
        FollowUpItem(
            id=application.id,
            company_name=application.company_name,
            position_title=application.position_title,
            status=ApplicationStatus(application.status),
            updated_at=application.updated_at,
            days_since_update=max((datetime.now(UTC) - _aware(application.updated_at)).days, 0),
        )
        for application in follow_up_rows.scalars().all()
    ]

    interview_rate = round((interview_count / total) * 100, 1) if total else 0.0

    return AnalyticsSummary(
        kpi=KpiSummary(
            total=total,
            active_pipeline=active_pipeline,
            interview_count=interview_count,
            interview_rate=interview_rate,
            offerings=status_counts.get(ApplicationStatus.OFFERING.value, 0),
            rejected=status_counts.get(ApplicationStatus.REJECTED.value, 0),
            ghosted=status_counts.get(ApplicationStatus.GHOSTED.value, 0),
        ),
        by_status=[
            StatusCount(status=status, count=status_counts.get(status.value, 0))
            for status in ApplicationStatus
        ],
        by_portal=[
            PortalCount(portal=portal, count=portal_counts.get(portal.value, 0))
            for portal in JobPortal
        ],
        follow_up=follow_up,
    )

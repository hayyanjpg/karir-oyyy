from uuid import UUID

from fastapi import HTTPException
from fastapi import status as http_status
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import ApplicationFilters, apply_application_filters
from app.models import JobApplication, StatusHistory
from app.schemas.application import ApplicationCreate, ApplicationUpdate

_ENUM_FIELDS = {"status", "work_model", "job_portal"}


def _normalise_enum_values(data: dict) -> dict:
    for field in _ENUM_FIELDS:
        value = data.get(field)
        if value is not None:
            data[field] = str(value)
    return data


async def list_applications(
    db: AsyncSession,
    user_id: UUID,
    filters: ApplicationFilters,
    page: int,
    page_size: int,
    sort: str,
    order: str,
) -> tuple[list[JobApplication], int]:
    base_stmt: Select = select(JobApplication).where(JobApplication.user_id == user_id)
    base_stmt = apply_application_filters(base_stmt, filters)

    count_stmt = select(func.count(JobApplication.id)).where(JobApplication.user_id == user_id)
    count_stmt = apply_application_filters(count_stmt, filters)
    total = int(await db.scalar(count_stmt) or 0)

    sort_columns = {
        "applied_date": JobApplication.applied_date,
        "created_at": JobApplication.created_at,
        "updated_at": JobApplication.updated_at,
        "company_name": JobApplication.company_name,
    }
    sort_column = sort_columns.get(sort, JobApplication.applied_date)
    ordering = sort_column.asc() if order == "asc" else sort_column.desc()

    stmt = (
        base_stmt.order_by(ordering, JobApplication.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def get_application(
    db: AsyncSession, user_id: UUID, application_id: UUID
) -> JobApplication | None:
    result = await db.execute(
        select(JobApplication).where(
            JobApplication.id == application_id,
            JobApplication.user_id == user_id,
        )
    )
    return result.scalar_one_or_none()


async def get_application_or_404(
    db: AsyncSession, user_id: UUID, application_id: UUID
) -> JobApplication:
    application = await get_application(db, user_id, application_id)
    if application is None:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )
    return application


async def create_application(
    db: AsyncSession, user_id: UUID, payload: ApplicationCreate
) -> JobApplication:
    data = _normalise_enum_values(payload.model_dump())
    application = JobApplication(user_id=user_id, **data)
    db.add(application)
    await db.flush()
    db.add(
        StatusHistory(
            application_id=application.id,
            user_id=user_id,
            from_status=None,
            to_status=application.status,
        )
    )
    await db.commit()
    await db.refresh(application)
    return application


async def update_application(
    db: AsyncSession, user_id: UUID, application_id: UUID, payload: ApplicationUpdate
) -> JobApplication:
    application = await get_application_or_404(db, user_id, application_id)
    data = _normalise_enum_values(payload.model_dump(exclude_unset=True))

    new_status = data.get("status")
    if new_status is not None and new_status != application.status:
        db.add(
            StatusHistory(
                application_id=application.id,
                user_id=user_id,
                from_status=application.status,
                to_status=new_status,
            )
        )

    for field, value in data.items():
        setattr(application, field, value)

    await db.commit()
    await db.refresh(application)
    return application


async def delete_application(db: AsyncSession, user_id: UUID, application_id: UUID) -> None:
    application = await get_application_or_404(db, user_id, application_id)
    await db.delete(application)
    await db.commit()


async def get_applications_for_export(
    db: AsyncSession, user_id: UUID, filters: ApplicationFilters, limit: int
) -> list[JobApplication]:
    stmt: Select = select(JobApplication).where(JobApplication.user_id == user_id)
    stmt = apply_application_filters(stmt, filters)
    stmt = stmt.order_by(JobApplication.applied_date.desc(), JobApplication.created_at.desc())
    stmt = stmt.limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())

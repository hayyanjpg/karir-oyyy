from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Query
from fastapi import status as http_status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import Select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import ApplicationStatus, JobPortal, WorkModel
from app.core.security import ACCESS_TOKEN_TYPE, TokenError, decode_token
from app.db.session import get_db
from app.models import JobApplication, User

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_token(credentials.credentials, ACCESS_TOKEN_TYPE)
    except TokenError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user = await db.get(User, UUID(str(payload["sub"])))
    if user is None or user.token_version != payload.get("ver", 0):
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="User session is no longer valid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


class ApplicationFilters:
    def __init__(
        self,
        search: str | None = Query(default=None, max_length=150),
        status: ApplicationStatus | None = Query(default=None),
        work_model: WorkModel | None = Query(default=None),
        job_portal: JobPortal | None = Query(default=None),
        start_date: date | None = Query(default=None),
        end_date: date | None = Query(default=None),
    ) -> None:
        if start_date and end_date and start_date > end_date:
            raise HTTPException(
                status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="start_date must be before or equal to end_date",
            )
        self.search = search.strip() if search and search.strip() else None
        self.status = status
        self.work_model = work_model
        self.job_portal = job_portal
        self.start_date = start_date
        self.end_date = end_date


def apply_application_filters(stmt: Select, filters: ApplicationFilters) -> Select:
    if filters.search:
        pattern = f"%{escape_like(filters.search)}%"
        stmt = stmt.where(
            or_(
                JobApplication.company_name.ilike(pattern, escape="\\"),
                JobApplication.position_title.ilike(pattern, escape="\\"),
            )
        )
    if filters.status is not None:
        stmt = stmt.where(JobApplication.status == filters.status.value)
    if filters.work_model is not None:
        stmt = stmt.where(JobApplication.work_model == filters.work_model.value)
    if filters.job_portal is not None:
        stmt = stmt.where(JobApplication.job_portal == filters.job_portal.value)
    if filters.start_date is not None:
        stmt = stmt.where(JobApplication.applied_date >= filters.start_date)
    if filters.end_date is not None:
        stmt = stmt.where(JobApplication.applied_date <= filters.end_date)
    return stmt

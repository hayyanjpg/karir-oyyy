from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import ApplicationFilters, get_current_user
from app.db.session import get_db
from app.models import JobApplication, User
from app.schemas.application import (
    ApplicationCreate,
    ApplicationPage,
    ApplicationRead,
    ApplicationUpdate,
)
from app.services import application_service

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("", response_model=ApplicationPage)
async def list_applications(
    filters: Annotated[ApplicationFilters, Depends()],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    sort: Literal["applied_date", "created_at", "updated_at", "company_name"] = Query(
        default="applied_date"
    ),
    order: Literal["asc", "desc"] = Query(default="desc"),
) -> ApplicationPage:
    applications, total = await application_service.list_applications(
        db,
        current_user.id,
        filters,
        page,
        page_size,
        sort,
        order,
    )
    pages = (total + page_size - 1) // page_size if total else 0
    return ApplicationPage(
        items=[ApplicationRead.model_validate(application) for application in applications],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/{application_id}", response_model=ApplicationRead)
async def get_application(
    application_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> JobApplication:
    return await application_service.get_application_or_404(db, current_user.id, application_id)


@router.post("", response_model=ApplicationRead, status_code=http_status.HTTP_201_CREATED)
async def create_application(
    payload: ApplicationCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> JobApplication:
    return await application_service.create_application(db, current_user.id, payload)


@router.patch("/{application_id}", response_model=ApplicationRead)
async def update_application(
    application_id: UUID,
    payload: ApplicationUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> JobApplication:
    return await application_service.update_application(
        db, current_user.id, application_id, payload
    )


@router.delete("/{application_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_application(
    application_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    await application_service.delete_application(db, current_user.id, application_id)

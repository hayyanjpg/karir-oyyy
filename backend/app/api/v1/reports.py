from enum import StrEnum
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import ApplicationFilters, get_current_user
from app.core.config import get_settings
from app.db.session import get_db
from app.models import User
from app.services.analytics_service import get_analytics_summary
from app.services.application_service import get_applications_for_export
from app.services.excel_service import build_excel_report
from app.services.pdf_service import build_pdf_report
from app.services.report_common import build_report_filename

router = APIRouter(prefix="/reports", tags=["reports"])


class ReportFormat(StrEnum):
    XLSX = "xlsx"
    PDF = "pdf"


def describe_filters(filters: ApplicationFilters) -> str:
    parts: list[str] = []
    if filters.search:
        parts.append(f"pencarian='{filters.search}'")
    if filters.status:
        parts.append(f"status={filters.status.value}")
    if filters.work_model:
        parts.append(f"model kerja={filters.work_model.value}")
    if filters.job_portal:
        parts.append(f"portal={filters.job_portal.value}")
    if filters.start_date:
        parts.append(f"mulai={filters.start_date.isoformat()}")
    if filters.end_date:
        parts.append(f"sampai={filters.end_date.isoformat()}")
    return "; ".join(parts) if parts else "Semua data"


@router.get("/export")
async def export_report(
    filters: Annotated[ApplicationFilters, Depends()],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    format: ReportFormat = Query(default=ReportFormat.XLSX),
) -> Response:
    settings = get_settings()
    applications = await get_applications_for_export(
        db,
        current_user.id,
        filters,
        settings.max_export_rows + 1,
    )
    if len(applications) > settings.max_export_rows:
        raise HTTPException(
            status_code=http_status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                f"Filter menghasilkan lebih dari {settings.max_export_rows} lamaran. "
                "Persempit filter sebelum mengekspor."
            ),
        )

    kpi = (await get_analytics_summary(db, current_user.id)).kpi
    filter_summary = describe_filters(filters)

    if format is ReportFormat.XLSX:
        content = build_excel_report(applications, current_user, filter_summary, kpi)
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    else:
        content = build_pdf_report(applications, current_user, filter_summary, kpi)
        media_type = "application/pdf"

    filename = build_report_filename(current_user.full_name, format.value)
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Cache-Control": "no-store",
        "Content-Length": str(len(content)),
    }
    return Response(content=content, media_type=media_type, headers=headers)

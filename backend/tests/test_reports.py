from io import BytesIO
from typing import Any

from httpx import AsyncClient
from openpyxl import load_workbook

from app.models import User
from tests.test_applications import create_application


async def test_export_xlsx(
    client: AsyncClient,
    user_factory: Any,
    auth_headers: Any,
) -> None:
    user: User = await user_factory()
    headers = auth_headers(user)
    await create_application(client, headers)

    response = await client.get(
        "/api/v1/reports/export",
        headers=headers,
        params={"format": "xlsx"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert response.content.startswith(b"PK")
    assert ".xlsx" in response.headers["content-disposition"]
    assert response.headers["cache-control"] == "no-store"

    workbook = load_workbook(BytesIO(response.content))
    assert workbook.sheetnames == ["Data Lamaran", "Ringkasan Statistik"]
    assert workbook["Data Lamaran"].max_row == 2


async def test_export_pdf(
    client: AsyncClient,
    user_factory: Any,
    auth_headers: Any,
) -> None:
    user: User = await user_factory()
    headers = auth_headers(user)
    await create_application(client, headers)

    response = await client.get(
        "/api/v1/reports/export",
        headers=headers,
        params={"format": "pdf"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")
    assert ".pdf" in response.headers["content-disposition"]


async def test_export_applies_filters(
    client: AsyncClient,
    user_factory: Any,
    auth_headers: Any,
) -> None:
    user: User = await user_factory()
    headers = auth_headers(user)
    await create_application(client, headers, company_name="Acme Corp")

    response = await client.get(
        "/api/v1/reports/export",
        headers=headers,
        params={"format": "xlsx", "search": "does-not-exist"},
    )

    assert response.status_code == 200
    workbook = load_workbook(BytesIO(response.content))
    assert workbook["Data Lamaran"].max_row == 1


async def test_export_exposes_content_disposition_for_cors(
    client: AsyncClient,
    user_factory: Any,
    auth_headers: Any,
) -> None:
    user: User = await user_factory()
    headers = auth_headers(user)
    headers["Origin"] = "http://localhost:5173"
    await create_application(client, headers)

    response = await client.get(
        "/api/v1/reports/export",
        headers=headers,
        params={"format": "xlsx"},
    )

    assert response.status_code == 200
    assert (
        "content-disposition" in response.headers.get("access-control-expose-headers", "").lower()
    )


async def test_export_requires_token(client: AsyncClient) -> None:
    response = await client.get("/api/v1/reports/export")
    assert response.status_code == 401

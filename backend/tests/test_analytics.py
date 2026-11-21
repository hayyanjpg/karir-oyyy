from typing import Any

from httpx import AsyncClient
from sqlalchemy import text

from app.db.session import engine
from app.models import User
from tests.test_applications import application_payload, create_application


async def test_analytics_summary(
    client: AsyncClient,
    user_factory: Any,
    auth_headers: Any,
) -> None:
    user: User = await user_factory()
    headers = auth_headers(user)

    statuses = ["Applied", "HR Interview", "Offering", "Rejected"]
    for index, status in enumerate(statuses):
        response = await client.post(
            "/api/v1/applications",
            headers=headers,
            json=application_payload(
                company_name=f"Company {index}",
                status=status,
                job_portal="LinkedIn" if index % 2 == 0 else "Glints",
            ),
        )
        assert response.status_code == 201, response.text

    response = await client.get("/api/v1/analytics/summary", headers=headers)
    assert response.status_code == 200
    body = response.json()

    kpi = body["kpi"]
    assert kpi["total"] == 4
    assert kpi["active_pipeline"] == 2
    assert kpi["interview_count"] == 2
    assert kpi["interview_rate"] == 50.0
    assert kpi["offerings"] == 1
    assert kpi["rejected"] == 1
    assert kpi["ghosted"] == 0

    assert len(body["by_status"]) == 8
    assert {row["status"] for row in body["by_status"]} == {
        "Applied",
        "Screening",
        "Technical Test",
        "HR Interview",
        "User Interview",
        "Offering",
        "Rejected",
        "Ghosted",
    }
    assert len(body["by_portal"]) == 6
    assert body["follow_up"] == []


async def test_analytics_is_tenant_scoped(
    client: AsyncClient,
    user_factory: Any,
    auth_headers: Any,
) -> None:
    owner: User = await user_factory(email="owner@example.com", google_id="google-owner")
    other: User = await user_factory(email="other@example.com", google_id="google-other")

    await create_application(client, auth_headers(owner))

    response = await client.get("/api/v1/analytics/summary", headers=auth_headers(other))
    assert response.status_code == 200
    assert response.json()["kpi"]["total"] == 0


async def test_analytics_requires_token(client: AsyncClient) -> None:
    response = await client.get("/api/v1/analytics/summary")
    assert response.status_code == 401


async def test_analytics_follow_up(
    client: AsyncClient,
    user_factory: Any,
    auth_headers: Any,
) -> None:
    user: User = await user_factory()
    headers = auth_headers(user)
    created = await create_application(client, headers, status="Screening")

    async with engine.begin() as connection:
        await connection.execute(
            text("ALTER TABLE job_applications DISABLE TRIGGER trg_job_applications_updated_at")
        )
        await connection.execute(
            text(
                "UPDATE job_applications "
                "SET updated_at = NOW() - INTERVAL '30 days' "
                "WHERE id = :application_id"
            ),
            {"application_id": created["id"]},
        )
        await connection.execute(
            text("ALTER TABLE job_applications ENABLE TRIGGER trg_job_applications_updated_at")
        )

    response = await client.get("/api/v1/analytics/summary", headers=headers)
    follow_up = response.json()["follow_up"]
    assert len(follow_up) == 1
    assert follow_up[0]["days_since_update"] >= 30

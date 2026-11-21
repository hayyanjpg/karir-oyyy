from datetime import date, timedelta
from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select, text

from app.db.session import SessionLocal, engine
from app.models import StatusHistory, User


def application_payload(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "company_name": "Acme Corp",
        "position_title": "Backend Engineer",
        "status": "Applied",
        "applied_date": date.today().isoformat(),
        "job_portal": "LinkedIn",
        "work_model": "Remote",
        "salary_range": "IDR 15.000.000 - 20.000.000",
        "job_url": "https://example.com/jobs/1",
        "notes": "Referral from a friend.",
    }
    payload.update(overrides)
    return payload


async def create_application(
    client: AsyncClient, headers: dict[str, str], **overrides: Any
) -> dict[str, Any]:
    response = await client.post(
        "/api/v1/applications",
        headers=headers,
        json=application_payload(**overrides),
    )
    assert response.status_code == 201, response.text
    return response.json()


async def test_auth_guard_without_token(client: AsyncClient) -> None:
    assert (await client.get("/api/v1/applications")).status_code == 401
    assert (
        await client.post("/api/v1/applications", json=application_payload())
    ).status_code == 401
    assert (
        await client.patch(
            "/api/v1/applications/00000000-0000-0000-0000-000000000000",
            json={"status": "Screening"},
        )
    ).status_code == 401
    assert (
        await client.delete("/api/v1/applications/00000000-0000-0000-0000-000000000000")
    ).status_code == 401


async def test_create_and_list_application(
    client: AsyncClient,
    user_factory: Any,
    auth_headers: Any,
) -> None:
    user: User = await user_factory()
    headers = auth_headers(user)

    created = await create_application(client, headers)

    assert created["company_name"] == "Acme Corp"
    assert created["status"] == "Applied"
    assert created["needs_follow_up"] is False

    listing = await client.get("/api/v1/applications", headers=headers)
    assert listing.status_code == 200
    body = listing.json()
    assert body["total"] == 1
    assert body["page"] == 1
    assert body["pages"] == 1
    assert body["items"][0]["id"] == created["id"]

    detail = await client.get(f"/api/v1/applications/{created['id']}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["position_title"] == "Backend Engineer"


@pytest.mark.parametrize(
    "override",
    [
        {"status": "Unknown"},
        {"work_model": "Onsite"},
        {"job_portal": "Indeed"},
        {"company_name": "   "},
        {"job_url": "example.com/no-scheme"},
        {"applied_date": "not-a-date"},
    ],
)
async def test_create_validation(
    client: AsyncClient,
    user_factory: Any,
    auth_headers: Any,
    override: dict[str, Any],
) -> None:
    user: User = await user_factory()
    response = await client.post(
        "/api/v1/applications",
        headers=auth_headers(user),
        json=application_payload(**override),
    )
    assert response.status_code == 422


async def test_update_requires_at_least_one_field(
    client: AsyncClient, user_factory: Any, auth_headers: Any
) -> None:
    user: User = await user_factory()
    headers = auth_headers(user)
    created = await create_application(client, headers)

    response = await client.patch(
        f"/api/v1/applications/{created['id']}",
        headers=headers,
        json={},
    )
    assert response.status_code == 422


async def test_tenant_isolation(
    client: AsyncClient,
    user_factory: Any,
    auth_headers: Any,
) -> None:
    owner: User = await user_factory(email="owner@example.com", google_id="google-owner")
    other: User = await user_factory(email="other@example.com", google_id="google-other")
    owner_headers = auth_headers(owner)
    other_headers = auth_headers(other)

    created = await create_application(client, owner_headers)

    listing = await client.get("/api/v1/applications", headers=other_headers)
    assert listing.status_code == 200
    assert listing.json()["total"] == 0

    detail = await client.get(f"/api/v1/applications/{created['id']}", headers=other_headers)
    assert detail.status_code == 404

    patch = await client.patch(
        f"/api/v1/applications/{created['id']}",
        headers=other_headers,
        json={"status": "Screening"},
    )
    assert patch.status_code == 404

    delete = await client.delete(f"/api/v1/applications/{created['id']}", headers=other_headers)
    assert delete.status_code == 404


async def test_filters(
    client: AsyncClient,
    user_factory: Any,
    auth_headers: Any,
) -> None:
    user: User = await user_factory()
    headers = auth_headers(user)
    today = date.today()

    await create_application(
        client,
        headers,
        company_name="Acme Corp",
        status="Applied",
        work_model="Remote",
        job_portal="LinkedIn",
        applied_date=today.isoformat(),
    )
    await create_application(
        client,
        headers,
        company_name="Beta Studio",
        status="HR Interview",
        work_model="Hybrid",
        job_portal="Glints",
        applied_date=(today - timedelta(days=10)).isoformat(),
    )
    await create_application(
        client,
        headers,
        company_name="Gamma Labs",
        status="Rejected",
        work_model="WFO",
        job_portal="JobStreet",
        applied_date=(today - timedelta(days=40)).isoformat(),
    )

    search = await client.get("/api/v1/applications", headers=headers, params={"search": "acme"})
    assert search.json()["total"] == 1
    assert search.json()["items"][0]["company_name"] == "Acme Corp"

    status_filter = await client.get(
        "/api/v1/applications", headers=headers, params={"status": "Rejected"}
    )
    assert status_filter.json()["total"] == 1

    work_model_filter = await client.get(
        "/api/v1/applications", headers=headers, params={"work_model": "Hybrid"}
    )
    assert work_model_filter.json()["total"] == 1

    portal_filter = await client.get(
        "/api/v1/applications", headers=headers, params={"job_portal": "JobStreet"}
    )
    assert portal_filter.json()["total"] == 1

    date_filter = await client.get(
        "/api/v1/applications",
        headers=headers,
        params={
            "start_date": (today - timedelta(days=15)).isoformat(),
            "end_date": today.isoformat(),
        },
    )
    assert date_filter.json()["total"] == 2

    invalid_range = await client.get(
        "/api/v1/applications",
        headers=headers,
        params={"start_date": today.isoformat(), "end_date": "2020-01-01"},
    )
    assert invalid_range.status_code == 422


async def test_pagination(
    client: AsyncClient,
    user_factory: Any,
    auth_headers: Any,
) -> None:
    user: User = await user_factory()
    headers = auth_headers(user)

    for index in range(3):
        await create_application(
            client,
            headers,
            company_name=f"Company {index}",
            applied_date=(date.today() - timedelta(days=index)).isoformat(),
        )

    first_page = await client.get(
        "/api/v1/applications",
        headers=headers,
        params={"page": 1, "page_size": 2},
    )
    assert first_page.json()["total"] == 3
    assert first_page.json()["pages"] == 2
    assert len(first_page.json()["items"]) == 2

    second_page = await client.get(
        "/api/v1/applications",
        headers=headers,
        params={"page": 2, "page_size": 2},
    )
    assert len(second_page.json()["items"]) == 1


async def test_status_history_and_interview_rate(
    client: AsyncClient,
    user_factory: Any,
    auth_headers: Any,
) -> None:
    user: User = await user_factory()
    headers = auth_headers(user)
    created = await create_application(client, headers)

    to_interview = await client.patch(
        f"/api/v1/applications/{created['id']}",
        headers=headers,
        json={"status": "HR Interview"},
    )
    assert to_interview.status_code == 200

    to_rejected = await client.patch(
        f"/api/v1/applications/{created['id']}",
        headers=headers,
        json={"status": "Rejected"},
    )
    assert to_rejected.status_code == 200
    assert to_rejected.json()["status"] == "Rejected"

    async with SessionLocal() as session:
        history_count = await session.scalar(
            select(func.count(StatusHistory.id)).where(
                StatusHistory.application_id == created["id"]
            )
        )
    assert history_count == 3

    summary = await client.get("/api/v1/analytics/summary", headers=headers)
    kpi = summary.json()["kpi"]
    assert kpi["interview_count"] == 1
    assert kpi["interview_rate"] == 100.0
    assert kpi["rejected"] == 1


async def test_follow_up_flag(
    client: AsyncClient,
    user_factory: Any,
    auth_headers: Any,
) -> None:
    user: User = await user_factory()
    headers = auth_headers(user)
    created = await create_application(client, headers)

    async with engine.begin() as connection:
        await connection.execute(
            text("ALTER TABLE job_applications DISABLE TRIGGER trg_job_applications_updated_at")
        )
        await connection.execute(
            text(
                "UPDATE job_applications "
                "SET updated_at = NOW() - INTERVAL '20 days' "
                "WHERE id = :application_id"
            ),
            {"application_id": created["id"]},
        )
        await connection.execute(
            text("ALTER TABLE job_applications ENABLE TRIGGER trg_job_applications_updated_at")
        )

    detail = await client.get(f"/api/v1/applications/{created['id']}", headers=headers)
    assert detail.json()["needs_follow_up"] is True
    assert detail.json()["days_since_update"] >= 20

    summary = await client.get("/api/v1/analytics/summary", headers=headers)
    assert len(summary.json()["follow_up"]) == 1
    assert summary.json()["follow_up"][0]["id"] == created["id"]


async def test_delete_application(
    client: AsyncClient,
    user_factory: Any,
    auth_headers: Any,
) -> None:
    user: User = await user_factory()
    headers = auth_headers(user)
    created = await create_application(client, headers)

    deleted = await client.delete(f"/api/v1/applications/{created['id']}", headers=headers)
    assert deleted.status_code == 204

    detail = await client.get(f"/api/v1/applications/{created['id']}", headers=headers)
    assert detail.status_code == 404

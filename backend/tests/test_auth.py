import pytest
from httpx import AsyncClient

from app.api.v1 import auth as auth_module
from app.core.security import TokenError


async def test_health(client: AsyncClient) -> None:
    response = await client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_google_login_creates_user_and_sets_cookie(
    client: AsyncClient, mock_google_login: None
) -> None:
    response = await client.post(
        "/api/v1/auth/google",
        json={"credential": "valid-google-credential"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == "google.user@example.com"
    assert body["user"]["full_name"] == "Google User"

    set_cookie = response.headers.get("set-cookie", "")
    assert "karirtrack_refresh=" in set_cookie
    assert "HttpOnly" in set_cookie
    assert "Path=/api/v1/auth" in set_cookie


async def test_google_login_rejects_invalid_credential(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    def reject(credential: str) -> dict[str, object]:
        raise TokenError("Invalid Google credential")

    monkeypatch.setattr(auth_module, "verify_google_token", reject)

    response = await client.post(
        "/api/v1/auth/google",
        json={"credential": "invalid-google-credential"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid Google credential"


async def test_me_requires_token(client: AsyncClient) -> None:
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


async def test_me_returns_profile(client: AsyncClient, mock_google_login: None) -> None:
    login = await client.post(
        "/api/v1/auth/google",
        json={"credential": "valid-google-credential"},
    )
    access_token = login.json()["access_token"]

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "google.user@example.com"


async def test_refresh_rotates_access_token(client: AsyncClient, mock_google_login: None) -> None:
    login = await client.post(
        "/api/v1/auth/google",
        json={"credential": "valid-google-credential"},
    )
    first_access_token = login.json()["access_token"]
    assert client.cookies.get("karirtrack_refresh")

    refreshed = await client.post("/api/v1/auth/refresh")

    assert refreshed.status_code == 200
    assert refreshed.json()["access_token"] != first_access_token
    assert "karirtrack_refresh=" in refreshed.headers.get("set-cookie", "")


async def test_logout_revokes_refresh_token(client: AsyncClient, mock_google_login: None) -> None:
    await client.post(
        "/api/v1/auth/google",
        json={"credential": "valid-google-credential"},
    )

    logout = await client.post("/api/v1/auth/logout")
    assert logout.status_code == 204

    refreshed = await client.post("/api/v1/auth/refresh")
    assert refreshed.status_code == 401

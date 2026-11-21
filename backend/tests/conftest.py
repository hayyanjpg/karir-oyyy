import asyncio
import os
import sys
from pathlib import Path

# psycopg's async mode cannot run on Windows' default ProactorEventLoop.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/karirtrack_test",
)
os.environ.setdefault(
    "DATABASE_URL_DIRECT",
    os.environ["DATABASE_URL"],
)
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-at-least-32-characters-long")
os.environ.setdefault("GOOGLE_CLIENT_ID", "test-google-client-id")
os.environ.setdefault("COOKIE_SECURE", "false")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")

from collections.abc import AsyncGenerator, Callable  # noqa: E402

import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from app.api.v1 import auth as auth_module  # noqa: E402
from app.core.security import create_access_token  # noqa: E402
from app.db.session import SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models import User  # noqa: E402

BACKEND_DIR = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session", autouse=True)
def apply_migrations() -> None:
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    command.upgrade(config, "head")


@pytest_asyncio.fixture(autouse=True)
async def clean_database() -> AsyncGenerator[None, None]:
    async with engine.begin() as connection:
        await connection.execute(text("TRUNCATE TABLE users CASCADE"))
    yield


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client


@pytest_asyncio.fixture
async def user_factory() -> Callable[..., object]:
    async def create_user(
        email: str = "user@example.com",
        google_id: str = "google-user-1",
        full_name: str = "Test User",
    ) -> User:
        async with SessionLocal() as session:
            user = User(google_id=google_id, email=email, full_name=full_name)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    return create_user


@pytest.fixture
def auth_headers() -> Callable[[User], dict[str, str]]:
    def build(user: User) -> dict[str, str]:
        token = create_access_token(user.id, user.token_version)
        return {"Authorization": f"Bearer {token}"}

    return build


@pytest.fixture
def google_identity() -> dict[str, object]:
    return {
        "sub": "google-123",
        "email": "google.user@example.com",
        "email_verified": True,
        "name": "Google User",
        "picture": "https://example.com/avatar.png",
    }


@pytest.fixture
def mock_google_login(monkeypatch: pytest.MonkeyPatch, google_identity: dict[str, object]) -> None:
    def fake_verify(credential: str) -> dict[str, object]:
        return google_identity

    monkeypatch.setattr(auth_module, "verify_google_token", fake_verify)

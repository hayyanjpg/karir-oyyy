from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


async def upsert_google_user(db: AsyncSession, idinfo: dict[str, Any]) -> User:
    google_id = str(idinfo["sub"])
    email = str(idinfo["email"])
    full_name = str(idinfo.get("name") or email.split("@")[0])[:150]
    avatar_url = idinfo.get("picture")
    now = datetime.now(UTC)

    result = await db.execute(select(User).where(User.google_id == google_id))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            google_id=google_id,
            email=email,
            full_name=full_name,
            avatar_url=avatar_url,
            last_login=now,
        )
        db.add(user)
        try:
            await db.commit()
        except IntegrityError:
            # Two first-time logins can race; fall back to the winning row.
            await db.rollback()
            result = await db.execute(select(User).where(User.google_id == google_id))
            user = result.scalar_one()
            user.last_login = now
            await db.commit()
    else:
        user.email = email
        user.full_name = full_name
        if avatar_url:
            user.avatar_url = avatar_url
        user.last_login = now
        await db.commit()

    await db.refresh(user)
    return user

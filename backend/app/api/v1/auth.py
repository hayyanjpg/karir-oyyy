from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.security import (
    REFRESH_COOKIE_NAME,
    REFRESH_TOKEN_TYPE,
    TokenError,
    clear_refresh_cookie,
    create_access_token,
    create_refresh_token,
    decode_token,
    set_refresh_cookie,
    verify_google_token,
)
from app.db.session import get_db
from app.models import User
from app.schemas.auth import GoogleLoginRequest, TokenResponse, UserRead
from app.services.auth_service import upsert_google_user

router = APIRouter(prefix="/auth", tags=["auth"])


def _token_response(user: User, access_token: str) -> TokenResponse:
    settings = get_settings()
    return TokenResponse(
        access_token=access_token,
        expires_in=settings.access_token_expire_minutes * 60,
        user=UserRead.model_validate(user),
    )


@router.post("/google", response_model=TokenResponse)
async def google_login(
    payload: GoogleLoginRequest,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    try:
        idinfo = await run_in_threadpool(verify_google_token, payload.credential)
    except TokenError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    user = await upsert_google_user(db, idinfo)
    access_token = create_access_token(user.id, user.token_version)
    set_refresh_cookie(response, create_refresh_token(user.id, user.token_version))
    return _token_response(user, access_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    token = request.cookies.get(REFRESH_COOKIE_NAME)
    if not token:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is missing",
        )

    try:
        payload = decode_token(token, REFRESH_TOKEN_TYPE)
    except TokenError as exc:
        clear_refresh_cookie(response)
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    user = await db.get(User, UUID(str(payload["sub"])))
    if user is None or user.token_version != payload.get("ver", 0):
        clear_refresh_cookie(response)
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is no longer valid",
        )

    access_token = create_access_token(user.id, user.token_version)
    set_refresh_cookie(response, create_refresh_token(user.id, user.token_version))
    return _token_response(user, access_token)


@router.post("/logout", status_code=http_status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    token = request.cookies.get(REFRESH_COOKIE_NAME)
    if token:
        try:
            payload = decode_token(token, REFRESH_TOKEN_TYPE)
            user = await db.get(User, UUID(str(payload["sub"])))
            if user is not None:
                user.token_version += 1
                await db.commit()
        except TokenError:
            pass
    clear_refresh_cookie(response)


@router.get("/me", response_model=UserRead)
async def read_current_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import jwt
from fastapi import Response
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from app.core.config import get_settings

REFRESH_COOKIE_NAME = "karirtrack_refresh"
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


class TokenError(Exception):
    """Raised when a JWT or Google credential cannot be trusted."""


def _encode_token(user_id: UUID, token_version: int, token_type: str, lifetime: timedelta) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "type": token_type,
        "ver": token_version,
        "iat": now,
        "exp": now + lifetime,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(user_id: UUID, token_version: int) -> str:
    settings = get_settings()
    return _encode_token(
        user_id,
        token_version,
        ACCESS_TOKEN_TYPE,
        timedelta(minutes=settings.access_token_expire_minutes),
    )


def create_refresh_token(user_id: UUID, token_version: int) -> str:
    settings = get_settings()
    return _encode_token(
        user_id,
        token_version,
        REFRESH_TOKEN_TYPE,
        timedelta(days=settings.refresh_token_expire_days),
    )


def decode_token(token: str, expected_type: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "type", "exp", "iat"]},
        )
    except ExpiredSignatureError as exc:
        raise TokenError("Token has expired") from exc
    except InvalidTokenError as exc:
        raise TokenError("Token is invalid") from exc

    if payload.get("type") != expected_type:
        raise TokenError("Unexpected token type")

    try:
        UUID(str(payload["sub"]))
    except (KeyError, ValueError) as exc:
        raise TokenError("Token subject is invalid") from exc

    return payload


def verify_google_token(credential: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        idinfo = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            settings.google_client_id,
        )
    except ValueError as exc:
        raise TokenError("Invalid Google credential") from exc

    issuer = idinfo.get("iss")
    if issuer not in {"accounts.google.com", "https://accounts.google.com"}:
        raise TokenError("Invalid Google issuer")
    if not idinfo.get("email_verified", False):
        raise TokenError("Google email is not verified")

    return idinfo


def set_refresh_cookie(response: Response, token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=token,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        path=settings.cookie_path,
        domain=settings.cookie_domain,
    )


def clear_refresh_cookie(response: Response) -> None:
    settings = get_settings()
    response.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        path=settings.cookie_path,
        domain=settings.cookie_domain,
        secure=settings.cookie_secure,
        httponly=True,
        samesite=settings.cookie_samesite,
    )

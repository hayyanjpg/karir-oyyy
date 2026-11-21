from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class GoogleLoginRequest(BaseModel):
    credential: str = Field(min_length=10)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    full_name: str
    avatar_url: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserRead

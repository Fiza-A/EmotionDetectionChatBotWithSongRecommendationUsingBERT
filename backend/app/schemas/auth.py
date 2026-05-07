from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.user import UserRead


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    preferred_languages: list[str] = Field(default_factory=lambda: ["English", "Hindi"])

    @field_validator("preferred_languages")
    @classmethod
    def languages_required(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("Select at least one preferred language.")
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator


class UserPreferenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    preferred_languages: list[str]

    @field_validator("preferred_languages", mode="before")
    @classmethod
    def split_languages(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    created_at: datetime
    preferences: UserPreferenceRead


class PreferenceUpdate(BaseModel):
    preferred_languages: list[str] = Field(min_length=1)

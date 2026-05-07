from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.chat import ChatMessageRead


class ConversationCreate(BaseModel):
    title: str | None = Field(default=None, max_length=160)


class ConversationUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=160)


class ConversationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    created_at: datetime
    updated_at: datetime


class ConversationDetail(ConversationRead):
    messages: list[ChatMessageRead]

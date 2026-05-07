from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from app.schemas.recommendation import RecommendationRead


class ChatMessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class ChatMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sender: str
    message_text: str
    detected_emotion: str | None = None
    confidence_score: float | None = None
    created_at: datetime


class ChatResponse(BaseModel):
    user_message: ChatMessageRead
    bot_message: ChatMessageRead
    detected_emotion: str
    confidence_score: float
    safety_triggered: bool
    recommendations: list[RecommendationRead]


class MoodHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    emotion: str
    confidence_score: float
    created_at: datetime

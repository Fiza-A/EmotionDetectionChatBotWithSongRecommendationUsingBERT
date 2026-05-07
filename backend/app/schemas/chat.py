from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from app.schemas.recommendation import RecommendationBundle, RecommendationRead


class ChatMessageRequest(BaseModel):
    message: str | None = Field(default=None, max_length=2000)
    message_text: str | None = Field(default=None, max_length=2000)
    conversation_id: int | None = None

    @property
    def text(self) -> str:
        return (self.message_text or self.message or "").strip()


class ChatMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sender: str
    message_text: str
    detected_emotion: str | None = None
    confidence_score: float | None = None
    recommendations: list[RecommendationRead] = Field(default_factory=list)
    recommendation_message: str | None = None
    created_at: datetime


class ChatResponse(BaseModel):
    conversation_id: int
    conversation_title: str
    user_message: ChatMessageRead
    bot_message: ChatMessageRead
    detected_emotion: str
    confidence_score: float
    safety_triggered: bool
    recommendations: RecommendationBundle


class MoodHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    emotion: str
    confidence_score: float
    created_at: datetime

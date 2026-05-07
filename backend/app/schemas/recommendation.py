from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RecommendationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    type: str
    language: str
    mood_tags: list[str]
    genre: str | None = None
    creator: str | None = None
    year: int | None = None
    link: str | None = None


class FeedbackRequest(BaseModel):
    recommendation_id: int
    detected_emotion: str = Field(min_length=2)
    feedback: str = Field(pattern="^(like|dislike|neutral)$")


class RecommendationEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    recommendation_id: int
    detected_emotion: str
    feedback: str | None
    created_at: datetime

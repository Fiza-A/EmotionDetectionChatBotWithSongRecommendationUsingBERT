from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.security import get_current_user
from app.database import get_db
from app.models.models import Recommendation, RecommendationEvent, User
from app.schemas.recommendation import FeedbackRequest, RecommendationEventRead, RecommendationRead
from app.services.recommendation_service import get_recommendations_for_user, recommendation_to_read

router = APIRouter()


@router.get("", response_model=list[RecommendationRead])
def recommendations(
    emotion: str = "neutral",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = get_recommendations_for_user(db, current_user, emotion, enrich_itunes=True)
    return [recommendation_to_read(item) for item in result.items]


@router.post("/feedback", response_model=RecommendationEventRead)
def feedback(payload: FeedbackRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    recommendation = db.get(Recommendation, payload.recommendation_id)
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found.")
    event = RecommendationEvent(
        user_id=current_user.id,
        recommendation_id=payload.recommendation_id,
        detected_emotion=payload.detected_emotion,
        feedback=payload.feedback,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

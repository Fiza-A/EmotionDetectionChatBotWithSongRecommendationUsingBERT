from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.security import get_current_user
from app.database import get_db
from app.models.models import ChatMessage, User
from app.schemas.chat import ChatMessageRead, ChatMessageRequest, ChatResponse
from app.services.chat_service import handle_chat_message
from app.services.recommendation_service import recommendation_to_read

router = APIRouter()


@router.post("/message", response_model=ChatResponse)
def message(payload: ChatMessageRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_message, bot_message, recommendations, safety_triggered = handle_chat_message(db, current_user, payload.message)
    return {
        "user_message": user_message,
        "bot_message": bot_message,
        "detected_emotion": bot_message.detected_emotion,
        "confidence_score": bot_message.confidence_score,
        "safety_triggered": safety_triggered,
        "recommendations": [recommendation_to_read(item) for item in recommendations],
    }


@router.get("/history", response_model=list[ChatMessageRead])
def history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == current_user.id)
        .order_by(ChatMessage.created_at.asc())
        .limit(200)
        .all()
    )


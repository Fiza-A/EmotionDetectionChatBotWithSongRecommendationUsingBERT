import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.security import get_current_user
from app.database import get_db
from app.models.models import ChatMessage, User
from app.schemas.chat import ChatMessageRead, ChatMessageRequest, ChatResponse
from app.services.chat_service import handle_chat_message
from app.routes.conversations import message_to_read
from app.services.recommendation_service import recommendation_to_read

router = APIRouter()


@router.post("/message", response_model=ChatResponse)
def message(payload: ChatMessageRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    text = payload.text
    if not text:
        raise HTTPException(status_code=422, detail="Message text is required.")
    conversation, user_message, bot_message, recommendation_result, safety_triggered = handle_chat_message(db, current_user, text, payload.conversation_id)
    return {
        "conversation_id": conversation.id,
        "conversation_title": conversation.title,
        "user_message": message_to_read(user_message),
        "bot_message": message_to_read(bot_message),
        "detected_emotion": bot_message.detected_emotion,
        "confidence_score": bot_message.confidence_score,
        "safety_triggered": safety_triggered,
        "recommendations": {"songs": [], "movies": [], "message": None} if safety_triggered else recommendation_result.to_payload(),
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

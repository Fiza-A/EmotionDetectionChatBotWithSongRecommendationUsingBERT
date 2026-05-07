import json

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.auth.security import get_current_user
from app.database import get_db
from app.models.models import ChatMessage, User
from app.schemas.conversation import ConversationCreate, ConversationDetail, ConversationRead, ConversationUpdate
from app.services.conversation_service import (
    create_conversation,
    delete_conversation,
    get_user_conversation,
    list_user_conversations,
    rename_conversation,
)

router = APIRouter()


def message_to_read(message: ChatMessage) -> dict:
    recommendations = []
    recommendation_message = None
    if message.recommendations_json:
        try:
            payload = json.loads(message.recommendations_json)
            if isinstance(payload, dict):
                recommendations = [*payload.get("songs", []), *payload.get("movies", [])]
                recommendation_message = payload.get("message")
            elif isinstance(payload, list):
                recommendations = payload
        except json.JSONDecodeError:
            recommendations = []
    return {
        "id": message.id,
        "sender": message.sender,
        "message_text": message.message_text,
        "detected_emotion": message.detected_emotion,
        "confidence_score": message.confidence_score,
        "recommendations": recommendations,
        "recommendation_message": recommendation_message,
        "created_at": message.created_at,
    }


@router.post("", response_model=ConversationRead)
def create(payload: ConversationCreate | None = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_conversation(db, current_user, payload.title if payload else None)


@router.get("", response_model=list[ConversationRead])
def list_conversations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return list_user_conversations(db, current_user)


@router.get("/{conversation_id}", response_model=ConversationDetail)
def detail(conversation_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    conversation = get_user_conversation(db, current_user, conversation_id)
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == current_user.id, ChatMessage.conversation_id == conversation.id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    return {
        "id": conversation.id,
        "title": conversation.title,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
        "messages": [message_to_read(message) for message in messages],
    }


@router.patch("/{conversation_id}", response_model=ConversationRead)
def rename(conversation_id: int, payload: ConversationUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return rename_conversation(db, current_user, conversation_id, payload.title)


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(conversation_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    delete_conversation(db, current_user, conversation_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

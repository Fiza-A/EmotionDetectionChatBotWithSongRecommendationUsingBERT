from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.models import ChatMessage, Conversation, RecommendationEvent, User


def make_title_from_message(text: str) -> str:
    cleaned = " ".join(text.strip().split())
    if not cleaned:
        return "New Conversation"
    return cleaned if len(cleaned) <= 34 else f"{cleaned[:31].rstrip()}..."


def create_conversation(db: Session, user: User, title: str | None = None) -> Conversation:
    conversation = Conversation(user_id=user.id, title=title or "New Conversation")
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def get_user_conversation(db: Session, user: User, conversation_id: int) -> Conversation:
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == user.id).first()
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")
    return conversation


def list_user_conversations(db: Session, user: User) -> list[Conversation]:
    return db.query(Conversation).filter(Conversation.user_id == user.id).order_by(Conversation.updated_at.desc()).all()


def rename_conversation(db: Session, user: User, conversation_id: int, title: str) -> Conversation:
    conversation = get_user_conversation(db, user, conversation_id)
    conversation.title = title.strip() or "New Conversation"
    conversation.updated_at = datetime.utcnow()
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def delete_conversation(db: Session, user: User, conversation_id: int) -> None:
    conversation = get_user_conversation(db, user, conversation_id)
    db.query(RecommendationEvent).filter(
        RecommendationEvent.user_id == user.id,
        RecommendationEvent.conversation_id == conversation.id,
    ).delete(synchronize_session=False)
    db.query(ChatMessage).filter(
        ChatMessage.user_id == user.id,
        ChatMessage.conversation_id == conversation.id,
    ).delete(synchronize_session=False)
    db.delete(conversation)
    db.commit()

import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.ml.inference import classifier
from app.models.models import ChatMessage, Conversation, MoodHistory, User
from app.services.conversation_service import get_user_conversation, make_title_from_message
from app.services.recommendation_service import get_recommendations_for_user, recommendation_to_read, record_recommendation_events
from app.services.safety import has_self_harm_intent, safety_response


EMPATHY = {
    "happy": "I sense you’re feeling happy. Here are some bright picks to keep that energy going.",
    "excited": "You sound excited. I picked upbeat recommendations that match that spark.",
    "calm": "You seem calm or gently positive. Here are easygoing recommendations for that mood.",
    "neutral": "I’m reading your mood as fairly neutral. Here are feel-good options to keep things light.",
    "sad": "I sense you may be feeling low. Here are uplifting and comforting picks that may help lighten the moment.",
    "disappointed": "I sense disappointment or heaviness. Here are hopeful, warm recommendations to lift the mood a little.",
    "angry": "I sense frustration or anger. Here are calming and funny picks to help soften the edge.",
    "anxious": "You may be feeling anxious or unsettled. Here are calming and comforting recommendations.",
    "lonely": "You may be feeling lonely. Here are warm, hopeful picks with a little companionship built in.",
}


def _ensure_conversation(db: Session, user: User, conversation_id: int | None) -> Conversation:
    if conversation_id:
        return get_user_conversation(db, user, conversation_id)
    conversation = Conversation(user_id=user.id, title="New Conversation")
    db.add(conversation)
    db.flush()
    return conversation


def handle_chat_message(db: Session, user: User, text: str, conversation_id: int | None = None) -> tuple[Conversation, ChatMessage, ChatMessage, list, bool]:
    conversation = _ensure_conversation(db, user, conversation_id)
    safety_triggered = has_self_harm_intent(text)
    prediction = classifier.predict(text)
    had_user_message = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user.id, ChatMessage.conversation_id == conversation.id, ChatMessage.sender == "user")
        .first()
        is not None
    )
    if not had_user_message and conversation.title == "New Conversation":
        conversation.title = make_title_from_message(text)

    user_message = ChatMessage(
        user_id=user.id,
        conversation_id=conversation.id,
        sender="user",
        message_text=text,
        detected_emotion=prediction.emotion,
        confidence_score=prediction.confidence,
    )
    db.add(user_message)
    db.add(MoodHistory(user_id=user.id, conversation_id=conversation.id, emotion=prediction.emotion, confidence_score=prediction.confidence))
    db.flush()

    recommendation_result = None if safety_triggered else get_recommendations_for_user(db, user, prediction.emotion, enrich_itunes=True)
    recommendation_payload = {"songs": [], "movies": [], "message": None} if safety_triggered else recommendation_result.to_payload()
    recommendation_items = [] if safety_triggered else recommendation_result.items
    if recommendation_items:
        record_recommendation_events(db, user, recommendation_items, prediction.emotion, conversation_id=conversation.id)

    body = safety_response() if safety_triggered else EMPATHY.get(prediction.emotion, EMPATHY["neutral"])
    bot_text = f"{body} Detected emotion: {prediction.emotion} ({prediction.confidence:.0%} confidence)."
    bot_message = ChatMessage(
        user_id=user.id,
        conversation_id=conversation.id,
        sender="bot",
        message_text=bot_text,
        detected_emotion=prediction.emotion,
        confidence_score=prediction.confidence,
        recommendations_json=json.dumps(recommendation_payload),
    )
    conversation.updated_at = datetime.utcnow()
    db.add(conversation)
    db.add(bot_message)
    db.commit()
    db.refresh(conversation)
    db.refresh(user_message)
    db.refresh(bot_message)
    return conversation, user_message, bot_message, recommendation_result, safety_triggered

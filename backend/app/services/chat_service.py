from sqlalchemy.orm import Session

from app.ml.inference import classifier
from app.models.models import ChatMessage, MoodHistory, User
from app.services.recommendation_service import get_recommendations_for_user, record_recommendation_events
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


def handle_chat_message(db: Session, user: User, text: str) -> tuple[ChatMessage, ChatMessage, list, bool]:
    safety_triggered = has_self_harm_intent(text)
    prediction = classifier.predict(text)

    user_message = ChatMessage(
        user_id=user.id,
        sender="user",
        message_text=text,
        detected_emotion=prediction.emotion,
        confidence_score=prediction.confidence,
    )
    db.add(user_message)
    db.add(MoodHistory(user_id=user.id, emotion=prediction.emotion, confidence_score=prediction.confidence))
    db.flush()

    recommendations = [] if safety_triggered else get_recommendations_for_user(db, user, prediction.emotion)
    if recommendations:
        record_recommendation_events(db, user, recommendations, prediction.emotion)

    body = safety_response() if safety_triggered else EMPATHY.get(prediction.emotion, EMPATHY["neutral"])
    bot_text = f"{body} Detected emotion: {prediction.emotion} ({prediction.confidence:.0%} confidence)."
    bot_message = ChatMessage(
        user_id=user.id,
        sender="bot",
        message_text=bot_text,
        detected_emotion=prediction.emotion,
        confidence_score=prediction.confidence,
    )
    db.add(bot_message)
    db.commit()
    db.refresh(user_message)
    db.refresh(bot_message)
    return user_message, bot_message, recommendations, safety_triggered

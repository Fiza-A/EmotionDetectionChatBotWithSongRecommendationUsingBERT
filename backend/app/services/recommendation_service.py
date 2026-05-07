from collections import Counter

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.models import Recommendation, RecommendationEvent, User
from app.services.user_service import parse_languages

NEGATIVE_MOODS = {"sad", "angry", "anxious", "disappointed", "lonely"}
MOOD_TARGETS = {
    "happy": ["happy", "upbeat", "feel-good", "comedy"],
    "excited": ["excited", "upbeat", "adventure", "happy"],
    "calm": ["calm", "comforting", "hopeful"],
    "neutral": ["feel-good", "calm", "comedy"],
    "sad": ["uplifting", "comforting", "hopeful", "comedy", "calm"],
    "disappointed": ["uplifting", "hopeful", "feel-good", "comforting"],
    "angry": ["calm", "comedy", "uplifting", "feel-good"],
    "anxious": ["calm", "comforting", "hopeful", "feel-good"],
    "lonely": ["comforting", "hopeful", "friendship", "feel-good"],
}


def _tags(value: str) -> list[str]:
    return [tag.strip() for tag in value.split(",") if tag.strip()]


def recommendation_to_read(item: Recommendation) -> dict:
    return {
        "id": item.id,
        "title": item.title,
        "type": item.type,
        "language": item.language,
        "mood_tags": _tags(item.mood_tags),
        "genre": item.genre,
        "creator": item.creator,
        "year": item.year,
        "link": item.link,
        "preview_url": item.preview_url,
        "album_art": item.album_art,
        "external_url": item.external_url,
    }


def get_common_moods(db: Session, user: User) -> list[str]:
    rows = (
        db.query(RecommendationEvent.detected_emotion, func.count(RecommendationEvent.id))
        .filter(RecommendationEvent.user_id == user.id)
        .group_by(RecommendationEvent.detected_emotion)
        .order_by(func.count(RecommendationEvent.id).desc())
        .limit(3)
        .all()
    )
    return [row[0] for row in rows]


def get_recommendations_for_user(db: Session, user: User, emotion: str, limit_per_type: int = 3) -> list[Recommendation]:
    preferred_languages = parse_languages(user.preferences.preferred_languages if user.preferences else None)
    target_tags = MOOD_TARGETS.get(emotion, MOOD_TARGETS["neutral"])
    served_ids = {
        row[0]
        for row in db.query(RecommendationEvent.recommendation_id)
        .filter(RecommendationEvent.user_id == user.id)
        .order_by(RecommendationEvent.created_at.desc())
        .limit(30)
        .all()
    }
    liked_ids = {
        row[0]
        for row in db.query(RecommendationEvent.recommendation_id)
        .filter(RecommendationEvent.user_id == user.id, RecommendationEvent.feedback == "like")
        .all()
    }

    items = db.query(Recommendation).all()

    def score(item: Recommendation) -> int:
        item_tags = set(_tags(item.mood_tags))
        value = len(item_tags.intersection(target_tags)) * 10
        if item.language in preferred_languages:
            value += 8 - preferred_languages.index(item.language)
        if item.id in served_ids:
            value -= 6
        if item.id in liked_ids:
            value += 4
        if emotion in NEGATIVE_MOODS and item_tags.intersection({"sad", "melancholy", "heartbreak"}):
            value -= 20
        return value

    filtered = [item for item in items if set(_tags(item.mood_tags)).intersection(target_tags)]
    ranked = sorted(filtered or items, key=score, reverse=True)
    chosen: list[Recommendation] = []
    counts = Counter()
    for item in ranked:
        if counts[item.type] >= limit_per_type:
            continue
        chosen.append(item)
        counts[item.type] += 1
        if counts["song"] >= limit_per_type and counts["movie"] >= limit_per_type:
            break
    return chosen


def record_recommendation_events(db: Session, user: User, items: list[Recommendation], emotion: str) -> None:
    for item in items:
        db.add(RecommendationEvent(user_id=user.id, recommendation_id=item.id, detected_emotion=emotion))
    db.commit()

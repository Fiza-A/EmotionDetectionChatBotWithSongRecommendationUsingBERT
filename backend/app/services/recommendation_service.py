from dataclasses import dataclass
import random

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
        "image_url": item.image_url,
        "preview_url": item.preview_url,
        "album_art": item.album_art,
        "external_url": item.external_url,
        "source": item.source,
        "source_id": item.source_id,
        "popularity_score": item.popularity_score or 0.0,
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


@dataclass
class RecommendationResult:
    songs: list[Recommendation]
    movies: list[Recommendation]
    message: str | None = None

    @property
    def items(self) -> list[Recommendation]:
        return [*self.songs, *self.movies]

    def to_payload(self) -> dict:
        return {
            "songs": [recommendation_to_read(item) for item in self.songs],
            "movies": [recommendation_to_read(item) for item in self.movies],
            "message": self.message,
        }


def _has_target_tag(item: Recommendation, target_tags: list[str]) -> bool:
    return bool(set(tag.lower() for tag in _tags(item.mood_tags)).intersection(tag.lower() for tag in target_tags))


def get_recommendations_for_user(db: Session, user: User, emotion: str, limit_per_type: int = 3) -> RecommendationResult:
    preferred_languages = parse_languages(user.preferences.preferred_languages if user.preferences else None)
    if not preferred_languages:
        return RecommendationResult(
            songs=[],
            movies=[],
            message="Please select at least one preferred language to get song and movie recommendations.",
        )

    preferred_lower = {language.lower() for language in preferred_languages}
    target_tags = MOOD_TARGETS.get(emotion, MOOD_TARGETS["neutral"])
    recent_ids = [
        row[0]
        for row in db.query(RecommendationEvent.recommendation_id)
        .filter(RecommendationEvent.user_id == user.id)
        .order_by(RecommendationEvent.created_at.desc())
        .limit(10)
        .all()
    ]
    recent_id_set = set(recent_ids)
    liked_ids = {
        row[0]
        for row in db.query(RecommendationEvent.recommendation_id)
        .filter(RecommendationEvent.user_id == user.id, RecommendationEvent.feedback == "like")
        .all()
    }
    disliked_ids = {
        row[0]
        for row in db.query(RecommendationEvent.recommendation_id)
        .filter(RecommendationEvent.user_id == user.id, RecommendationEvent.feedback == "dislike")
        .all()
    }

    items = (
        db.query(Recommendation)
        .filter(func.lower(Recommendation.language).in_(list(preferred_lower)))
        .all()
    )

    def score(item: Recommendation) -> float:
        item_tags = set(_tags(item.mood_tags))
        target_lower = {tag.lower() for tag in target_tags}
        value = len({tag.lower() for tag in item_tags}.intersection(target_lower)) * 10
        if item.language in preferred_languages:
            value += 8 - preferred_languages.index(item.language)
        if item.id in liked_ids:
            value += 8
        if item.id in disliked_ids:
            value -= 25
        value += min(float(item.popularity_score or 0), 100.0) / 20.0
        value += random.random() * 7
        if emotion in NEGATIVE_MOODS and item_tags.intersection({"sad", "melancholy", "heartbreak"}):
            value -= 20
        return value

    strict_matches = [item for item in items if _has_target_tag(item, target_tags)]

    # Allowed fallback: broaden within selected languages only, while still avoiding sad tags for negative moods.
    if not strict_matches and emotion in NEGATIVE_MOODS:
        broad_tags = ["uplifting", "comforting", "hopeful", "comedy", "calm", "feel-good"]
        strict_matches = [item for item in items if _has_target_tag(item, broad_tags)]

    def valid_for_negative(item: Recommendation) -> bool:
        return not (
            emotion in NEGATIVE_MOODS
            and set(tag.lower() for tag in _tags(item.mood_tags)).intersection({"sad", "melancholic", "heartbreak", "grief", "tragedy", "dark", "horror", "depressing"})
        )

    def choose(kind: str) -> list[Recommendation]:
        candidates = [item for item in strict_matches if item.type == kind and valid_for_negative(item) and item.id not in disliked_ids]
        fresh = [item for item in candidates if item.id not in recent_id_set]
        pool = fresh if len(fresh) >= limit_per_type else candidates
        return sorted(pool, key=score, reverse=True)[:limit_per_type]

    songs = choose("song")
    movies = choose("movie")

    message = None
    if not songs and not movies:
        message = "No recommendations found for your selected languages. Please add more languages in preferences or try another mood."
    elif len(songs) < limit_per_type or len(movies) < limit_per_type:
        message = "Showing fewer recommendations because your selected languages have limited matches for this mood."

    return RecommendationResult(songs=songs, movies=movies, message=message)


def record_recommendation_events(db: Session, user: User, items: list[Recommendation], emotion: str, conversation_id: int | None = None) -> None:
    for item in items:
        db.add(
            RecommendationEvent(
                user_id=user.id,
                conversation_id=conversation_id,
                recommendation_id=item.id,
                detected_emotion=emotion,
            )
        )
    db.commit()

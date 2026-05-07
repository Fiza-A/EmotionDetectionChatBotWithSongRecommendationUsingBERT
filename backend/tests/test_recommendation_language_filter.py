from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.models import Recommendation, RecommendationEvent, User, UserPreference
from app.services.recommendation_service import get_recommendations_for_user


def make_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def add_user(db, languages: str):
    user = User(username=f"user_{languages or 'none'}", email=f"{languages or 'none'}@example.com", password_hash="x")
    db.add(user)
    db.flush()
    db.add(UserPreference(user_id=user.id, preferred_languages=languages))
    db.commit()
    db.refresh(user)
    return user


def add_recommendation(db, title, kind, language, tags):
    db.add(Recommendation(title=title, type=kind, language=language, mood_tags=tags, genre="Test"))


def seed_language_cases(db):
    for language in ["English", "Hindi", "Tamil", "Telugu", "Malayalam", "Gujarati"]:
        add_recommendation(db, f"{language} Happy Song", "song", language, "happy,upbeat")
        add_recommendation(db, f"{language} Happy Movie", "movie", language, "happy,feel-good")
        add_recommendation(db, f"{language} Uplift Song", "song", language, "uplifting,hopeful")
        add_recommendation(db, f"{language} Comedy Movie", "movie", language, "comedy,feel-good")
        add_recommendation(db, f"{language} Calm Song", "song", language, "calm,comforting")
    db.commit()


def languages(result):
    return {item.language for item in result.items}


def test_hindi_only_happy_returns_only_hindi():
    db = make_db()
    seed_language_cases(db)
    result = get_recommendations_for_user(db, add_user(db, "Hindi"), "happy")
    assert result.items
    assert languages(result) == {"Hindi"}


def test_tamil_telugu_sad_returns_only_selected_languages():
    db = make_db()
    seed_language_cases(db)
    result = get_recommendations_for_user(db, add_user(db, "Tamil,Telugu"), "sad")
    assert result.items
    assert languages(result).issubset({"Tamil", "Telugu"})


def test_malayalam_angry_returns_only_malayalam():
    db = make_db()
    seed_language_cases(db)
    result = get_recommendations_for_user(db, add_user(db, "Malayalam"), "angry")
    assert result.items
    assert languages(result) == {"Malayalam"}


def test_no_languages_returns_message_and_no_recommendations():
    db = make_db()
    seed_language_cases(db)
    result = get_recommendations_for_user(db, add_user(db, ""), "happy")
    assert result.items == []
    assert "select at least one" in result.message.lower()


def test_gujarati_limited_data_never_falls_back_to_other_languages():
    db = make_db()
    add_recommendation(db, "Gujarati Calm Song", "song", "Gujarati", "calm")
    add_recommendation(db, "English Calm Song", "song", "English", "calm")
    db.commit()
    result = get_recommendations_for_user(db, add_user(db, "Gujarati"), "calm")
    assert result.items
    assert languages(result) == {"Gujarati"}


def test_empty_catalog_returns_friendly_message():
    db = make_db()
    result = get_recommendations_for_user(db, add_user(db, "Hindi"), "happy")
    assert result.items == []
    assert "no recommendations found" in result.message.lower()


def test_recent_recommendations_are_avoided_when_alternatives_exist():
    db = make_db()
    user = add_user(db, "Hindi")
    for index in range(8):
        add_recommendation(db, f"Hindi Happy Song {index}", "song", "Hindi", "happy,upbeat")
    db.commit()
    first_three = db.query(Recommendation).filter(Recommendation.type == "song").limit(3).all()
    for item in first_three:
        db.add(RecommendationEvent(user_id=user.id, recommendation_id=item.id, detected_emotion="happy"))
    db.commit()

    result = get_recommendations_for_user(db, user, "happy", limit_per_type=3)
    returned_ids = {item.id for item in result.songs}

    assert returned_ids
    assert returned_ids.isdisjoint({item.id for item in first_three})

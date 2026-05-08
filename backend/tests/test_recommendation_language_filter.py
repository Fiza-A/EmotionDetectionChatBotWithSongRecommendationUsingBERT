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
    item = Recommendation(title=title, type=kind, language=language, mood_tags=tags, genre="Test")
    db.add(item)
    return item


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
    assert all(item.type == "song" for item in result.songs)
    assert all(item.type == "movie" for item in result.movies)


def test_tamil_telugu_sad_returns_only_selected_languages():
    db = make_db()
    seed_language_cases(db)
    result = get_recommendations_for_user(db, add_user(db, "Tamil,Telugu"), "sad")
    assert result.items
    assert languages(result).issubset({"Tamil", "Telugu"})
    assert result.songs
    assert result.movies
    blocked_tags = {"sad", "melancholic", "heartbreak", "grief", "depressing"}
    assert all(blocked_tags.isdisjoint(set(item.mood_tags.split(","))) for item in result.songs)


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


def test_returns_up_to_three_songs_and_three_movies_when_available():
    db = make_db()
    user = add_user(db, "Hindi")
    for index in range(5):
        add_recommendation(db, f"Hindi Happy Song {index}", "song", "Hindi", "happy,upbeat")
        add_recommendation(db, f"Hindi Happy Movie {index}", "movie", "Hindi", "happy,feel-good")
    db.commit()

    result = get_recommendations_for_user(db, user, "happy", limit_per_type=3)

    assert len(result.songs) == 3
    assert len(result.movies) == 3
    assert {item.language for item in result.songs + result.movies} == {"Hindi"}


def test_per_type_broadening_keeps_songs_when_movie_pool_matches_first():
    db = make_db()
    user = add_user(db, "Malayalam")
    for index in range(4):
        add_recommendation(db, f"Malayalam Exact Calm Movie {index}", "movie", "Malayalam", "calm")
        add_recommendation(db, f"Malayalam Hopeful Song {index}", "song", "Malayalam", "hopeful,comforting")
    db.commit()

    result = get_recommendations_for_user(db, user, "angry", limit_per_type=3)

    assert len(result.songs) == 3
    assert len(result.movies) == 3
    assert {item.language for item in result.items} == {"Malayalam"}


def test_itunes_runtime_enrichment_adds_30_second_preview_to_songs(monkeypatch):
    db = make_db()
    user = add_user(db, "Hindi")
    song = add_recommendation(db, "Hindi Preview Song", "song", "Hindi", "happy,upbeat")
    add_recommendation(db, "Hindi Happy Movie", "movie", "Hindi", "happy,feel-good")
    db.commit()

    def fake_itunes_fields(title, artist):
        assert title == "Hindi Preview Song"
        return {
            "preview_url": "https://audio-ssl.itunes.apple.com/example-preview.m4a",
            "album_art": "https://is1-ssl.mzstatic.com/example-art.jpg",
            "external_url": "https://music.apple.com/example-song",
        }

    monkeypatch.setattr("app.services.recommendation_service.itunes_fields_for", fake_itunes_fields)

    result = get_recommendations_for_user(db, user, "happy", limit_per_type=3, enrich_itunes=True)

    assert len(result.songs) == 1
    assert result.songs[0].preview_url.endswith(".m4a")
    assert result.songs[0].album_art
    assert result.songs[0].external_url
    db.refresh(song)
    assert song.preview_url == result.songs[0].preview_url

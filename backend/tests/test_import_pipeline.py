from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.models import Recommendation
from app.seed.import_utils import import_records


def make_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def test_csv_import_adds_records_and_skips_duplicate_creates():
    db = make_db()
    rows = [
        {
            "title": "Test Song",
            "type": "song",
            "language": "hi",
            "genre": "pop",
            "mood_tags": "happy,upbeat",
            "artist": "Tester",
            "source": "unit",
            "source_id": "song-1",
        }
    ]

    first = import_records(db, rows)
    second = import_records(db, rows)

    assert first["created"] == 1
    assert second["updated"] == 1
    assert db.query(Recommendation).count() == 1
    item = db.query(Recommendation).first()
    assert item.language == "Hindi"
    assert item.source == "unit"


def test_csv_import_ignores_unknown_language():
    db = make_db()
    result = import_records(db, [{"title": "Unknown", "type": "movie", "language": "xx"}])
    assert result["skipped"] == 1
    assert db.query(Recommendation).count() == 0

from sqlalchemy import create_engine
from sqlalchemy import inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_settings


settings = get_settings()
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_db_and_tables():
    from app.models import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    ensure_sqlite_columns()


def ensure_sqlite_columns():
    if not settings.database_url.startswith("sqlite"):
        return
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    table_additions = {
        "recommendations": {
            "preview_url": "TEXT",
            "album_art": "TEXT",
            "external_url": "TEXT",
            "image_url": "TEXT",
            "source": "VARCHAR(80)",
            "source_id": "VARCHAR(120)",
            "popularity_score": "FLOAT DEFAULT 0.0",
            "created_at": "DATETIME",
            "updated_at": "DATETIME",
        },
        "chat_messages": {
            "conversation_id": "INTEGER",
            "recommendations_json": "TEXT",
        },
        "recommendation_events": {
            "conversation_id": "INTEGER",
        },
        "mood_history": {
            "conversation_id": "INTEGER",
        },
    }
    with engine.begin() as connection:
        for table, additions in table_additions.items():
            if table not in tables:
                continue
            existing = {column["name"] for column in inspector.get_columns(table)}
            for column, column_type in additions.items():
                if column not in existing:
                    connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}"))

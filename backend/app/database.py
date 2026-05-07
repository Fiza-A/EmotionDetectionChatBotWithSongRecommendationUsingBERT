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
    ensure_sqlite_recommendation_columns()


def ensure_sqlite_recommendation_columns():
    if not settings.database_url.startswith("sqlite"):
        return
    inspector = inspect(engine)
    if "recommendations" not in inspector.get_table_names():
        return
    existing = {column["name"] for column in inspector.get_columns("recommendations")}
    additions = {
        "preview_url": "TEXT",
        "album_art": "TEXT",
        "external_url": "TEXT",
    }
    with engine.begin() as connection:
        for column, column_type in additions.items():
            if column not in existing:
                connection.execute(text(f"ALTER TABLE recommendations ADD COLUMN {column} {column_type}"))

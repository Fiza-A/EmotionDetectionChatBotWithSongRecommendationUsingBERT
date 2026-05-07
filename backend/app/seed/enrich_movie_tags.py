from app.config import get_settings
from app.database import SessionLocal, create_db_and_tables
from app.models.models import Recommendation
from app.seed.mood_tags import generate_mood_tags, tags_to_text


def main():
    create_db_and_tables()
    settings = get_settings()
    if not settings.tmdb_api_key:
        print("TMDB_API_KEY is not configured; applying local genre/title tag enrichment only.")
    db = SessionLocal()
    try:
        updated = 0
        for item in db.query(Recommendation).filter(Recommendation.type == "movie").all():
            tags = generate_mood_tags("movie", genre=item.genre, raw_tags=item.mood_tags, title=item.title)
            tag_text = tags_to_text(tags)
            if tag_text and tag_text != item.mood_tags:
                item.mood_tags = tag_text
                updated += 1
        db.commit()
        print(f"Updated movie tags for {updated} movies.")
    finally:
        db.close()


if __name__ == "__main__":
    main()

from app.config import get_settings
from app.database import SessionLocal, create_db_and_tables
from app.models.models import Recommendation
from app.seed.mood_tags import generate_mood_tags, tags_to_text


def main():
    create_db_and_tables()
    settings = get_settings()
    if not settings.lastfm_api_key and not settings.spotify_client_id:
        print("LASTFM_API_KEY/SPOTIFY credentials are not configured; applying local genre/title tag enrichment only.")
    db = SessionLocal()
    try:
        updated = 0
        for item in db.query(Recommendation).filter(Recommendation.type == "song").all():
            tags = generate_mood_tags("song", genre=item.genre, raw_tags=item.mood_tags, title=item.title)
            tag_text = tags_to_text(tags)
            if tag_text and tag_text != item.mood_tags:
                item.mood_tags = tag_text
                updated += 1
        db.commit()
        print(f"Updated music tags for {updated} songs.")
    finally:
        db.close()


if __name__ == "__main__":
    main()

import argparse

from app.database import SessionLocal, create_db_and_tables
from app.models.models import Recommendation
from app.seed.catalog import LANGUAGES, SEED_ITEMS
from app.seed.expanded_catalog import EXPANDED_SEED_ITEMS
from app.services.itunes_service import itunes_fields_for


def search_link(title: str) -> str:
    return "https://www.google.com/search?q=" + title.replace(" ", "+")


def seed(enrich_itunes: bool = False):
    create_db_and_tables()
    db = SessionLocal()
    try:
        seed_items = [
            (*item, None, "built-in-curated", None, 75.0)
            for item in SEED_ITEMS
        ] + EXPANDED_SEED_ITEMS
        for title, kind, language, tags, genre, creator, year, image_url, source, source_id, popularity_score in seed_items:
            exists = db.query(Recommendation).filter_by(title=title, type=kind, language=language).first()
            itunes_fields = itunes_fields_for(title, creator) if enrich_itunes and kind == "song" else {}
            if exists:
                if enrich_itunes and kind == "song":
                    exists.preview_url = itunes_fields.get("preview_url")
                    exists.album_art = itunes_fields.get("album_art")
                    exists.external_url = itunes_fields.get("external_url")
                    exists.link = itunes_fields.get("external_url") or exists.link
                exists.source = exists.source or source
                exists.source_id = exists.source_id or source_id
                exists.popularity_score = exists.popularity_score or popularity_score
                continue
            db.add(
                Recommendation(
                    title=title,
                    type=kind,
                    language=language,
                    mood_tags=tags,
                    genre=genre,
                    creator=creator,
                    year=year,
                    link=itunes_fields.get("external_url") or search_link(f"{title} {kind}"),
                    image_url=image_url,
                    preview_url=itunes_fields.get("preview_url"),
                    album_art=itunes_fields.get("album_art"),
                    external_url=itunes_fields.get("external_url"),
                    source=source,
                    source_id=source_id,
                    popularity_score=popularity_score,
                )
            )
        db.commit()
        print(f"Seeded recommendations for {', '.join(LANGUAGES)}.")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--itunes", action="store_true", help="Enrich seeded songs with iTunes preview/art/link metadata.")
    args = parser.parse_args()
    seed(enrich_itunes=args.itunes)

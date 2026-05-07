import csv
from datetime import datetime
from pathlib import Path
from typing import Iterable

from sqlalchemy.orm import Session

from app.models.models import Recommendation
from app.services.languages import normalize_languages
from app.seed.mood_tags import generate_mood_tags, tags_to_text


DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def search_link(title: str, kind: str) -> str:
    return "https://www.google.com/search?q=" + f"{title} {kind}".replace(" ", "+")


def read_table(path: Path) -> list[dict]:
    if not path.exists():
        print(f"Missing file: {path}")
        return []
    delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=delimiter))


def pick(row: dict, *names: str) -> str | None:
    lowered = {key.lower().strip(): value for key, value in row.items()}
    for name in names:
        value = lowered.get(name.lower())
        if value not in (None, "", "\\N"):
            return str(value).strip()
    return None


def parse_year(value: str | None) -> int | None:
    if not value:
        return None
    for token in str(value).replace("/", "-").split("-"):
        if token.isdigit() and len(token) == 4:
            return int(token)
    return None


def parse_float(value: str | None, default: float = 0.0) -> float:
    try:
        return float(value) if value not in (None, "", "\\N") else default
    except ValueError:
        return default


def normalize_record(row: dict, forced_type: str | None = None) -> dict | None:
    kind = (forced_type or pick(row, "type", "kind", "media_type") or "").lower()
    if kind in {"track", "music"}:
        kind = "song"
    if kind not in {"song", "movie"}:
        return None
    title = pick(row, "title", "track_name", "trackName", "movie_title", "primaryTitle", "originalTitle", "name")
    if not title:
        return None
    language = normalize_languages([pick(row, "language", "original_language", "lang") or ""])
    if not language:
        return None
    genre = pick(row, "genre", "genres", "primaryGenreName")
    raw_tags = pick(row, "mood_tags", "tags", "lastfm_tags", "keywords")
    overview = pick(row, "overview", "description", "plot")
    mood_tags = tags_to_text(raw_tags) or tags_to_text(generate_mood_tags(kind, genre=genre, raw_tags=raw_tags, title=title, overview=overview))
    return {
        "title": title,
        "type": kind,
        "language": language[0],
        "mood_tags": mood_tags,
        "genre": genre,
        "creator": pick(row, "creator", "artist", "artistName", "director", "directors"),
        "year": parse_year(pick(row, "year", "release_year", "releaseDate", "startYear")),
        "link": pick(row, "link", "url", "external_url", "trackViewUrl") or search_link(title, kind),
        "image_url": pick(row, "image_url", "poster_url", "poster_path", "artworkUrl100"),
        "preview_url": pick(row, "preview_url", "previewUrl"),
        "album_art": pick(row, "album_art", "artworkUrl100"),
        "external_url": pick(row, "external_url", "trackViewUrl", "tmdb_url", "imdb_url"),
        "source": pick(row, "source") or "csv",
        "source_id": pick(row, "source_id", "id", "trackId", "tconst", "tmdb_id"),
        "popularity_score": parse_float(pick(row, "popularity_score", "popularity", "averageRating"), 0.0),
    }


def upsert_recommendation(db: Session, record: dict) -> tuple[Recommendation, bool]:
    existing = (
        db.query(Recommendation)
        .filter(
            Recommendation.title == record["title"],
            Recommendation.type == record["type"],
            Recommendation.language == record["language"],
        )
        .first()
    )
    created = existing is None
    item = existing or Recommendation(title=record["title"], type=record["type"], language=record["language"], mood_tags=record["mood_tags"])
    for key, value in record.items():
        if hasattr(item, key) and value not in (None, ""):
            setattr(item, key, value)
    item.updated_at = datetime.utcnow()
    db.add(item)
    return item, created


def import_records(db: Session, rows: Iterable[dict], forced_type: str | None = None) -> dict:
    created = updated = skipped = 0
    for row in rows:
        record = normalize_record(row, forced_type=forced_type)
        if not record:
            skipped += 1
            continue
        _, was_created = upsert_recommendation(db, record)
        created += int(was_created)
        updated += int(not was_created)
    db.commit()
    return {"created": created, "updated": updated, "skipped": skipped}

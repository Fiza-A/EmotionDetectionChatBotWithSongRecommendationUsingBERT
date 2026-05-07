import argparse
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.config import get_settings
from app.database import SessionLocal, create_db_and_tables
from app.seed.import_utils import DATA_DIR, import_records, read_table
from app.services.languages import normalize_languages


def tmdb_rows(language: str, limit: int) -> list[dict]:
    settings = get_settings()
    if not settings.tmdb_api_key:
        print("TMDB_API_KEY is not configured; skipping TMDb import.")
        return []
    normalized = normalize_languages([language])
    if not normalized:
        print(f"Unsupported TMDb language: {language}")
        return []
    language_map = {
        "English": "en",
        "Hindi": "hi",
        "Tamil": "ta",
        "Telugu": "te",
        "Malayalam": "ml",
        "Kannada": "kn",
        "Bengali": "bn",
        "Marathi": "mr",
        "Punjabi": "pa",
        "Gujarati": "gu",
    }
    rows = []
    pages = max(1, min(25, (limit + 19) // 20))
    for page in range(1, pages + 1):
        params = urlencode(
            {
                "api_key": settings.tmdb_api_key,
                "with_original_language": language_map[normalized[0]],
                "sort_by": "popularity.desc",
                "page": page,
            }
        )
        request = Request(f"https://api.themoviedb.org/3/discover/movie?{params}", headers={"User-Agent": "EmotionDetectionChatbot/1.0"})
        with urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
        for item in payload.get("results", []):
            rows.append(
                {
                    "type": "movie",
                    "title": item.get("title") or item.get("original_title"),
                    "language": normalized[0],
                    "overview": item.get("overview"),
                    "year": item.get("release_date"),
                    "popularity_score": item.get("popularity"),
                    "source": "tmdb",
                    "source_id": item.get("id"),
                    "image_url": f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}" if item.get("poster_path") else None,
                    "external_url": f"https://www.themoviedb.org/movie/{item.get('id')}" if item.get("id") else None,
                }
            )
            if len(rows) >= limit:
                return rows
    return rows


def imdb_rows() -> list[dict]:
    basics_path = DATA_DIR / "imdb_title_basics.tsv"
    ratings_path = DATA_DIR / "imdb_title_ratings.tsv"
    basics = read_table(basics_path)
    ratings = {row.get("tconst"): row for row in read_table(ratings_path)}
    rows = []
    for row in basics:
        if row.get("titleType") != "movie":
            continue
        rating = ratings.get(row.get("tconst"), {})
        rows.append(
            {
                "type": "movie",
                "title": row.get("primaryTitle"),
                "language": row.get("language") or "",
                "genre": row.get("genres"),
                "year": row.get("startYear"),
                "source": "imdb",
                "source_id": row.get("tconst"),
                "popularity_score": rating.get("averageRating"),
            }
        )
    return rows


def main():
    parser = argparse.ArgumentParser(description="Import movie recommendations from CSV, IMDb files, or TMDb.")
    parser.add_argument("--source", choices=["csv", "imdb", "tmdb"], default="csv")
    parser.add_argument("--file", default=str(DATA_DIR / "movies.csv"))
    parser.add_argument("--language", default="Hindi")
    parser.add_argument("--limit", type=int, default=500)
    args = parser.parse_args()

    create_db_and_tables()
    rows = read_table(Path(args.file)) if args.source == "csv" else imdb_rows() if args.source == "imdb" else tmdb_rows(args.language, args.limit)
    db = SessionLocal()
    try:
        print(import_records(db, rows, forced_type="movie"))
    finally:
        db.close()


if __name__ == "__main__":
    main()

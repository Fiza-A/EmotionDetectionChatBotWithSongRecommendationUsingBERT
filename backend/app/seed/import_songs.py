import argparse
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.database import SessionLocal, create_db_and_tables
from app.seed.import_utils import DATA_DIR, import_records, read_table
from app.services.languages import normalize_languages


def musicbrainz_rows(language: str, limit: int) -> list[dict]:
    normalized = normalize_languages([language])
    if not normalized:
        print(f"Unsupported MusicBrainz language: {language}")
        return []
    query = f'tag:"{normalized[0].lower()}" OR artist:"{normalized[0]}"'
    params = urlencode({"query": query, "fmt": "json", "limit": min(limit, 100)})
    request = Request(f"https://musicbrainz.org/ws/2/recording?{params}", headers={"User-Agent": "EmotionDetectionChatbot/1.0 (local import)"})
    with urlopen(request, timeout=20) as response:
        payload = json.loads(response.read().decode("utf-8"))
    rows = []
    for item in payload.get("recordings", [])[:limit]:
        artist_credit = item.get("artist-credit") or []
        artist = artist_credit[0].get("name") if artist_credit and isinstance(artist_credit[0], dict) else None
        tags = ",".join(tag.get("name", "") for tag in item.get("tags", []))
        rows.append(
            {
                "type": "song",
                "title": item.get("title"),
                "language": normalized[0],
                "artist": artist,
                "tags": tags,
                "source": "musicbrainz",
                "source_id": item.get("id"),
                "external_url": f"https://musicbrainz.org/recording/{item.get('id')}" if item.get("id") else None,
            }
        )
    return rows


def main():
    parser = argparse.ArgumentParser(description="Import song recommendations from CSV or MusicBrainz.")
    parser.add_argument("--source", choices=["csv", "musicbrainz"], default="csv")
    parser.add_argument("--file", default=str(DATA_DIR / "songs.csv"))
    parser.add_argument("--language", default="Hindi")
    parser.add_argument("--limit", type=int, default=500)
    args = parser.parse_args()

    create_db_and_tables()
    rows = read_table(Path(args.file)) if args.source == "csv" else musicbrainz_rows(args.language, args.limit)
    db = SessionLocal()
    try:
        print(import_records(db, rows, forced_type="song"))
    finally:
        db.close()


if __name__ == "__main__":
    main()

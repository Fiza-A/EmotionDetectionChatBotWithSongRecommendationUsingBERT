import argparse
import json
from pathlib import Path
import sys


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.seed.catalog import SEED_ITEMS
from app.services.itunes_service import search_music


def seeded_songs():
    for title, kind, language, tags, genre, creator, year in SEED_ITEMS:
        if kind == "song":
            yield {
                "title": title,
                "artist": creator,
                "language": language,
                "year": year,
            }


def main():
    parser = argparse.ArgumentParser(description="Check iTunes preview availability for the seeded song catalog.")
    parser.add_argument("--one-title", default="Happy", help="Single song title for a quick iTunes smoke test.")
    parser.add_argument("--one-artist", default="Pharrell Williams", help="Single song artist for a quick iTunes smoke test.")
    parser.add_argument("--country", default="US")
    parser.add_argument("--output", default="itunes_song_check.json")
    args = parser.parse_args()

    one = search_music(args.one_title, args.one_artist, country=args.country)
    all_results = []
    for song in seeded_songs():
        track = search_music(song["title"], song["artist"], country=args.country)
        all_results.append(
            {
                **song,
                "found": bool(track),
                "itunes_title": track.title if track else None,
                "itunes_artist": track.artist if track else None,
                "preview_url": track.preview_url if track else None,
                "album_art": track.album_art if track else None,
                "external_url": track.external_url if track else None,
                "match_score": round(track.score, 3) if track else 0,
            }
        )

    found = [item for item in all_results if item["found"] and item["preview_url"]]
    missing = [item for item in all_results if not item["found"] or not item["preview_url"]]
    report = {
        "single_song_test": {
            "query": f"{args.one_title} {args.one_artist}",
            "found": bool(one),
            "itunes_title": one.title if one else None,
            "itunes_artist": one.artist if one else None,
            "preview_url": one.preview_url if one else None,
            "album_art": one.album_art if one else None,
            "external_url": one.external_url if one else None,
        },
        "summary": {
            "total_seeded_songs": len(all_results),
            "found_with_preview": len(found),
            "missing_or_without_preview": len(missing),
        },
        "songs": all_results,
    }
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report["single_song_test"], indent=2))
    print(json.dumps(report["summary"], indent=2))
    if missing:
        print("Missing or no-preview songs:")
        for item in missing:
            print(f"- {item['title']} ({item['artist']})")


if __name__ == "__main__":
    main()

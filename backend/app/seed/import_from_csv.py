import argparse
from pathlib import Path

from app.database import SessionLocal, create_db_and_tables
from app.seed.import_utils import DATA_DIR, import_records, read_table


def main():
    parser = argparse.ArgumentParser(description="Import recommendation records from CSV/TSV.")
    parser.add_argument("--file", default=None, help="CSV/TSV file. Defaults to backend/data/movies.csv and songs.csv.")
    parser.add_argument("--type", choices=["song", "movie"], default=None)
    args = parser.parse_args()

    create_db_and_tables()
    db = SessionLocal()
    try:
        files = [Path(args.file)] if args.file else [DATA_DIR / "movies.csv", DATA_DIR / "songs.csv"]
        total = {"created": 0, "updated": 0, "skipped": 0}
        for file_path in files:
            rows = read_table(file_path)
            if not rows:
                continue
            kind = args.type
            if kind is None and "song" in file_path.stem.lower():
                kind = "song"
            if kind is None and "movie" in file_path.stem.lower():
                kind = "movie"
            result = import_records(db, rows, forced_type=kind)
            print(f"{file_path}: {result}")
            for key in total:
                total[key] += result[key]
        print(f"Total: {total}")
    finally:
        db.close()


if __name__ == "__main__":
    main()

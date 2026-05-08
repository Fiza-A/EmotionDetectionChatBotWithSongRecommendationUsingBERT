from collections import Counter

from app.seed.catalog import LANGUAGES
from app.seed.expanded_catalog import EXPANDED_SEED_ITEMS


def test_expanded_catalog_has_at_least_50_songs_per_supported_language():
    counts = Counter()
    for item in EXPANDED_SEED_ITEMS:
        title, kind, language, tags, genre, creator, year, image_url, source, source_id, popularity_score = item
        if kind == "song":
            counts[language] += 1
            assert title
            assert kind == "song"
            assert language in LANGUAGES
            assert tags
            assert genre
            assert creator
            assert year
            assert source

    assert all(counts[language] >= 50 for language in LANGUAGES)
